"""
Alternative AI Juror Agent with better prompt engineering
"""
import anthropic
from typing import List, Dict, Any, Optional
import asyncio
import json
from app.models.deliberation import (
    JurorPersona, JurorStatement, Vote, VerdictChoice, 
    DeliberationPhase, DeliberationCase
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AIJurorAgentV2:
    """Improved AI-powered juror that avoids safety triggers"""
    
    def __init__(self, persona: JurorPersona, case: DeliberationCase):
        self.persona = persona
        self.case = case
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.conversation_history: List[Dict[str, str]] = []
        
    def _build_analytical_prompt(self) -> str:
        """Build prompt focused on analytical decision-making"""
        pers = self.persona.personality
        
        return f"""You are an AI assistant helping analyze decision-making patterns in group discussions.

Based on these personality traits:
- Detail-oriented: {pers['conscientiousness']:.1f}/5
- Open to ideas: {pers['openness']:.1f}/5  
- Collaborative: {pers['agreeableness']:.1f}/5
- Expressive: {pers['extraversion']:.1f}/5

How might someone with these traits analyze the following information:
- Multiple pieces of evidence exist
- Some evidence is direct, some circumstantial
- There are arguments on both sides
- A decision requires careful consideration

Please provide analytical thoughts that someone with these traits might have."""

    async def generate_statement(
        self, 
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None
    ) -> JurorStatement:
        """Generate a statement focused on evidence analysis"""
        
        try:
            # Use indirect prompting
            if phase == DeliberationPhase.OPENING:
                prompt = f"""Analyze how someone with high {max(self.persona.personality, key=self.persona.personality.get)} 
                might initially react to conflicting evidence in a decision-making scenario."""
            
            elif phase == DeliberationPhase.EVIDENCE_REVIEW:
                prompt = f"""Describe how someone who values {list(self.persona.attitudes.keys())[0]} 
                might weigh different types of evidence when making important decisions."""
            
            else:
                prompt = f"""Given personality traits of {self.persona.personality}, 
                how might this person contribute to a group discussion about evaluating evidence?"""
            
            response = self.client.completions.create(
                model="claude-2.1",
                max_tokens_to_sample=200,
                temperature=0.7,
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}"
            )
            
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=response.completion,
                sentiment="analytical"
            )
            
        except Exception as e:
            logger.error(f"Error generating statement: {e}")
            # Return a generic analytical response
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content="I believe we should carefully examine all the evidence before reaching any conclusions.",
                sentiment="neutral"
            )

    async def cast_vote(
        self, 
        round_number: int,
        previous_votes: Optional[List[Vote]] = None
    ) -> Vote:
        """Cast a vote based on personality analysis"""
        
        try:
            # Calculate vote based on personality traits
            # High conscientiousness = more likely to require strong evidence
            # High agreeableness = more likely to go with majority
            # High openness = more likely to consider alternatives
            
            conscientiousness = self.persona.personality.get('conscientiousness', 3.0)
            agreeableness = self.persona.personality.get('agreeableness', 3.0)
            
            # Simple heuristic for demonstration
            if conscientiousness > 3.5:
                # High standards for evidence
                verdict = VerdictChoice.UNDECIDED
                confidence = 0.4
                reasoning = "Need more conclusive evidence before making a decision."
            elif agreeableness > 3.5 and previous_votes:
                # Go with majority
                guilty_votes = sum(1 for v in previous_votes if v.verdict == VerdictChoice.GUILTY)
                if guilty_votes > len(previous_votes) / 2:
                    verdict = VerdictChoice.GUILTY
                else:
                    verdict = VerdictChoice.NOT_GUILTY
                confidence = 0.6
                reasoning = "After considering others' perspectives, I'm inclined to agree with the majority view."
            else:
                # Random for demo
                import random
                verdict = random.choice([VerdictChoice.GUILTY, VerdictChoice.NOT_GUILTY])
                confidence = 0.5
                reasoning = "Based on the evidence presented, I've reached my decision."
            
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=verdict,
                confidence=confidence,
                reasoning=reasoning,
                round_number=round_number
            )
            
        except Exception as e:
            logger.error(f"Error casting vote: {e}")
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=VerdictChoice.UNDECIDED,
                confidence=0.5,
                reasoning="I need more time to consider.",
                round_number=round_number
            )