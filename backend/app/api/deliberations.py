from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional
import asyncio
import json
from datetime import datetime
from app.models.deliberation import DeliberationCase, VerdictChoice, JurorStatement, Vote
from app.services.deliberation_engine_v2 import ImprovedDeliberationEngine
from app.services.deliberation_engine import DeliberationEngine
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine
from app.services.streaming_deliberation_engine import StreamingDeliberationEngine
from app.services.juror_generator import JurorGenerator
from pydantic import BaseModel
import logging

router = APIRouter(tags=["deliberations"])
logger = logging.getLogger(__name__)

# Store active sessions in memory (in production, use Redis or database)
active_sessions: Dict[str, ResponsiveDeliberationEngine] = {}
session_transcripts: Dict[str, List[Dict]] = {}
session_queues: Dict[str, asyncio.Queue] = {}

class StartDeliberationRequest(BaseModel):
    county: str
    state: str
    case: DeliberationCase


@router.post("/sessions/create")
async def create_deliberation_session(
    case: DeliberationCase,
    juror_count: int = 6,
    county: str = "Los Angeles",
    state: str = "CA"
):
    """Create a new deliberation session"""
    try:
        # Generate jurors
        generator = JurorGenerator()
        jurors = generator.generate_jury_pool(
            county=county,
            state=state,
            pool_size=juror_count,
            case_type=case.case_type
        )
        
        # Create responsive engine for better interactions
        engine = ResponsiveDeliberationEngine(
            case=case,
            jurors=jurors,
            county=county,
            state=state
        )
        session_id = engine.session.session_id
        
        # Store session
        active_sessions[session_id] = engine
        session_transcripts[session_id] = []
        
        return {
            "session_id": session_id,
            "case_title": case.case_title,
            "juror_count": len(jurors),
            "status": "created"
        }
        
    except Exception as e:
        logger.error(f"Error creating deliberation session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/transcript")
async def get_session_transcript(session_id: str):
    """Get the full transcript of a deliberation session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = active_sessions[session_id]
    
    # Collect transcripts from all jurors
    all_transcripts = []
    for juror_id, agent in engine.agents.items():
        juror_transcript = agent.get_full_transcript()
        all_transcripts.extend(juror_transcript)
    
    # Sort by timestamp
    all_transcripts.sort(key=lambda x: x.get('timestamp', ''))
    
    # Get session summary
    summary = {
        "session_id": session_id,
        "case_title": engine.case.case_title,
        "current_phase": engine.session.current_phase.value,
        "final_verdict": engine.session.final_verdict if isinstance(engine.session.final_verdict, str) else engine.session.final_verdict.value if engine.session.final_verdict else None,
        "total_interactions": len(all_transcripts),
        "juror_summaries": {},
        "transcript_files": {}
    }
    
    # Add individual juror summaries and file paths
    for juror_id, agent in engine.agents.items():
        summary["juror_summaries"][agent.persona.name] = agent.get_transcript_summary()
        if hasattr(agent, 'get_transcript_file_path'):
            summary["transcript_files"][agent.persona.name] = agent.get_transcript_file_path()
    
    # Add session directory path
    if engine.agents:
        first_agent = next(iter(engine.agents.values()))
        if hasattr(first_agent, 'get_session_directory'):
            summary["session_directory"] = first_agent.get_session_directory()
    
    return {
        "summary": summary,
        "transcript": all_transcripts
    }


@router.get("/sessions/{session_id}/transcript/export")
async def export_session_transcript(session_id: str, format: str = "json"):
    """Export session transcript in various formats"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = active_sessions[session_id]
    
    # Collect all juror transcripts
    combined_export = {
        "session_id": session_id,
        "export_time": datetime.utcnow().isoformat(),
        "case": {
            "title": engine.case.case_title,
            "type": engine.case.case_type,
            "summary": engine.case.summary
        },
        "jurors": {}
    }
    
    for juror_id, agent in engine.agents.items():
        combined_export["jurors"][agent.persona.name] = {
            "persona": agent.persona.dict(),
            "transcript": agent.get_full_transcript(),
            "summary": agent.get_transcript_summary()
        }
    
    if format == "json":
        return combined_export
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'json'")


