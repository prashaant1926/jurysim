"""
Realistic AI Juror Agent with authentic speech and behavior patterns
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
import random
from datetime import datetime
from pathlib import Path
from app.models.deliberation import (
    JurorPersona, JurorStatement, Vote, VerdictChoice, 
    DeliberationPhase, DeliberationCase
)
from app.core.config import settings
from app.services.realistic_speech_generator import RealisticSpeechGenerator
from app.services.jury_dynamics_manager import JuryDynamicsManager, JurorRole
from app.services.realistic_deliberation_flow import RealisticDeliberationFlow
import logging

logger = logging.getLogger(__name__)


class RealisticAIJurorAgent:
    """AI Juror with realistic speech patterns and behavior"""
    
    def __init__(self, 
                 persona: JurorPersona, 
                 case: DeliberationCase,
                 dynamics_manager: JuryDynamicsManager,
                 flow_manager: RealisticDeliberationFlow,
                 session_id: Optional[str] = None):
        self.persona = persona
        self.case = case
        self.dynamics_manager = dynamics_manager
        self.flow_manager = flow_manager
        self.speech_generator = RealisticSpeechGenerator()
        self.session_id = session_id or str(datetime.utcnow().timestamp())
        
        # Use DeepSeek API from environment variable
        deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None) or os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        self.client = OpenAI(
            api_key=deepseek_key,
            base_url="https://api.deepseek.com"
        )
        self.conversation_history: List[Dict[str, str]] = []
        self.full_transcript: List[Dict[str, Any]] = []
        self.system_prompt = self._build_realistic_system_prompt()
        
        # Get assigned role and current state
        self.role = dynamics_manager.juror_roles[persona.juror_id]
        self.state = dynamics_manager.juror_states[persona.juror_id]
        
        # Track current verdict position
        self.current_verdict = VerdictChoice.UNDECIDED
        
        # Set up transcript file
        self._setup_transcript_file()
        
    def _build_realistic_system_prompt(self) -> str:
        """Build system prompt for realistic behavior"""
        base_prompt = f"""You are {self.persona.name}, a {self.persona.demographics.age}-year-old {self.persona.demographics.race} {self.persona.demographics.gender.lower()} from {self.persona.demographics.community_type} {self.persona.demographics.city}, {self.persona.demographics.state}.

IMPORTANT: You must speak naturally like a real person in a jury room, NOT like an AI or formal speaker.

Your background:
- Occupation: {self.persona.demographics.occupation}
- Education: {self.persona.demographics.education_level} ({self.persona.demographics.education_years} years)
- Income: ${self.persona.demographics.income:,}/year
- {self.persona.interview_summary}

Your personality and role:
- You are a {self.role.value} in this jury
"""
        
        # Add role-specific behavior
        role_behaviors = {
            JurorRole.LEADER: "You naturally take charge and try to organize the discussion. You speak first and often.",
            JurorRole.BULLY: "You dominate conversations, dismiss others' opinions, and get frustrated when people disagree with you.",
            JurorRole.SILENT_OBSERVER: "You rarely speak up unless directly asked or when you have something crucial to say.",
            JurorRole.PEACEMAKER: "You try to keep everyone calm and find common ground. You hate conflict.",
            JurorRole.CHALLENGER: "You question everything and play devil's advocate. You don't accept things at face value.",
            JurorRole.FENCE_SITTER: "You have trouble making decisions and keep changing your mind.",
            JurorRole.DETAIL_ORIENTED: "You focus on specific evidence details and want everything to be precise.",
            JurorRole.EMOTIONAL_APPEALER: "You make arguments based on feelings and personal experiences.",
            JurorRole.REBEL: "You tend to go against the majority just to be different.",
            JurorRole.FOLLOWER: "You tend to agree with whoever speaks most confidently."
        }
        
        base_prompt += f"\n{role_behaviors.get(self.role, '')}\n\n"
        
        # Add speech style instructions
        base_prompt += """
