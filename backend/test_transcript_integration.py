#!/usr/bin/env python3
"""
Test script to verify TranscriptManager integration in ResponsiveDeliberationEngine
"""
import asyncio
from app.models.deliberation import DeliberationCase
from app.services.juror_generator import JurorGenerator
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine
from pathlib import Path
import json

async def test_transcript_integration():
    """Test that transcript manager creates the correct files"""
    
    # Create a simple test case
    case = DeliberationCase(
        case_type="theft",
        case_title="Test Case: State v. Smith",
        summary="Test case for transcript integration",
        key_evidence=[
            "Security footage shows defendant",
            "Witness testimony",
            "Receipt evidence"
        ],
        prosecution_argument="Evidence proves guilt",
        defense_argument="Reasonable doubt exists",
        jury_instructions="You must find guilt beyond reasonable doubt",
        requires_unanimous=True
    )
    
    # Generate jurors
    generator = JurorGenerator()
    jurors = generator.generate_jury_pool("San Francisco", "CA", 6)
    
    print(f"Generated {len(jurors)} jurors")
    
    # Create engine with county and state
    engine = ResponsiveDeliberationEngine(
        case=case,
        jurors=jurors,
        county="San Francisco",
        state="CA"
    )
    
    print(f"Session ID: {engine.session.session_id}")
    print(f"Transcript path: {engine.transcript_manager.get_transcript_path()}")
    
    # Run a short deliberation
    try:
        session = await engine.run_full_deliberation(max_rounds=1)
        print(f"Deliberation completed. Final verdict: {session.final_verdict}")
        
        # Check if transcript file exists
        transcript_path = Path(engine.transcript_manager.get_transcript_path())
        if transcript_path.exists():
            print(f"\n✓ Transcript file created: {transcript_path.name}")
            
            # Check file size
            size = transcript_path.stat().st_size
            print(f"✓ Transcript size: {size} bytes")
            
            # Check JSON summary
            json_path = transcript_path.with_suffix('.json')
            if json_path.exists():
                print(f"✓ JSON summary created: {json_path.name}")
                with open(json_path, 'r') as f:
                    summary = json.load(f)
                print(f"  - Case: {summary['case_title']}")
                print(f"  - Location: {summary['location']}")
                print(f"  - Duration: {summary['duration_minutes']:.1f} minutes")
                print(f"  - Voting rounds: {summary['voting_rounds']}")
            else:
                print("✗ JSON summary not found")
                
            # Show first few lines of transcript
            print("\nFirst few lines of transcript:")
            print("-" * 60)
            with open(transcript_path, 'r') as f:
                lines = f.readlines()[:20]
                for line in lines:
                    print(line.rstrip())
            print("-" * 60)
            
        else:
            print(f"✗ Transcript file not found at {transcript_path}")
            
    except Exception as e:
        print(f"Error during deliberation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_transcript_integration())