"""
Streaming Deliberation Engine with real-time updates
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable
import json
from datetime import datetime
from app.models.deliberation import (
    DeliberationSession, JurorPersona, JurorStatement, Vote,
    DeliberationPhase, DeliberationCase, VerdictChoice
)
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine
from app.services.ai_juror_agent import AIJurorAgent
from app.services.ai_juror_agent_streaming import StreamingAIJurorAgent
import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)


class StreamingDeliberationEngine(ResponsiveDeliberationEngine):
    """Enhanced deliberation engine with streaming support"""
    
    def __init__(
        self,
        case: DeliberationCase,
        jurors: List[Dict[str, Any]],
        county: str = "Unknown",
        state: str = "Unknown",
        on_statement: Optional[Callable[[JurorStatement], None]] = None,
        on_vote: Optional[Callable[[List[Vote]], None]] = None,
        on_status: Optional[Callable[[str, str], None]] = None,
        on_partial: Optional[Callable[[int, str, str], None]] = None
    ):
        super().__init__(case, jurors, county, state, on_statement, on_vote)
        self.on_status = on_status
        self.on_partial = on_partial
        
        # Replace agents with streaming versions
        print(f"\n{Fore.GREEN}🎭 INITIALIZING STREAMING DELIBERATION ENGINE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Case: {case.case_title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Jurors: {len(self.agents)}{Style.RESET_ALL}\n")
        
        for juror_id, agent in self.agents.items():
            streaming_agent = StreamingAIJurorAgent(agent.persona, agent.case, agent.session_id)
            self.agents[juror_id] = streaming_agent
        
    async def run_full_deliberation(self, max_rounds: int = 8) -> DeliberationSession:
        """Run complete deliberation with streaming updates"""
        
        # Send status update
        if self.on_status:
            self.on_status("selecting_foreperson", f"Selecting foreperson from {len(self.agents)} jurors...")
        
        # Announce foreperson selection
        await self._announce_foreperson()
        
        if self.on_status:
            self.on_status("foreperson_selected", f"{self.foreperson_name} has been selected as foreperson")
        
        # Phase 1: Opening statements
        if self.on_status:
            self.on_status("opening_statements", "Jurors are presenting their opening statements...")
        await self._run_opening_statements()
        
        # Phase 2: Evidence review
        if self.on_status:
            self.on_status("evidence_review", "Reviewing key evidence...")
        await self._run_evidence_review()
        
        # Phase 3: Discussion with responsive speaking
        for round_num in range(max_rounds):
            if self.on_status:
                self.on_status("discussion", f"Discussion round {round_num + 1} of {max_rounds}")
            
            await self._run_responsive_discussion(round_num)
            
            # Voting round
            if self.on_status:
                self.on_status("voting", f"Voting round {round_num + 1}")
            await self._run_voting_round(round_num + 1)
            
            # Check for verdict
            if self._check_verdict():
                break
            
            # Check if we're making progress
            if round_num >= 2 and self._is_deadlocked():
                if self.on_status:
                    self.on_status("deadlock_check", "Checking for deadlock...")
                await self._foreperson_statement(
                    "We seem to be at an impasse. Let me suggest we each identify the ONE piece of evidence that most influences our decision. Then let's discuss those specific points."
                )
            
            # Post-vote persuasion phase
            if self.on_status:
                self.on_status("persuasion", "Jurors are trying to persuade each other...")
            await self._run_post_vote_persuasion()
            
            # Foreperson summarizes if not final round
            if round_num < max_rounds - 1:
                await self._foreperson_summary()
        
        # Finalize
        if self.on_status:
            self.on_status("finalizing", "Finalizing deliberation...")
        self._finalize_deliberation()
        
        return self.session
    
    async def _have_juror_speak_streaming(self, juror_id: int):
        """Have a specific juror speak with streaming support"""
        agent = self.agents[juror_id]
        
        # Send status that this juror is thinking
        if self.on_partial:
            self.on_partial(juror_id, agent.persona.name, "[thinking...]")
        
        # Get recent context
        recent_context = self.recent_statements[-10:]
        
        # Get guidance to avoid repetition
        guidance = self.discussion_tracker.get_guidance_for_next_speaker(agent.persona.name)
        
        # Create conversational prompts based on context
        discussion_prompt = None
        
        # Check if this is a direct response to being mentioned
        if juror_id in self.waiting_to_respond:
            discussion_prompt = "Someone just addressed you directly. Give a quick, natural response in 1-2 sentences."
        elif len(self.recent_statements) > 0 and "?" in self.recent_statements[-1].content:
            discussion_prompt = "Answer the question that was just asked. Be direct and conversational, 1-2 sentences."
        elif guidance:
            discussion_prompt = f"{guidance} Keep it conversational and brief."
        else:
            discussion_prompt = "Jump into the conversation naturally. React, question, or add a quick point. 1-2 sentences max."
        
        # Generate statement with streaming
        statement = await self._generate_statement_streaming(
            agent, 
            self.session.current_phase,
            recent_context,
            discussion_prompt
        )
        
        self.session.statements.append(statement)
        self.recent_statements.append(statement)
        
        # Update discussion tracker
        self.discussion_tracker.update_from_statement(agent.persona.name, statement.content)
        
        # Detect mentions and add to response queue
        mentioned_ids = self._detect_mentions(statement.content)
        for mentioned_id in mentioned_ids:
            if mentioned_id != juror_id and mentioned_id not in self.has_spoken:
                if mentioned_id not in self.waiting_to_respond:
                    self.waiting_to_respond.append(mentioned_id)
                    if self.on_status:
                        self.on_status("mention", f"{self.agents[mentioned_id].persona.name} was mentioned")
        
        if self.on_statement:
            self.on_statement(statement)
    
    async def _generate_statement_streaming(
        self,
        agent: StreamingAIJurorAgent,
        phase: DeliberationPhase,
        recent_context: List[JurorStatement],
        prompt_addition: Optional[str] = None
    ) -> JurorStatement:
        """Generate statement with real DeepSeek streaming"""
        
        # Token callback to send partial updates
        partial_content = ""
        
        def on_token(token: str):
            nonlocal partial_content
            partial_content += token
            if self.on_partial:
                self.on_partial(agent.persona.juror_id, agent.persona.name, partial_content)
        
        # Use the streaming method
        statement = await agent.generate_statement_streaming(
            phase,
            recent_context,
            prompt_addition=prompt_addition,
            on_token=on_token
        )
        
        return statement
    
    async def _run_responsive_discussion(self, round_num: int):
        """Run discussion phase with streaming updates"""
        if self.on_status:
            self.on_status("discussion_start", f"Starting discussion round {round_num + 1}")
        
        # Override parent method to use streaming version
        self.session.current_phase = DeliberationPhase.DISCUSSION
        self.has_spoken.clear()
        self.waiting_to_respond.clear()
        
        # Foreperson opens discussion
        prompts = [
            "Let's have an open discussion. Who wants to address the points raised?",
            "We need to talk through the key issues. What's troubling you about this case?",
            "Let's dig into the evidence. What stands out to you?",
            "I'd like to hear different perspectives. What's your take on the evidence?"
        ]
        
        await self._foreperson_statement(prompts[round_num % len(prompts)])
        
        # Dynamic discussion
        max_speakers = min(12, 6 + round_num * 2)
        speakers_this_round = 0
        interruption_count = 0
        
        # Continue with responsive speaking
        while speakers_this_round < max_speakers and (self.waiting_to_respond or len(self.has_spoken) < len(self.agents)):
            await asyncio.sleep(0.2 if self.waiting_to_respond and random.random() < 0.7 else 0.5)
            
            # Foreperson occasionally moderates
            if interruption_count >= 4 and random.random() < 0.3:
                moderation_phrases = [
                    "Let's stay focused on the evidence presented in court.",
                    "Please, one at a time. Everyone deserves to be heard.",
                    "Remember, we must base our decision only on the evidence, not speculation.",
                    "Let's avoid repeating the same points. What new insights can we bring?",
                    "Keep in mind the prosecution must prove guilt beyond a reasonable doubt.",
                    "Remember to remain impartial and consider all viewpoints.",
                    "We need compelling reasons to change our views, not just repetition.",
                    "Try to understand why others see the evidence differently. Ask questions.",
                    "Focus on the specific evidence that's dividing us. What exactly concerns you?",
                    "Let's find common ground. What evidence do we all agree on?",
                    "Address each other's concerns directly. Don't just restate your position."
                ]
                await self._foreperson_statement(random.choice(moderation_phrases))
                interruption_count = 0
            
            # First, let mentioned jurors respond
            if self.waiting_to_respond:
                next_speaker = self.waiting_to_respond.pop(0)
                if next_speaker not in self.has_spoken:
                    await self._have_juror_speak_streaming(next_speaker)
                    speakers_this_round += 1
                    self.has_spoken.add(next_speaker)
                    interruption_count += 1
            else:
                # Pick someone who hasn't spoken yet
                remaining = [j_id for j_id in self.agents.keys() if j_id not in self.has_spoken]
                if remaining:
                    # Foreperson might call on quiet jurors
                    if len(remaining) <= 3 and random.random() < 0.5:
                        quiet_juror = random.choice(remaining)
                        await self._foreperson_statement(
                            f"{self.agents[quiet_juror].persona.name}, we haven't heard from you. What are your thoughts?"
                        )
                        await self._have_juror_speak_streaming(quiet_juror)
                    else:
                        next_speaker = random.choice(remaining)
                        await self._have_juror_speak_streaming(next_speaker)
                    speakers_this_round += 1
                    self.has_spoken.add(next_speaker if 'next_speaker' in locals() else quiet_juror)
                    interruption_count += 1
                else:
                    break


import random  # Add at top of file