CRITICAL SPEECH RULES:
1. Use casual, conversational language - contractions, slang, incomplete sentences
2. Add filler words like "um", "uh", "like", "you know" naturally
3. Sometimes trail off mid-sentence...
4. Interrupt or react emotionally when frustrated
5. Make grammar mistakes, especially when emotional
6. Reference your personal life and experiences
7. Express physical needs (hungry, tired, need bathroom)
8. Show confusion about legal terms or procedures
9. React to other jurors personally, not just their arguments
10. Let your mood affect how you speak

NEVER speak in perfect paragraphs or use sophisticated vocabulary unless it truly fits your background.
"""
        
        # Add case context
        base_prompt += f"\n\nCASE: {self.case.case_title}\n{self.case.summary}"
        
        return base_prompt
    
    def _setup_transcript_file(self):
        """Set up transcript file for this juror"""
        self.transcript_dir = Path("/Users/prashaantranganathan/FreudLaw/backend/transcripts")
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir = self.transcript_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = self.persona.name.replace(" ", "_").replace("/", "_")
        self.transcript_file = self.session_dir / f"juror_{self.persona.juror_id}_{safe_name}_realistic.txt"
        
        # Initialize with header
        self._init_transcript_file()
    
    def _init_transcript_file(self):
        """Initialize transcript with realistic header"""
        header = f"""JURY DELIBERATION TRANSCRIPT - REALISTIC SIMULATION
Session ID: {self.session_id}
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

JUROR INFORMATION:
Name: {self.persona.name}
Role: {self.role.value}
Demographics: {self.persona.demographics.age}yo {self.persona.demographics.race} {self.persona.demographics.gender}
Occupation: {self.persona.demographics.occupation}
Education: {self.persona.demographics.education_level}

{'='*80}
TRANSCRIPT:
{'='*80}

