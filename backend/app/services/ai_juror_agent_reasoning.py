"""
AI Juror Agent using DeepSeek Reasoning Model (deepseek-reasoner)
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


class AIJurorAgentReasoning:
    """AI-powered juror using DeepSeek's reasoning model for better deliberation"""
    
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

Remember: You must presume innocence until proven guilty beyond a reasonable doubt.

SPEAKING STYLE: Talk naturally like different real people. VARY your language - don't use the same phrases as other jurors.

MIX UP these patterns (don't repeat 'gut' or other phrases):
- Start different ways: 'So...', 'Well...', 'I think...', 'Honestly...', 'The way I see it...'
- Show uncertainty: 'I dunno', 'Maybe', 'Could be', 'Not sure', 'Hard to say'
- Personal examples: 'My dad always said...', 'At my job...', 'This one time...'
- Reactions: 'That's wild', 'Seriously?', 'Come on', 'No kidding', 'Right?'
- Questions: 'But what if...?', 'How do we know...?', 'Anyone else think...?'

Sound like DIFFERENT people, not the same person. Each juror should have their own way of talking.

IMPORTANT: Do NOT include physical actions or gestures in asterisks like *leans forward*, *taps table*, *adjusts glasses*. Just speak naturally without stage directions."""
        
        return base_prompt + case_context
    
    async def generate_statement(
        self, 
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None
    ) -> JurorStatement:
        """Generate a statement using reasoning model"""
        
        # Build conversation context
        messages = self._build_conversation_context(phase, previous_statements, prompt_addition)
        
        try:
            # Add unique speech reminder based on persona
            speech_reminder = self._get_speech_reminder()
            
            # Use reasoning model
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": self.system_prompt + f"\n\n{speech_reminder}"},
                    {"role": "user", "content": messages[-1]['content']}
                ],
                max_tokens=4000  # Reasoning model supports up to 64K
            )
            
            # Extract reasoning and content
            reasoning_content = getattr(response.choices[0].message, 'reasoning_content', None)
            content = response.choices[0].message.content
            
            # Log reasoning for debugging
            if reasoning_content:
                logger.info(f"{self.persona.name} reasoning process: {reasoning_content[:300]}...")
            
            # Add to history (only the final content, not reasoning)
            self.conversation_history.extend(messages)
            self.conversation_history.append({"role": "assistant", "content": content})
            
            # Keep only last 10 exchanges
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Determine sentiment based on content
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

Think carefully about:
1. The evidence presented
2. Whether guilt has been proven beyond reasonable doubt
3. Your character's background and perspective

Then provide your verdict in this EXACT JSON format:
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
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": vote_prompt}
                ],
                max_tokens=2000
            )
            
            # Extract reasoning and vote
            reasoning_content = getattr(response.choices[0].message, 'reasoning_content', None)
            response_text = response.choices[0].message.content.strip()
            
            # Log reasoning
            if reasoning_content:
                logger.info(f"{self.persona.name} vote reasoning: {reasoning_content[:300]}...")
            
            # Extract JSON
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
            
            # Better fallback based on personality
            if self.persona.attitudes['trust_courts'] > 0.6:
                verdict = VerdictChoice.GUILTY
                confidence = 0.6
                reasoning = "The evidence seems convincing based on what I've heard."
            elif self.persona.attitudes['trust_courts'] < 0.4:
                verdict = VerdictChoice.NOT_GUILTY
                confidence = 0.6
                reasoning = "I have reasonable doubts about the prosecution's case."
            else:
                verdict = VerdictChoice.UNDECIDED
                confidence = 0.5
                reasoning = "I'm torn between the arguments and need more discussion."
            
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=verdict,
                confidence=confidence,
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
                reasoning="I need more time to consider all the evidence.",
                round_number=round_number
            )
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of statement"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['strongly', 'definitely', 'certain', 'absolutely', 'clearly']):
            return 'assertive'
        elif any(word in content_lower for word in ['maybe', 'perhaps', 'not sure', 'uncertain', 'torn']):
            return 'uncertain'
        elif any(word in content_lower for word in ['disagree', 'wrong', 'but', 'however', 'challenge']):
            return 'challenging'
        elif any(word in content_lower for word in ['agree', 'right', 'exactly', 'precisely']):
            return 'agreeable'
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
                "content": "What's your take on this case? What stands out to you?"
            })
        elif phase == DeliberationPhase.EVIDENCE_REVIEW:
            messages.append({
                "role": "user", 
                "content": "Let's dig into the evidence. What pieces stand out to you - good or bad?"
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
                        "content": f"Here's what's been said:\n\n{discussion}\n\n{opposing_view.juror_name} just made their point. What do you think? Agree? Disagree? Jump in and respond to them directly."
                    })
                elif last_speaker:
                    messages.append({
                        "role": "user",
                        "content": f"Here's what's been said:\n\n{discussion}\n\n{last_speaker.juror_name} just spoke up. What's your take? Do you buy it or not?"
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
    
    def _get_speech_reminder(self) -> str:
        """Generate unique speech reminder for this specific juror"""
        age = self.persona.demographics.get('age', 40)
        edu = self.persona.demographics.get('education_years', 12)
        extraversion = self.persona.personality.get('extraversion', 3)
        agreeableness = self.persona.personality.get('agreeableness', 3)
        
        # Create unique speech patterns based on persona
        reminders = []
        
        if age > 60:
            reminders.append("Start with phrases like 'Back when I...' or 'Now listen here...'")
        elif age < 30:
            reminders.append("Use modern casual speech: 'Honestly...', 'I'm not gonna lie...', 'That's kinda...'")
        
        if edu >= 16:
            reminders.append("Speak professionally but naturally: 'In my experience...', 'I have concerns about...'")
        elif edu < 12:
            reminders.append("Use working-class speech: 'Look here...', 'That ain't right...', 'I don't buy it'")
        
        if extraversion > 4:
            reminders.append("Be animated and interrupt: 'Hold up!', 'Wait a minute!', speak enthusiastically")
        elif extraversion < 2.5:
            reminders.append("Speak quietly and briefly: 'Well...', 'I think...', wait your turn")
        
        if agreeableness < 2.5:
            reminders.append("Be blunt and direct: 'That's wrong', 'Come on', 'No way'")
        
        # Combine into specific guidance
        speech_style = ". ".join(reminders[:3]) if reminders else "Speak naturally"
        
        return f"YOUR UNIQUE SPEECH STYLE: {speech_style}. DO NOT use 'gut' phrases - vary your language! NO physical gestures (*leans*, *taps*, etc.) - just natural speech!"