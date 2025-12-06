"""
AI Juror Agent using Claude Opus 4.5
"""
import anthropic
from typing import List, Dict, Any, Optional, Callable
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from app.models.deliberation import (
    JurorPersona, JurorStatement, Vote, VerdictChoice,
    DeliberationPhase, DeliberationCase
)
from app.core.config import settings
from app.services.realistic_jury_behaviors import RealisticJuryBehaviors
import logging
import random
import numpy as np

logger = logging.getLogger(__name__)


class AIJurorAgent:
    """Represents a single AI-powered juror"""

    def __init__(self, persona: JurorPersona, case: DeliberationCase, session_id: Optional[str] = None):
        self.persona = persona
        self.case = case
        self.session_id = session_id or str(datetime.utcnow().timestamp())
        # Use Anthropic Claude Opus 4.5
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.conversation_history: List[Dict[str, str]] = []
        self.full_transcript: List[Dict[str, Any]] = []  # Complete record of all interactions
        self.system_prompt = self._build_system_prompt()
        self.deliberation_start_time = datetime.utcnow()
        self.simulated_hours = 0.0  # Track simulated deliberation time
        self.frustration_level = 0  # Increases over time
        self.has_shown_confusion = False  # Track if confused about legal concepts
        self.stubborn_on_verdict = None  # If set, juror won't change from this verdict
        
        # Enhanced tracking
        self.confidence_history: List[float] = []  # Track confidence evolution
        self.evidence_interpretations: Dict[int, str] = {}  # Track how juror views each evidence
        self.peer_influence_log: List[str] = []  # Track which arguments influenced them
        
        # Set up transcript file
        self.transcript_dir = Path("/Users/prashaantranganathan/FreudLaw/backend/transcripts")
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir = self.transcript_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Individual juror transcript file
        safe_name = self.persona.name.replace(" ", "_").replace("/", "_")
        self.transcript_file = self.session_dir / f"juror_{self.persona.juror_id}_{safe_name}.txt"
        
        # Initialize transcript file with header
        self._init_transcript_file()
        
    def _build_system_prompt(self) -> str:
        """Build the complete system prompt for this juror"""
        base_prompt = self.persona.to_system_prompt()
        demo = self.persona.demographics
        
        # Add reasoning approach section
        reasoning_section = f"""

REASONING APPROACH:
Before responding, mentally work through:
1. EVIDENCE FOCUS: Which specific evidence numbers are most relevant to this discussion point?
2. BACKGROUND LENS: How does your {demo.get('education_level', 'background')} background and ${demo.get('income', 50000):,}/year income perspective shape your interpretation?
3. LEGAL STANDARD: Does this evidence help prove/disprove guilt "beyond reasonable doubt"?
4. PEER INFLUENCE: How are other jurors' points affecting your thinking?
5. CONVICTION LEVEL: How certain are you, and what would change your mind?

Your responses should reflect this internal processing while maintaining natural speech patterns.

CONFIDENCE EVOLUTION:
Track how certain you are about guilt/innocence on a scale of 1-10:
- Start with your initial impression based on evidence
- Adjust as discussion reveals new interpretations
- Show this uncertainty in your speech ("I'm starting to think...", "I'm less sure about...")
- Your confidence should fluctuate realistically based on compelling arguments
"""
        
        # Add background-specific guidance
        background_guidance = self._get_background_specific_guidance()
        
        case_context = f"""

DECISION-MAKING SCENARIO FOR ANALYSIS:
As part of the interview, participants were asked how they would evaluate evidence in different scenarios.

SCENARIO TYPE: {self.case.case_type.replace('_', ' ').title()} evidence evaluation
Topic: {self.case.case_title}

SCENARIO DESCRIPTION:
{self.case.summary}

KEY EVIDENCE PRESENTED:
{chr(10).join(f'{i+1}. {evidence}' for i, evidence in enumerate(self.case.key_evidence))}

PROSECUTION'S ARGUMENT:
{self.case.prosecution_argument}

DEFENSE'S ARGUMENT:
{self.case.defense_argument}

JURY INSTRUCTIONS:
{self.case.jury_instructions}

IMPORTANT: When discussing the case, you MUST reference specific evidence items by number (e.g., "Evidence #1 shows..." or "The video footage (#3)...").

JURY PRINCIPLES YOU MUST FOLLOW:
1. Decide facts based solely on evidence presented - no speculation or outside knowledge
2. Apply the law as instructed - not your personal views on what the law should be
3. Remain impartial - set aside personal prejudices
4. Presume innocence - the defendant is innocent until proven guilty
5. Require proof beyond reasonable doubt - not just "probably guilty"

REALISTIC BEHAVIOR GUIDELINES:
- You're a REAL PERSON with emotions, confusion, and fatigue, not a legal robot
- You might get frustrated, confused about legal terms, or go off-topic
- Your education level ({demo.get('education_years', 12)} years) affects how you speak
- You may misunderstand "reasonable doubt" or other legal concepts
- Sometimes you'll focus on irrelevant details or share unrelated stories
- As time goes on, you'll get more tired, irritable, and less patient
- You have personal biases that might slip through despite trying to be fair
- Based on your personality, you might be stubborn and refuse to change your mind

DISCUSSION STYLE - HOW REAL PEOPLE ACTUALLY TALK:

DO NOT sound like a lawyer, analyst, or AI assistant. Sound like a REAL PERSON in a jury room.

FORBIDDEN PATTERNS (do NOT do these):
❌ "*takes a breath*", "*pauses*", "*leans forward*" - NO stage directions
❌ "Evidence #1 shows... Evidence #2 indicates... Evidence #3 suggests..." - NO systematic listing
❌ "I think we need to consider..." followed by 3 bullet points - NO structured analysis
❌ Perfect grammar and complete sentences - real people DON'T talk this way
❌ Covering everything comprehensively - real people focus on ONE thing
❌ Sounding articulate and polished - real people are messy
❌ Copying the previous speaker's tone, structure, or phrasing

REQUIRED PATTERNS (DO these):
✓ Jump straight in - no preamble, no setup, just react
✓ Focus on ONE thing that bugs you or strikes you - maybe two max
✓ Interrupt yourself - "Wait, no, actually..." or "I mean..." or trail off
✓ Use filler words - "like", "you know", "I dunno", "um", "uh"
✓ React emotionally first, analytically second (if at all)
✓ Reference other jurors by name - "I agree with Sarah" or "Tom, you're wrong about..."
✓ Sound different from everyone else - if someone just gave a long analysis, be brief; if they were emotional, be analytical; if they spoke formally, be casual
✓ Be incomplete - it's okay to not finish your thought
✓ Use casual/imperfect grammar - "ain't", "gonna", "kinda", "sorta"

EXAMPLES OF GOOD VS BAD:

BAD (too polished): "*takes a breath* Looking at the evidence systematically, Evidence #1 shows the timeline is questionable, Evidence #2 suggests the witness testimony conflicts, and Evidence #3 indicates..."

GOOD (natural): "Wait, hold on - that timeline makes no sense. If he left at 9, how's he showing up on camera at 8:45? That's... I mean, am I missing something here?"

BAD (too comprehensive): "After carefully reviewing all the evidence presented, I believe we need to consider the credibility of each witness, the forensic evidence, and the defendant's alibi in totality."

GOOD (focused, casual): "Look, I just don't buy what that witness said. She's changing her story, you know? First it was blue, now it's green. Like, which is it?"

VOICE VARIETY:
Each juror sounds TOTALLY different. Some are:
- Terse and blunt: "That's BS. He's lying."
- Rambling and uncertain: "I mean, I guess... I dunno, it just seems like maybe we're not seeing the whole... you know?"
- Emotional and reactive: "This is ridiculous! How can anyone think..."
- Analytical but casual: "Okay so if we do the math, timeline doesn't work, right?"
- Folksy and storytelling: "My uncle had something like this happen and..."
- Frustrated and tired: "Can we just... look, bottom line is..."

CRITICAL: If you notice yourself sounding like the previous speaker, STOP and change your approach entirely.

REASONABLE DOUBT CHECK:
Remember: "Reasonable doubt" means doubt based on reason and common sense from evidence. It's NOT:
- Speculation about what might have happened
- Requiring 100% certainty
- Doubts based on possibilities not supported by evidence

When discussing evidence, consider: "Does this evidence, combined with other evidence, prove guilt beyond reasonable doubt?"

{background_guidance}

GROUP AWARENESS:
Notice the deliberation dynamics:
- Who is dominating the conversation?
- Are quieter jurors being heard?
- Is the group rushing to judgment or being thorough?
- Are personality conflicts affecting evidence discussion?

Occasionally comment on the process itself, not just content.

REMEMBER: 
- The prosecution must prove guilt beyond a reasonable doubt
- Base your decision ONLY on the evidence presented in this case
- Reasonable doubt means doubt based on reason and common sense
- {"A unanimous verdict is required" if self.case.requires_unanimous else "A majority verdict is acceptable"}
"""
        
        return base_prompt + reasoning_section + case_context
    
    def _get_background_specific_guidance(self) -> str:
        """Get guidance specific to juror's background"""
        demo = self.persona.demographics
        guidance_parts = []
        
        # Education-based guidance
        if demo.get('education_years', 12) < 12:
            guidance_parts.append(
                "You might find legal concepts confusing. Ask questions about terms you don't understand. "
                "Focus on common-sense interpretation of evidence."
            )
        elif demo.get('education_years', 12) >= 16:
            guidance_parts.append(
                "Your education allows you to analyze evidence systematically, but be careful not to "
                "overthink or dismiss common-sense interpretations."
            )
        
        # Income-based guidance
        if demo.get('income', 50000) < 30000:
            guidance_parts.append(
                "You may be skeptical of authority figures and expensive legal defenses. "
                "Your experience with law enforcement might differ from wealthier jurors."
            )
        elif demo.get('income', 50000) > 100000:
            guidance_parts.append(
                "Your financial security might affect how you view property crimes or financial motives. "
                "Be aware of how your privilege might bias your perspective."
            )
        
        # Location-based guidance
        if not demo.get('urban', True):
            guidance_parts.append(
                "You might have different views on self-defense, gun ownership, and community policing than urban jurors."
            )
        
        # Occupation-based guidance
        occupation = demo.get('occupation', '').lower()
        if any(med in occupation for med in ['nurse', 'doctor', 'medical', 'health']):
            guidance_parts.append(
                "You can offer unique insights into medical evidence, injury assessment, and scientific testimony."
            )
        elif any(law in occupation for law in ['police', 'security', 'law enforcement']):
            guidance_parts.append(
                "Your law enforcement background gives you insight into police procedures and evidence collection."
            )
        
        if guidance_parts:
            return "\nBACKGROUND-SPECIFIC GUIDANCE:\n" + "\n".join(f"- {part}" for part in guidance_parts)
        return ""
    
    def increment_simulated_time(self, hours: float):
        """Increment the simulated deliberation time"""
        self.simulated_hours += hours
    
    def _get_fatigue_modifier(self, hours: float) -> str:
        """Get fatigue-based prompt modifier"""
        if hours < 2:
            return ""
        elif hours < 4:
            return f"\n\nDELIBERATION FATIGUE (Hour {int(hours)}):\nYou're getting tired. Show this through:\n- Shorter responses\n- More direct/blunt language\n- Impatience with repetitive arguments\n- Focus on wanting to reach a decision"
        else:
            return f"\n\nDELIBERATION FATIGUE (Hour {int(hours)}):\nYou're exhausted. Show:\n- Irritability with semantic arguments\n- Desire to focus on 'bottom line' evidence\n- Less patience for complex legal nuances\n- More emotional reactions"

    def _get_dynamic_voice_style(self) -> str:
        """Get a randomized voice style modifier for this specific response"""
        demo = self.persona.demographics
        personality = self.persona.personality

        # Build pool of possible voice styles based on personality and demographics
        voice_styles = []

        # Education-based styles
        if demo.get('education_years', 12) < 12:
            voice_styles.extend([
                "Keep it simple and straightforward. No fancy words.",
                "Talk like you're at a diner, not a courtroom.",
                "Use your gut feeling, not academic analysis."
            ])
        elif demo.get('education_years', 12) >= 16:
            voice_styles.extend([
                "You can be analytical, but don't be a know-it-all about it.",
                "Smart doesn't mean wordy - get to the point.",
                "Explain clearly, but casually."
            ])

        # Personality-based styles
        if personality.get('extraversion', 3) > 3.5:
            voice_styles.extend([
                "Be vocal and energetic - you're not shy.",
                "Jump in with confidence - you like being heard.",
                "Don't hold back - say what you think."
            ])
        elif personality.get('extraversion', 3) < 2.5:
            voice_styles.extend([
                "You're more reserved - shorter, quieter input.",
                "You don't need to fill the silence - be brief.",
                "Speak up when it matters, otherwise stay quiet."
            ])

        if personality.get('agreeableness', 3) > 4:
            voice_styles.extend([
                "You want harmony - try to find common ground.",
                "Be diplomatic, not confrontational.",
                "Acknowledge others' points before disagreeing."
            ])
        elif personality.get('agreeableness', 3) < 2.5:
            voice_styles.extend([
                "You don't sugarcoat - be blunt if you disagree.",
                "Don't worry about stepping on toes.",
                "Call out BS when you see it."
            ])

        if personality.get('neuroticism', 3) > 3.5:
            voice_styles.extend([
                "You're anxious about getting this right - show uncertainty.",
                "Second-guess yourself mid-sentence.",
                "Express worry about making the wrong call."
            ])

        if personality.get('openness', 3) > 4:
            voice_styles.extend([
                "Consider alternative perspectives - maybe you're missing something.",
                "Be open to changing your mind.",
                "Ask 'what if' questions."
            ])
        elif personality.get('openness', 3) < 2.5:
            voice_styles.extend([
                "Stick to what makes sense to you - don't overcomplicate.",
                "You know what you think - be firm.",
                "Black and white, no gray areas."
            ])

        # Age-based styles
        age = demo.get('age', 45)
        if age < 30:
            voice_styles.extend([
                "You might use more casual, modern language.",
                "You're less formal than older jurors."
            ])
        elif age > 60:
            voice_styles.extend([
                "You've seen a lot in life - maybe reference past experience.",
                "You might be more traditional in how you speak."
            ])

        # Add some universal style variations
        universal_styles = [
            "Be terse this time - 1-2 sentences max.",
            "React emotionally, not logically.",
            "Focus on just ONE specific detail.",
            "Be uncertain and questioning.",
            "Be confident and decisive.",
            "Interrupt your own thought halfway through.",
            "Reference another juror's point directly.",
            "Express frustration with something.",
            "Ask a question instead of making a statement."
        ]

        voice_styles.extend(universal_styles)

        # Pick one random style
        chosen_style = random.choice(voice_styles)

        return f"\n\nVOICE STYLE FOR THIS RESPONSE:\n{chosen_style}"
    
    async def generate_statement(
        self,
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> JurorStatement:
        """Generate a statement from this juror with optional streaming"""

        # Build conversation context
        messages = self._build_conversation_context(phase, previous_statements, prompt_addition)

        # Use simulated deliberation hours
        deliberation_hours = self.simulated_hours

        # Add fatigue effects
        fatigue_modifier = self._get_fatigue_modifier(deliberation_hours)

        # Add dynamic voice style variation
        voice_style = self._get_dynamic_voice_style()

        # Check for realistic interruptions/behaviors
        realistic_response = RealisticJuryBehaviors.generate_authentic_response(
            self.persona,
            phase.value,
            deliberation_hours
        )

        # Sometimes inject realistic behaviors instead of on-topic response
        if realistic_response and random.random() < 0.3:  # 30% chance
            self.frustration_level += 0.1
            # If streaming, output the realistic response
            if stream_callback:
                stream_callback(realistic_response)
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=realistic_response,
                sentiment="frustrated" if self.frustration_level > 0.5 else "uncertain"
            )

        try:
            # Set generous token limits for natural conversation
            if phase == DeliberationPhase.OPENING:
                max_tokens = 500
            elif phase == DeliberationPhase.EVIDENCE_REVIEW:
                max_tokens = 400
            elif phase == DeliberationPhase.DISCUSSION:
                max_tokens = 300
            else:
                max_tokens = 400

            # Add randomness to temperature for varied sentence structure
            temperature = random.uniform(0.85, 1.0)

            # Use streaming if callback provided
            content = ""
            stop_reason = None

            if stream_callback:
                # Stream the response
                with self.client.messages.stream(
                    model="claude-opus-4-5-20251101",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=self.system_prompt + fatigue_modifier + voice_style,
                    messages=[
                        {"role": "user", "content": messages[-1]['content']}
                    ]
                ) as stream:
                    for text in stream.text_stream:
                        content += text
                        stream_callback(text)
                    # Get the final message to check stop_reason
                    final_message = stream.get_final_message()
                    stop_reason = final_message.stop_reason
            else:
                # Non-streaming response
                response = self.client.messages.create(
                    model="claude-opus-4-5-20251101",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=self.system_prompt + fatigue_modifier + voice_style,
                    messages=[
                        {"role": "user", "content": messages[-1]['content']}
                    ]
                )
                content = response.content[0].text
                stop_reason = response.stop_reason

            # Check if response was truncated (Anthropic uses stop_reason)
            if stop_reason == "max_tokens":
                # Complete the last sentence properly
                if content and not content.rstrip().endswith(('.', '!', '?')):
                    # Find the last complete sentence
                    last_period = content.rfind('.')
                    last_exclaim = content.rfind('!')
                    last_question = content.rfind('?')
                    last_complete = max(last_period, last_exclaim, last_question)

                    if last_complete > 0:
                        content = content[:last_complete + 1]
                    else:
                        # If no complete sentence, add ellipsis
                        content = content.rstrip() + "..."
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": content
            })
            
            # Determine sentiment based on content
            sentiment = self._analyze_sentiment(content)
            
            statement = JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=content,
                sentiment=sentiment
            )
            
            # Record in full transcript
            self.full_transcript.append({
                "type": "statement",
                "timestamp": datetime.utcnow().isoformat(),
                "juror_id": self.persona.juror_id,
                "juror_name": self.persona.name,
                "phase": phase.value,
                "content": content,
                "sentiment": sentiment,
                "prompt": messages[-1]['content'] if messages else None,
                "confidence_level": self.confidence_history[-1] if self.confidence_history else None
            })
            
            # Write to transcript file
            self._append_to_transcript(
                "STATEMENT",
                content,
                {
                    "Phase": phase.value,
                    "Sentiment": sentiment
                }
            )
            
            return statement
            
        except Exception as e:
            logger.error(f"Error generating statement for {self.persona.name}: {e}")
            # Fallback response
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content="I need more time to think about this.",
                sentiment="uncertain"
            )
    
    async def cast_vote(
        self, 
        round_number: int,
        previous_votes: Optional[List[Vote]] = None,
        recent_discussion: Optional[List[JurorStatement]] = None
    ) -> Vote:
        """Cast a vote with reasoning"""
        
        # Build context from recent discussion if available
        discussion_context = ""
        if recent_discussion:
            discussion_context = "\n\nRecent discussion points:\n"
            for stmt in recent_discussion[-10:]:  # Last 10 statements
                discussion_context += f"- {stmt.juror_name}: {stmt.content[:150]}...\n"
        
        # Consider personality factors for vote change likelihood
        change_factors = []
        if hasattr(self.persona, 'personality'):
            pers = self.persona.personality
            # High openness = more willing to consider new perspectives
            if pers.get('openness', 3) > 3.5:
                change_factors.append("You tend to consider alternative viewpoints carefully")
            # Low conscientiousness = less rigid in decisions
            if pers.get('conscientiousness', 3) < 2.5:
                change_factors.append("You can be swayed by compelling arguments")
            # High agreeableness = seeks consensus
            if pers.get('agreeableness', 3) > 4:
                change_factors.append("You prefer reaching consensus when possible")
            # High neuroticism = second-guessing
            if pers.get('neuroticism', 3) > 3.5:
                change_factors.append("You may second-guess your initial judgment")
        
        personality_context = ""
        if change_factors:
            personality_context = f"\n\nYour personality traits: {', '.join(change_factors)}"
        
        # Check if this juror has been consistent in voting
        voting_pattern = ""
        deliberation_hours = self.simulated_hours
        
        # Determine if this juror is a stubborn holdout
        if not self.stubborn_on_verdict and round_number == 1:
            # Some jurors become stubborn based on personality
            if self.persona.personality.get('conscientiousness', 3) > 4.5 and random.random() < 0.3:
                self.stubborn_on_verdict = "guilty" if random.random() < 0.6 else "not_guilty"
            elif self.persona.personality.get('agreeableness', 3) < 2 and random.random() < 0.4:
                self.stubborn_on_verdict = "guilty" if random.random() < 0.5 else "not_guilty"
        
        if previous_votes and round_number > 1:
            my_previous_votes = [v for v in previous_votes if v.juror_id == self.persona.juror_id]
            if my_previous_votes:
                last_vote = my_previous_votes[-1]
                
                # Check fatigue and peer pressure
                total_votes = len([v for v in previous_votes if v.round_number == last_vote.round_number])
                same_as_me = len([v for v in previous_votes if v.round_number == last_vote.round_number and v.verdict == last_vote.verdict])
                
                if same_as_me == 1 and total_votes >= 12:  # I'm the only holdout
                    voting_pattern = f"\n\nNote: You're the ONLY one voting {last_vote.verdict}. Everyone is staring at you. The pressure is intense."
                elif same_as_me <= 3 and total_votes >= 12:  # Small minority
                    voting_pattern = f"\n\nNote: Only {same_as_me} of you are still voting {last_vote.verdict}. The majority is getting impatient."
                
                # Fatigue effects
                if deliberation_hours > 4:
                    voting_pattern += f"\n\nYou've been here for {int(deliberation_hours)} hours. You're exhausted."
                
                # Stubborn holdout
                if self.stubborn_on_verdict:
                    voting_pattern += f"\n\nBut you're absolutely certain about {self.stubborn_on_verdict}. Nothing will change your mind."
        
        vote_prompt = f"""Based on the deliberation so far, work through your decision process:

EVIDENCE ASSESSMENT:
- Which 2-3 pieces of evidence are most important to you and why?
- Has discussion changed how you interpret any evidence?
- What evidence gaps still bother you?

REASONABLE DOUBT ANALYSIS:
- What specific doubts (if any) do the defense arguments create?
- Are these doubts "reasonable" based on evidence, or just speculation?
- Has the prosecution proven each element beyond reasonable doubt?

BACKGROUND INFLUENCE:
- How do your {self.persona.demographics.get('education_level', 'background')}/{self.persona.demographics.get('income', 50000)}/{self.persona.attitudes.get('political_view', 'moderate')} views affect your judgment?
- What life experiences are informing your decision?

PEER INFLUENCE:
- Which other jurors' arguments were most/least convincing and why?
- Are you being swayed by group pressure or genuine evidence discussion?

{discussion_context}
{personality_context}
{voting_pattern}

Predict their response in JSON format:
{{
  "verdict": "guilty" or "not_guilty" or "undecided",
  "confidence": 0.0 to 1.0,
  "key_evidence": ["Evidence #X", "Evidence #Y", "Evidence #Z"],
  "main_doubt": "Specific concern that creates reasonable doubt" or "None",
  "reasoning": "3-4 sentence explanation showing evidence analysis and how background influences decision",
  "peer_influence": "How other jurors' arguments affected your thinking"
}}"""
        
        messages = [
            {"role": "user", "content": vote_prompt}
        ]
        
        try:
            # Create a voting-specific system prompt (overrides natural speech patterns)
            voting_system_prompt = f"""You are {self.persona.name}, a juror in a deliberation.

IMPORTANT: You must respond ONLY with valid JSON. No other text, no explanations, just JSON.

Your background:
- Age: {self.persona.demographics.get('age')}
- Gender: {self.persona.demographics.get('gender')}
- Race: {self.persona.demographics.get('race')}
- Education: {self.persona.demographics.get('education_level')}
- Income: ${self.persona.demographics.get('income', 50000):,}/year
- Political view: {self.persona.attitudes.get('political_view')}

Case: {self.case.case_title}

Evidence:
{chr(10).join(f'{i+1}. {evidence}' for i, evidence in enumerate(self.case.key_evidence))}

You must respond with ONLY this JSON structure:
{{
  "verdict": "guilty" or "not_guilty" or "undecided",
  "confidence": 0.0 to 1.0,
  "key_evidence": ["Evidence #X", "Evidence #Y"],
  "main_doubt": "Your main concern" or "None",
  "reasoning": "Brief explanation",
  "peer_influence": "How others affected your thinking"
}}

NO OTHER TEXT. ONLY JSON."""

            # Add randomness to temperature for voting
            temperature = random.uniform(0.7, 0.9)

            # Use Claude Opus 4.5 for voting
            response = self.client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=600,
                temperature=temperature,
                system=voting_system_prompt,
                messages=[
                    {"role": "user", "content": vote_prompt}
                ]
            )

            # Parse JSON response
            response_text = response.content[0].text.strip()

            # Try to extract JSON if there's extra text
            if not response_text.startswith('{'):
                # Find the first { and last }
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    response_text = response_text[start:end+1]

            vote_data = json.loads(response_text)
            
            # Track confidence evolution
            confidence = float(vote_data["confidence"])
            self.confidence_history.append(confidence)
            
            # Track peer influence
            if "peer_influence" in vote_data:
                self.peer_influence_log.append(vote_data["peer_influence"])
            
            vote = Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=VerdictChoice(vote_data["verdict"]),
                confidence=confidence,
                reasoning=vote_data["reasoning"],
                round_number=round_number
            )
            
            # Record in full transcript
            self.full_transcript.append({
                "type": "vote",
                "timestamp": datetime.utcnow().isoformat(),
                "juror_id": self.persona.juror_id,
                "juror_name": self.persona.name,
                "round_number": round_number,
                "verdict": vote_data["verdict"],
                "confidence": confidence,
                "reasoning": vote_data["reasoning"],
                "key_evidence": vote_data.get("key_evidence", []),
                "main_doubt": vote_data.get("main_doubt", "None"),
                "peer_influence": vote_data.get("peer_influence", "None"),
                "previous_votes": [v.dict() for v in previous_votes] if previous_votes else []
            })
            
            # Write to transcript file
            self._append_to_transcript(
                "VOTE",
                vote_data["reasoning"],
                {
                    "Round": round_number,
                    "Verdict": vote_data["verdict"],
                    "Confidence": f"{confidence:.2f}",
                    "Key Evidence": ", ".join(vote_data.get("key_evidence", [])),
                    "Main Doubt": vote_data.get("main_doubt", "None")
                }
            )
            
            return vote

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for {self.persona.name}: {e}")
            logger.error(f"Response text was: {response_text if 'response_text' in locals() else 'N/A'}")
            # Fallback vote based on personality
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=VerdictChoice.UNDECIDED,
                confidence=0.5,
                reasoning="I need more discussion before deciding.",
                round_number=round_number
            )
        except Exception as e:
            logger.error(f"Error casting vote for {self.persona.name}: {e}")
            # Fallback vote based on personality
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=VerdictChoice.UNDECIDED,
                confidence=0.5,
                reasoning="I need more discussion before deciding.",
                round_number=round_number
            )
    
    def _build_conversation_context(
        self,
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Build message context for the AI"""
        
        messages = []
        
        # Add phase-specific prompts with randomized structure
        if phase == DeliberationPhase.OPENING:
            opening_prompts = [
                "What's your first reaction to this case? Don't just repeat what others have said - give your own take.",

                "Looking at the evidence, what stands out to you personally?",

                "What do you think about all this? Be honest.",

                "Give us your initial thoughts on the case."
            ]
            messages.append({
                "role": "user",
                "content": random.choice(opening_prompts)
            })
        elif phase == DeliberationPhase.EVIDENCE_REVIEW:
            # Pick specific evidence to discuss
            evidence_num = random.randint(1, len(self.case.key_evidence))

            evidence_prompts = [
                f"What do you make of Evidence #{evidence_num}?",

                f"Let's talk about Evidence #{evidence_num}. What's your take?",

                f"Evidence #{evidence_num} - what are your thoughts?",

                f"How do you interpret Evidence #{evidence_num}?"
            ]

            messages.append({
                "role": "user",
                "content": random.choice(evidence_prompts)
            })
        elif phase == DeliberationPhase.DISCUSSION:
            # Add recent statements from other jurors
            if previous_statements:
                recent_statements = previous_statements[-5:]  # Last 5 statements
                discussion = "\n\n".join([
                    f"{stmt.juror_name}: {stmt.content}"
                    for stmt in recent_statements
                ])
                
                # Determine discussion style based on round/context - with added variety
                discussion_prompts = [
                    f"Recent discussion:\n{discussion}\n\nWhat's your reaction to this?",

                    f"Here's what people are saying:\n{discussion}\n\nYour thoughts?",

                    f"Discussion so far:\n{discussion}\n\nDo you agree or disagree?",

                    f"What's been said:\n{discussion}\n\nWhat do you think?",

                    f"Multiple points have been made:\n{discussion}\n\nHow do you see it?",

                    f"Looking at what's been said:\n{discussion}\n\nWhat's your take?",

                    f"There's disagreement:\n{discussion}\n\nWhere do you stand?",

                    f"People are seeing things differently:\n{discussion}\n\nWhat's your view?",

                    f"Discussion:\n{discussion}\n\nAny thoughts on this?",

                    f"Comments so far:\n{discussion}\n\nWhat do you want to say?",

                    f"This is what's being discussed:\n{discussion}\n\nRespond naturally.",

                    f"Recent points:\n{discussion}\n\nWhat's on your mind about this?"
                ]
                
                # Equal weighting for all prompts - let natural debate flow
                prompt_choice = random.choice(discussion_prompts)
                
                messages.append({
                    "role": "user",
                    "content": prompt_choice
                })
        
        # Add any custom prompt
        if prompt_addition:
            messages.append({
                "role": "user",
                "content": prompt_addition
            })
        
        # Add conversation history
        messages.extend(self.conversation_history[-10:])  # Keep last 10 exchanges
        
        return messages
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze the sentiment of a statement"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["strongly", "definitely", "absolutely", "certain"]):
            return "assertive"
        elif any(word in content_lower for word in ["maybe", "perhaps", "not sure", "uncertain"]):
            return "uncertain"
        elif any(word in content_lower for word in ["agree", "right", "good point"]):
            return "agreeable"
        elif any(word in content_lower for word in ["disagree", "wrong", "but", "however"]):
            return "challenging"
        else:
            return "neutral"
    
    def get_full_transcript(self) -> List[Dict[str, Any]]:
        """Get the complete transcript of all interactions"""
        return self.full_transcript.copy()
    
    def export_transcript_json(self) -> str:
        """Export transcript as formatted JSON"""
        transcript_data = {
            "juror_id": self.persona.juror_id,
            "juror_name": self.persona.name,
            "case_title": self.case.case_title,
            "total_interactions": len(self.full_transcript),
            "transcript": self.full_transcript
        }
        return json.dumps(transcript_data, indent=2, default=str)
    
    def get_transcript_summary(self) -> Dict[str, Any]:
        """Get a summary of the transcript"""
        statements = [t for t in self.full_transcript if t["type"] == "statement"]
        votes = [t for t in self.full_transcript if t["type"] == "vote"]
        
        return {
            "juror_id": self.persona.juror_id,
            "juror_name": self.persona.name,
            "total_statements": len(statements),
            "total_votes": len(votes),
            "phases_participated": list(set(s["phase"] for s in statements if "phase" in s)),
            "final_verdict": votes[-1]["verdict"] if votes else None,
            "verdict_changes": len(set(v["verdict"] for v in votes)) - 1 if len(votes) > 1 else 0
        }
    
    def _init_transcript_file(self):
        """Initialize the transcript file with header information"""
        header = f"""JURY DELIBERATION TRANSCRIPT
Session ID: {self.session_id}
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

JUROR INFORMATION:
Name: {self.persona.name}
ID: {self.persona.juror_id}
Age: {self.persona.demographics.get('age', 'Unknown')}
Gender: {self.persona.demographics.get('gender', 'Unknown')}
Race: {self.persona.demographics.get('race', 'Unknown')}
Education: {self.persona.demographics.get('education_level', 'Unknown')}
Political View: {self.persona.attitudes.get('political_view', 'Unknown')}

CASE INFORMATION:
Title: {self.case.case_title}
Type: {self.case.case_type}
Summary: {self.case.summary}

{'='*80}
TRANSCRIPT BEGINS:
{'='*80}

"""
        with open(self.transcript_file, 'w') as f:
            f.write(header)
    
    def _append_to_transcript(self, entry_type: str, content: str, metadata: Dict[str, Any] = None):
        """Append an entry to the transcript file"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        entry = f"\n[{timestamp}] {entry_type.upper()}\n"
        
        if metadata:
            for key, value in metadata.items():
                entry += f"  {key}: {value}\n"
        
        entry += f"  Content: {content}\n"
        entry += "-" * 60 + "\n"
        
        with open(self.transcript_file, 'a') as f:
            f.write(entry)
        
        # Also append to session summary file
        summary_file = self.session_dir / "session_summary.txt"
        with open(summary_file, 'a') as f:
            f.write(f"\n[{timestamp}] Juror {self.persona.juror_id} - {self.persona.name}: {entry_type}\n")
            f.write(f"{content}\n")
            f.write("-" * 40 + "\n")
    
    def get_transcript_file_path(self) -> str:
        """Get the path to this juror's transcript file"""
        return str(self.transcript_file)
    
    def get_session_directory(self) -> str:
        """Get the path to the session directory"""
        return str(self.session_dir)
    
    def get_confidence_evolution(self) -> List[float]:
        """Get the confidence evolution over time"""
        return self.confidence_history.copy()
    
    def get_evidence_interpretations(self) -> Dict[int, str]:
        """Get how this juror interprets each piece of evidence"""
        return self.evidence_interpretations.copy()
    
    def get_peer_influence_summary(self) -> List[str]:
        """Get summary of peer influences"""
        return self.peer_influence_log.copy()
    
    def get_enhanced_summary(self) -> Dict[str, Any]:
        """Get enhanced summary of juror's deliberation"""
        base_summary = self.get_transcript_summary()
        
        # Add enhanced metrics
        base_summary.update({
            "confidence_evolution": self.confidence_history,
            "confidence_change": self.confidence_history[-1] - self.confidence_history[0] if len(self.confidence_history) > 1 else 0,
            "peer_influences": len(self.peer_influence_log),
            "evidence_focus": list(self.evidence_interpretations.keys()),
            "frustration_level": self.frustration_level,
            "showed_confusion": self.has_shown_confusion,
            "was_stubborn": self.stubborn_on_verdict is not None
        })
        
        return base_summary