"""
        with open(self.transcript_file, 'w') as f:
            f.write(header)
    
    async def generate_statement(
        self, 
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None,
        allow_interruption: bool = True
    ) -> JurorStatement:
        """Generate realistic statement with possible interruptions"""
        
        # Check if we need a break
        needs_break, break_type = self.dynamics_manager.needs_break()
        if needs_break and random.random() < 0.3:
            content = self._generate_break_request(break_type)
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=content,
                sentiment="frustrated"
            )
        
        # Get emotional state
        emotional_state = self.dynamics_manager.get_emotional_state(self.persona.juror_id)
        
        # Check for procedural confusion
        confusion = self.flow_manager.get_procedural_confusion(phase)
        if confusion and self.role != JurorRole.LEADER and random.random() < 0.3:
            content = self.speech_generator.add_speech_realism(
                confusion, self.persona, "confused"
            )
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=content,
                sentiment="uncertain"
            )
        
        # Build context for AI
        messages = self._build_realistic_context(phase, previous_statements, emotional_state)
        
        try:
            # Get AI response using DeepSeek
            deepseek_messages = [
                {"role": "system", "content": self.system_prompt + f"\n\nCurrent emotional state: {emotional_state}"},
                {"role": "user", "content": messages[-1]['content'] + "\n\nRespond in 2-4 sentences. Be thoughtful and reference evidence by number. Show your reasoning process."}
            ]
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=deepseek_messages,
                max_tokens=200,  # Allow for more thoughtful deliberation
                temperature=0.9
            )
            
            raw_content = response.choices[0].message.content
            
            # Apply realistic speech patterns
            content = self.speech_generator.add_speech_realism(
                raw_content, self.persona, emotional_state
            )
            
            # Check for interruption
            if allow_interruption and previous_statements:
                last_speaker = previous_statements[-1].juror_id
                if self.dynamics_manager.should_interrupt(last_speaker, self.persona.juror_id):
                    interrupted, interruption = self.speech_generator.generate_interruption(
                        self.persona, content, emotional_state
                    )
                    
                    # Record interruption
                    self.dynamics_manager.record_interaction(last_speaker, interrupted=True)
                    self.dynamics_manager.record_interaction(self.persona.juror_id)
                    
                    content = interruption
            
            # Analyze sentiment
            sentiment = self._analyze_realistic_sentiment(content, emotional_state)
            
            # Create statement
            statement = JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=content,
                sentiment=sentiment
            )
            
            # Record to transcript
            self._append_to_transcript("STATEMENT", content, {
                "Phase": phase.value,
                "Emotional State": emotional_state,
                "Sentiment": sentiment,
                "Role": self.role.value
            })
            
            return statement
            
        except Exception as e:
            logger.error(f"Error generating statement for {self.persona.name}: {e}")
            # Realistic fallback
            fallback_responses = {
                JurorRole.SILENT_OBSERVER: "...",
                JurorRole.FENCE_SITTER: "I... I don't know what to think",
                JurorRole.BULLY: "This is stupid",
                JurorRole.FOLLOWER: "What they said"
            }
            
            content = fallback_responses.get(self.role, "I need a minute")
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=content,
                sentiment="uncertain"
            )
    
    def _generate_break_request(self, break_type: str) -> str:
        """Generate realistic break requests"""
        requests = {
            "bathroom": [
                "Sorry, I really need to use the restroom",
                "Can we take a quick bathroom break?",
                "I gotta go... like now"
            ],
            "meal": [
                "Look, I'm starving. Can we break for lunch?",
                "My blood sugar's dropping. I need food.",
                "It's been hours. When do we eat?"
            ],
            "cooling_off": [
                "We need to take a break before someone says something they regret",
                "Everyone needs to calm down. Let's take 10.",
                "I need some air"
            ],
            "scheduled": [
                "We've been at this for 2 hours. Time for a break.",
                "Judge said we could have breaks, right?",
                "My back is killing me. Can we stretch?"
            ]
        }
        
        return random.choice(requests.get(break_type, ["I need a break"]))
    
    def _build_realistic_context(self, 
                                phase: DeliberationPhase,
                                previous_statements: List[JurorStatement],
                                emotional_state: str) -> List[Dict[str, str]]:
        """Build context that encourages realistic responses"""
        messages = []
        
        # Add time pressure comments
        if self.dynamics_manager.deliberation_time > 180:  # 3 hours
            time_comment = self.flow_manager.generate_time_pressure_comment(
                self.dynamics_manager.deliberation_time / 60
            )
            if time_comment:
                messages.append({"role": "user", "content": time_comment})
        
        # Phase-specific prompts
        if phase == DeliberationPhase.OPENING:
            prompts = [
                "What's your gut reaction to this case? Take your time and explain what evidence impacts you most.",
                "First thoughts? Walk us through your initial impression of the key evidence.",
                "So what does everyone think? Share your perspective on the most important evidence items."
            ]
        elif phase == DeliberationPhase.EVIDENCE_REVIEW:
            prompts = [
                "What stood out to you from the evidence? Explain why it matters to your decision.",
                "Did anyone else notice the issues with the evidence? Share your concerns in detail.",
                "The thing that gets me is... explain what troubles or convinces you about specific evidence."
            ]
        else:
            prompts = ["Share your thoughts on what's been discussed. Take time to explain your reasoning."]
        
        messages.append({"role": "user", "content": random.choice(prompts)})
        
        return messages
    
    def _analyze_realistic_sentiment(self, content: str, emotional_state: str) -> str:
        """Analyze sentiment considering emotional state"""
        content_lower = content.lower()
        
        # Emotional state overrides
        if emotional_state in ["angry", "frustrated"]:
            return "challenging"
        elif emotional_state == "exhausted":
            return "resigned"
        
        # Content analysis
        if any(phrase in content_lower for phrase in ["are you serious", "ridiculous", "stupid"]):
            return "hostile"
        elif any(phrase in content_lower for phrase in ["i guess", "maybe", "don't know"]):
            return "uncertain"
        elif "!" in content:
            return "assertive"
        else:
            return "neutral"
    
    def _append_to_transcript(self, entry_type: str, content: str, metadata: Dict[str, Any] = None):
        """Append to transcript file"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        entry = f"\n[{timestamp}] {entry_type}\n"
        if metadata:
            for key, value in metadata.items():
                entry += f"  {key}: {value}\n"
        entry += f"  Content: {content}\n"
        entry += "-" * 60 + "\n"
        
        with open(self.transcript_file, 'a') as f:
            f.write(entry)