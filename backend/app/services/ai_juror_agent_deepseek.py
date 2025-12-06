"""
AI Juror Agent using DeepSeek API
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
from app.models.deliberation import (
    JurorPersona, JurorStatement, Vote, VerdictChoice, 
    DeliberationPhase, DeliberationCase
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AIJurorAgentDeepSeek:
    """Represents a single AI-powered juror using DeepSeek"""
    
    def __init__(self, persona: JurorPersona, case: DeliberationCase):
        self.persona = persona
        self.case = case
        # Use DeepSeek API from environment variable
        deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None) or os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        self.client = OpenAI(
            api_key=deepseek_key,
            base_url="https://api.deepseek.com"
        )
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Build the complete system prompt for this juror"""
        base_prompt = self.persona.to_system_prompt()
        
        case_context = f"""

CURRENT CASE: {self.case.case_title}
Type: {self.case.case_type.replace('_', ' ').title()} case

CASE SUMMARY:
{self.case.summary}

KEY EVIDENCE:
{chr(10).join(f'- {evidence}' for evidence in self.case.key_evidence)}

PROSECUTION ARGUES:
{self.case.prosecution_argument}

DEFENSE ARGUES:
{self.case.defense_argument}

JURY INSTRUCTIONS:
{self.case.jury_instructions}

Remember: You must presume innocence until proven guilty beyond a reasonable doubt."""
        
        return base_prompt + case_context
    
    async def generate_statement(
        self, 
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None
    ) -> JurorStatement:
        """Generate a statement from this juror"""
        
        # Build conversation context
        messages = self._build_conversation_context(phase, previous_statements, prompt_addition)
        
        try:
            # DeepSeek uses the same format as OpenAI
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": self.system_prompt + "\n\nIMPORTANT: Do NOT include physical actions, gestures, or stage directions like *adjusts glasses* or *leans forward*. Focus only on your arguments and reasoning."},
                    {"role": "user", "content": messages[-1]['content']}
                ],
                max_tokens=2000
            )
            
            # Extract reasoning content if available
            reasoning_content = getattr(response.choices[0].message, 'reasoning_content', None)
            content = response.choices[0].message.content
            
            # Log reasoning if available (for debugging)
            if reasoning_content:
                logger.debug(f"{self.persona.name} reasoning: {reasoning_content[:200]}...")
            
            # Add to history
            self.conversation_history.extend(messages)
            self.conversation_history.append({"role": "assistant", "content": content})
            
            # Keep only last 10 exchanges
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Determine sentiment
            sentiment = self._analyze_sentiment(content)
            
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=content,
                sentiment=sentiment
            )
            
        except Exception as e:
            logger.error(f"Error generating statement for {self.persona.name}: {e}")
            # Fallback response
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content="I need to hear more before I can form an opinion.",
                sentiment="uncertain"
            )
    
    async def cast_vote(
        self, 
        round_number: int,
        previous_votes: Optional[List[Vote]] = None
    ) -> Vote:
        """Cast a vote with reasoning"""
        
        # Add context about previous votes if available
        vote_context = ""
        if previous_votes and round_number > 1:
            guilty_count = sum(1 for v in previous_votes if v.verdict == VerdictChoice.GUILTY)
            not_guilty_count = sum(1 for v in previous_votes if v.verdict == VerdictChoice.NOT_GUILTY)
            vote_context = f"\n\nPrevious vote was {guilty_count} guilty, {not_guilty_count} not guilty. Consider if the discussion has changed your mind."
        
        vote_prompt = f"""Based on the evidence and discussion so far, what is your verdict?{vote_context}

You MUST respond with ONLY valid JSON in this exact format:
{{"verdict": "guilty", "confidence": 0.8, "reasoning": "The evidence clearly shows..."}}  

IMPORTANT:
- verdict must be EXACTLY one of: "guilty", "not_guilty", "undecided" (with underscore)
- confidence must be a number between 0.0 and 1.0 (e.g., 0.7)
- reasoning should be 1-2 sentences from your character's perspective
- Output ONLY the JSON, nothing else"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": self.system_prompt + "\n\nYou must respond with valid JSON only."},
                    {"role": "user", "content": vote_prompt}
                ],
                max_tokens=1000
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
            # Try to extract JSON if there's extra text
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]
            
            vote_data = json.loads(response_text)
            
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=VerdictChoice(vote_data["verdict"]),
                confidence=float(vote_data["confidence"]),
                reasoning=vote_data["reasoning"],
                round_number=round_number
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for {self.persona.name}: {e}")
            logger.error(f"Response was: {response.choices[0].message.content if 'response' in locals() else 'No response'}")
            # Fallback based on personality
            if self.persona.attitudes['trust_courts'] > 0.6:
                verdict = VerdictChoice.GUILTY
                reasoning = "The evidence seems convincing to me."
            elif self.persona.attitudes['trust_courts'] < 0.4:
                verdict = VerdictChoice.NOT_GUILTY
                reasoning = "I have reasonable doubts about this case."
            else:
                verdict = VerdictChoice.UNDECIDED
                reasoning = "I need more discussion before deciding."
            
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=verdict,
                confidence=0.5,
                reasoning=reasoning,
                round_number=round_number
            )
        except Exception as e:
            logger.error(f"Error casting vote for {self.persona.name}: {e}")
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=VerdictChoice.UNDECIDED,
                confidence=0.5,
                reasoning="I need more discussion before deciding.",
                round_number=round_number
            )
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of statement"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['strongly', 'definitely', 'certain', 'absolutely']):
            return 'assertive'
        elif any(word in content_lower for word in ['maybe', 'perhaps', 'not sure', 'uncertain']):
            return 'uncertain'
        elif any(word in content_lower for word in ['disagree', 'wrong', 'but', 'however']):
            return 'challenging'
        else:
            return 'neutral'
    
    def _build_conversation_context(
        self,
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Build message context for the AI"""
        
        messages = []
        
        # Add phase-specific prompts
        if phase == DeliberationPhase.OPENING:
            messages.append({
                "role": "user",
                "content": "Please share your initial thoughts on this case. What stands out to you?"
            })
        elif phase == DeliberationPhase.EVIDENCE_REVIEW:
            messages.append({
                "role": "user", 
                "content": "Let's review the evidence. What pieces of evidence do you find most compelling or problematic?"
            })
        elif phase == DeliberationPhase.DISCUSSION:
            # Add recent statements from other jurors
            if previous_statements:
                recent_statements = previous_statements[-5:]  # Last 5 statements
                
                # Find if anyone mentioned this juror or made strong claims
                last_speaker = recent_statements[-1] if recent_statements else None
                opposing_view = None
                for stmt in recent_statements:
                    if stmt.sentiment in ['assertive', 'challenging']:
                        opposing_view = stmt
                        break
                
                discussion = "\n\n".join([
                    f"{stmt.juror_name}: {stmt.content}"
                    for stmt in recent_statements
                ])
                
                # Create more direct prompts
                if opposing_view and opposing_view.juror_id != self.persona.juror_id:
                    messages.append({
                        "role": "user",
                        "content": f"Here's the recent discussion:\n\n{discussion}\n\n{opposing_view.juror_name} just made a strong argument. Respond directly to their points. You can agree, disagree, or challenge their reasoning. Address them by name."
                    })
                elif last_speaker:
                    messages.append({
                        "role": "user",
                        "content": f"Here's the recent discussion:\n\n{discussion}\n\nRespond to what {last_speaker.juror_name} just said. Build on their points or respectfully challenge them if you disagree."
                    })
                else:
                    messages.append({
                        "role": "user",
                        "content": f"Here's what other jurors have said:\n\n{discussion}\n\nWhat are your thoughts? Feel free to directly address other jurors by name."
                    })
            else:
                messages.append({
                    "role": "user",
                    "content": "Let's discuss the case. What's your perspective on the evidence and arguments presented?"
                })
        
        # Add any additional prompt
        if prompt_addition:
            messages.append({"role": "user", "content": prompt_addition})
        
        return messages