@router.websocket("/sessions/{session_id}/ws")
async def deliberation_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time deliberation updates"""
    if session_id not in active_sessions:
        await websocket.close(code=4004, reason="Session not found")
        return
        
    await websocket.accept()
    engine = active_sessions[session_id]
    
    try:
        # Set up callbacks to send updates
        async def on_statement(statement):
            await websocket.send_json({
                "type": "statement",
                "data": statement.dict()
            })
        
        async def on_vote(votes):
            await websocket.send_json({
                "type": "vote",
                "data": [v.dict() for v in votes]
            })
        
        # Update engine callbacks
        engine.on_statement = on_statement
        engine.on_vote = on_vote
        
        # Run responsive deliberation
        await engine.run_full_deliberation()
        
        # Send final transcript
        await websocket.send_json({
            "type": "complete",
            "final_verdict": engine.session.final_verdict if isinstance(engine.session.final_verdict, str) else engine.session.final_verdict.value if engine.session.final_verdict else None
        })
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in deliberation websocket: {e}")
        await websocket.close(code=4000, reason=str(e))


@router.get("/sessions")
async def list_sessions():
    """List all active deliberation sessions"""
    sessions = []
    for session_id, engine in active_sessions.items():
        sessions.append({
            "session_id": session_id,
            "case_title": engine.case.case_title,
            "current_phase": engine.session.current_phase.value,
            "created_at": engine.session.created_at.isoformat()
        })
    return {"sessions": sessions, "count": len(sessions)}


@router.post("/deliberations/start")
async def start_deliberation(request: StartDeliberationRequest):
    """Start a new deliberation session with the given configuration"""
    try:
        # Check if this is the OJ Simpson case and load complete data
        case = request.case
        if case.case_title == "People of the State of California v. Orenthal James Simpson":
            # Try to load the complete OJ Simpson case data
            from app.cli.deliberation_interface import load_oj_simpson_complete
            complete_case = load_oj_simpson_complete()
            if complete_case:
                case = complete_case
                logger.info("Loaded complete OJ Simpson case data")
        
        # Generate jurors
        generator = JurorGenerator()
        jurors = generator.generate_jury_pool(
            county=request.county,
            state=request.state,
            pool_size=6,
            case_type=case.case_type
        )
        
        # Create event queue for SSE
        queue = asyncio.Queue()
        
        # Send initial status
        await queue.put({
            "type": "status",
            "data": {
                "message": f"Loading {request.case.case_title}...",
                "phase": "loading_case"
            }
        })
        
        # Send jury generation status
        await queue.put({
            "type": "status", 
            "data": {
                "message": f"Generating jury pool for {request.county}, {request.state}...",
                "phase": "generating_jury"
            }
        })
        
        # Create responsive engine with callbacks
        def on_statement(statement: JurorStatement):
            asyncio.create_task(queue.put({
                "type": "statement",
                "data": {
                    "juror_id": statement.juror_id,
                    "juror_name": statement.juror_name,
                    "content": statement.content,
                    "phase": statement.phase,
                    "timestamp": statement.timestamp.isoformat(),
                    "sentiment": statement.sentiment
                }
            }))
        
        def on_vote(votes: List[Vote]):
            # Send individual votes
            for vote in votes:
                asyncio.create_task(queue.put({
                    "type": "vote",
                    "data": {
                        "juror_id": vote.juror_id,
                        "juror_name": vote.juror_name,
                        "verdict": vote.verdict,
                        "confidence": vote.confidence,
                        "reasoning": vote.reasoning,
                        "round_number": vote.round_number
                    }
                }))
            
            # Calculate and send vote summary
            vote_counts = {"guilty": 0, "not_guilty": 0, "undecided": 0}
            for vote in votes:
                if vote.verdict == VerdictChoice.GUILTY:
                    vote_counts["guilty"] += 1
                elif vote.verdict == VerdictChoice.NOT_GUILTY:
                    vote_counts["not_guilty"] += 1
                else:
                    vote_counts["undecided"] += 1
                    
            asyncio.create_task(queue.put({
                "type": "vote_summary",
                "data": vote_counts
            }))
        
        def on_status(phase: str, message: str):
            asyncio.create_task(queue.put({
                "type": "status",
                "data": {
                    "phase": phase,
                    "message": message
                }
            }))
        
        def on_partial(juror_id: int, juror_name: str, partial_content: str):
            asyncio.create_task(queue.put({
                "type": "partial_statement",
                "data": {
                    "juror_id": juror_id,
                    "juror_name": juror_name,
                    "content": partial_content
                }
            }))
        
        # Create engine first to get persona names
        engine = StreamingDeliberationEngine(
            case,  # Use the potentially enhanced case
            jurors,
            county=request.county,
            state=request.state,
            on_statement=on_statement,
            on_vote=on_vote,
            on_status=on_status,
            on_partial=on_partial
        )
        
        # Send juror info with actual names from personas
        await queue.put({
            "type": "jurors",
            "data": [{"id": persona.juror_id, "name": persona.name} for persona in engine.juror_personas]
        })
        
        session_id = engine.session.session_id
        
        # Store session and queue
        active_sessions[session_id] = engine
        session_queues[session_id] = queue
        
        # Start deliberation in background
        async def run_deliberation():
            try:
                await engine.run_full_deliberation(max_rounds=10)
                await queue.put({
                    "type": "complete",
                    "data": {
                        "verdict": engine.session.final_verdict
                    }
                })
            except Exception as e:
                logger.error(f"Error in deliberation: {e}")
                await queue.put({
                    "type": "error",
                    "data": {"message": str(e)}
                })
        
        asyncio.create_task(run_deliberation())
        
        return {
            "session_id": session_id,
            "case_title": request.case.case_title,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Error starting deliberation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deliberations/{session_id}/stream")
async def stream_deliberation(session_id: str):
    """Server-sent events stream for deliberation updates"""
    if session_id not in session_queues:
        raise HTTPException(status_code=404, detail="Session not found")
    
    queue = session_queues[session_id]
    
    async def event_generator():
        try:
            while True:
                # Wait for events with timeout
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    
                    # Check if deliberation is complete
                    if event.get("type") == "complete":
                        break
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                    
        except Exception as e:
            logger.error(f"Error in event stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )