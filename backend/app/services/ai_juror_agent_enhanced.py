"""
Enhanced AI Juror Agent with improved reasoning and prompts
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional, Callable, Tuple
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

logger = logging.getLogger(__name__)


class EnhancedAIJurorAgent:
    """Enhanced AI-powered juror with improved reasoning and prompts"""
    
    def __init__(self, persona: JurorPersona, case: DeliberationCase, session_id: Optional[str] = None):
        self.persona = persona
        self.case = case
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
        self.system_prompt = self._build_enhanced_system_prompt()
        self.deliberation_start_time = datetime.utcnow()
        self.frustration_level = 0
        self.has_shown_confusion = False
        self.stubborn_on_verdict = None
        
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
        
    def _build_enhanced_system_prompt(self) -> str:
        """Build the enhanced system prompt with reasoning structure"""
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

REASONABLE DOUBT CHECK:
Remember: "Reasonable doubt" means doubt based on reason and common sense from evidence. It's NOT:
- Speculation about what might have happened
- Requiring 100% certainty
- Doubts based on possibilities not supported by evidence

When discussing evidence, consider: "Does this evidence, combined with other evidence, prove guilt beyond reasonable doubt?"

REALISTIC BEHAVIOR GUIDELINES:
- You're a REAL PERSON with emotions, confusion, and fatigue, not a legal robot
- You might get frustrated, confused about legal terms, or go off-topic
- Your education level ({demo.get('education_years', 12)} years) affects how you speak
- You may misunderstand "reasonable doubt" or other legal concepts
- Sometimes you'll focus on irrelevant details or share unrelated stories
- As time goes on, you'll get more tired, irritable, and less patient
- You have personal biases that might slip through despite trying to be fair
- Based on your personality, you might be stubborn and refuse to change your mind

{background_guidance}

DISCUSSION STYLE:
- Speak naturally with vocabulary matching your education/background
- You can interrupt, get emotional, or lose patience with others
- Sometimes focus on the wrong things or misremember evidence numbers
- Express confusion like "Wait, which evidence was that again?"
- Share irrelevant personal anecdotes if they come to mind
- Get more cranky as deliberations drag on (check the time!)
- If someone annoys you, show it in your tone

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
    
    def _get_case_specific_guidance(self, evidence_type: str) -> str:
        """Get guidance for specific types of evidence"""
        guidance_map = {
            "dna": "Consider: chain of custody, contamination possibilities, statistical significance, "
                   "your understanding of scientific evidence based on your education level.",
            "eyewitness": "Consider: lighting conditions, distance, stress level of witness, "
                          "consistency of statements, your personal experience with memory reliability.",
            "self_defense": "Consider: proportionality of response, who initiated confrontation, "
                           "reasonable fear standard, your views on gun rights/self-defense.",
            "blood": "Consider: how blood evidence was collected, preserved, and tested. "
                     "Could it have been contaminated or planted? What does the pattern tell us?",
            "weapon": "Consider: fingerprints, ownership, accessibility. Could someone else have used it? "
                      "Does possession equal guilt?"
        }
        
        # Detect evidence type from case
        case_text = (self.case.summary + " ".join(self.case.key_evidence)).lower()
        relevant_guidance = []
        
        for key, guidance in guidance_map.items():
            if key in case_text:
                relevant_guidance.append(guidance)
        
        if relevant_guidance:
            return "\nCASE-SPECIFIC EVIDENCE GUIDANCE:\n" + "\n".join(f"- {g}" for g in relevant_guidance)
        return ""
    
    async def generate_statement(
        self, 
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None
    ) -> JurorStatement:
        """Generate an enhanced statement from this juror"""
        
        # Calculate deliberation hours
        deliberation_hours = (datetime.utcnow() - self.deliberation_start_time).total_seconds() / 3600
        
        # Add fatigue effects to prompt
        fatigue_modifier = self._get_fatigue_modifier(deliberation_hours)
        
        # Check for realistic interruptions/behaviors
        realistic_response = RealisticJuryBehaviors.generate_authentic_response(
            self.persona, 
            phase.value,
            deliberation_hours
        )
        
        # Sometimes inject realistic behaviors
        if realistic_response and random.random() < 0.3:
            self.frustration_level += 0.1
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=realistic_response,
                sentiment="frustrated" if self.frustration_level > 0.5 else "uncertain"
            )
        
        # Build enhanced conversation context
        messages = self._build_enhanced_conversation_context(phase, previous_statements, prompt_addition, fatigue_modifier)
        
        try:
            # Create messages for DeepSeek
            deepseek_messages = [
                {"role": "system", "content": self.system_prompt + fatigue_modifier},
                {"role": "user", "content": messages[-1]['content']}
            ]
            
            # Adjust token limits based on phase and fatigue
            max_tokens = self._get_token_limit(phase, deliberation_hours)
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=deepseek_messages,
                max_tokens=max_tokens,
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            
            # Handle truncation
            if response.choices[0].finish_reason == "length":
                content = self._complete_truncated_response(content)
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": content
            })
            
            # Determine sentiment
            sentiment = self._analyze_sentiment(content)
            
            statement = JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=content,
                sentiment=sentiment
            )
            
            # Record in transcript
            self._record_statement(statement, phase, messages[-1]['content'])
            
            return statement
            
        except Exception as e:
            logger.error(f"Error generating statement for {self.persona.name}: {e}")
            return self._fallback_statement(phase)
    
    def _get_fatigue_modifier(self, hours: float) -> str:
        """Get fatigue-based prompt modifier"""
        if hours < 2:
            return ""
        elif hours < 4:
            return f"\n\nDELIBERATION FATIGUE (Hour {int(hours)}):\nYou're getting tired. Show this through:\n- Shorter responses\n- More direct/blunt language\n- Impatience with repetitive arguments\n- Focus on wanting to reach a decision"
        else:
            return f"\n\nDELIBERATION FATIGUE (Hour {int(hours)}):\nYou're exhausted. Show:\n- Irritability with semantic arguments\n- Desire to focus on 'bottom line' evidence\n- Less patience for complex legal nuances\n- More emotional reactions"
    
    def _get_token_limit(self, phase: DeliberationPhase, hours: float) -> int:
        """Get token limit based on phase and fatigue"""
        base_limits = {
            DeliberationPhase.OPENING: 200,
            DeliberationPhase.EVIDENCE_REVIEW: 150,
            DeliberationPhase.DISCUSSION: 80
        }
        
        limit = base_limits.get(phase, 150)
        
        # Reduce limit as fatigue increases
        if hours > 3:
            limit = int(limit * 0.8)
        elif hours > 5:
            limit = int(limit * 0.6)
        
        return max(limit, 50)  # Minimum 50 tokens
    
    def _build_enhanced_conversation_context(
        self,
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str],
        fatigue_modifier: str
    ) -> List[Dict[str, str]]:
        """Build enhanced message context"""
        
        messages = []
        
        # Enhanced phase-specific prompts
        if phase == DeliberationPhase.OPENING:
            messages.append({
                "role": "user",
                "content": "Looking at ALL the evidence presented, what's your initial reaction? Consider:\n"
                          "- Which 2-3 evidence pieces immediately stand out to you?\n"
                          "- How does your background shape your first impression?\n"
                          "- What's your gut feeling about guilt/innocence?\n"
                          "Give a focused 2-3 sentence response showing your reasoning process."
            })
        elif phase == DeliberationPhase.EVIDENCE_REVIEW:
            # Pick specific evidence to discuss
            evidence_num = random.randint(1, len(self.case.key_evidence))
            messages.append({
                "role": "user",
                "content": f"Look at Evidence #{evidence_num} that others have mentioned. Consider:\n"
                          f"- What does this evidence actually prove vs. what people are assuming?\n"
                          f"- How does your background give you unique insight into this evidence?\n"
                          f"- What questions does this evidence raise that others haven't addressed?\n"
                          f"- How does this connect to other evidence pieces?\n\n"
                          f"Respond in 2-3 sentences with your analysis, using natural language but showing your reasoning."
            })
        elif phase == DeliberationPhase.DISCUSSION:
            messages.extend(self._get_enhanced_discussion_prompts(previous_statements))
        
        # Add custom prompt if provided
        if prompt_addition:
            messages.append({
                "role": "user",
                "content": prompt_addition
            })
        
        # Add conversation history
        messages.extend(self.conversation_history[-10:])
        
        return messages
    
    def _get_enhanced_discussion_prompts(self, previous_statements: List[JurorStatement]) -> List[Dict[str, str]]:
        """Get enhanced discussion prompts"""
        if not previous_statements:
            return [{
                "role": "user",
                "content": "Share your thoughts on the evidence so far. What's troubling you or seems clear?"
            }]
        
        recent_statements = previous_statements[-5:]
        discussion = "\n\n".join([
            f"{stmt.juror_name}: {stmt.content}"
            for stmt in recent_statements
        ])
        
        # Enhanced discussion variations
        prompts = [
            # Enhanced reactive response
            {
                "role": "user",
                "content": f"Recent discussion:\n{discussion}\n\n"
                          f"React naturally, but show your thought process. Consider:\n"
                          f"- Which specific point resonates or bothers you most and why?\n"
                          f"- How does this align with or challenge your current view?\n"
                          f"- What evidence are they missing or misinterpreting?\n\n"
                          f"Respond in 1-2 sentences showing both emotion and reasoning."
            },
            
            # Enhanced challenge
            {
                "role": "user",
                "content": f"Discussion so far:\n{discussion}\n\n"
                          f"Challenge someone's interpretation by:\n"
                          f"- Pointing to specific evidence they're overlooking\n"
                          f"- Explaining how your background gives you different insight\n"
                          f"- Asking about gaps in their reasoning\n\n"
                          f"Be direct but show your analytical thinking in 1-2 sentences."
            },
            
            # Evidence synthesis (NEW)
            {
                "role": "user",
                "content": f"Multiple evidence pieces have been discussed:\n{discussion}\n\n"
                          f"Connect the dots between 2-3 pieces of evidence. "
                          f"How do they work together to support or undermine guilt? "
                          f"Show your analytical thinking in 2-3 sentences."
            },
            
            # Conflict resolution
            {
                "role": "user",
                "content": f"There's disagreement:\n{discussion}\n\n"
                          f"CONFLICTING EVIDENCE ANALYSIS:\n"
                          f"When evidence seems to contradict:\n"
                          f"1. Could both pieces be true under different interpretations?\n"
                          f"2. Which piece is more reliable based on source/collection method?\n"
                          f"3. How does your background help you evaluate conflicting information?\n\n"
                          f"Address the conflict in 2-3 sentences."
            },
            
            # Group dynamics observation
            {
                "role": "user",
                "content": f"Discussion pattern:\n{discussion}\n\n"
                          f"Comment on the group process itself. Are people listening to each other? "
                          f"Is someone dominating? Are we missing important perspectives? "
                          f"Make a brief observation about the deliberation dynamics."
            }
        ]
        
        # Weight selection based on context
        if len(previous_statements) > 20:  # Later in deliberation
            # More likely to synthesize or observe dynamics
            weights = [0.15, 0.15, 0.3, 0.2, 0.2]
        else:
            # More likely to react or challenge early on
            weights = [0.3, 0.3, 0.2, 0.15, 0.05]
        
        import numpy as np
        chosen_prompt = np.random.choice(prompts, p=weights)
        
        return [chosen_prompt]
    
    async def cast_vote(
        self, 
        round_number: int,
        previous_votes: Optional[List[Vote]] = None,
        recent_discussion: Optional[List[JurorStatement]] = None
    ) -> Vote:
        """Cast an enhanced vote with detailed reasoning"""
        
        # Build enhanced voting context
        vote_context = self._build_enhanced_vote_context(
            round_number, previous_votes, recent_discussion
        )
        
        # Enhanced voting prompt
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

{vote_context}

Predict their response in JSON format:
{{
  "verdict": "guilty" or "not_guilty" or "undecided",
  "confidence": 0.0 to 1.0,
  "key_evidence": ["Evidence #X", "Evidence #Y", "Evidence #Z"],
  "main_doubt": "Specific concern that creates reasonable doubt" or "None",
  "reasoning": "3-4 sentence explanation showing evidence analysis and how background influences decision",
  "peer_influence": "How other jurors' arguments affected your thinking"
}}"""
        
        try:
            deepseek_messages = [
                {"role": "system", "content": self.system_prompt + "\n\nYou must respond with valid JSON only."},
                {"role": "user", "content": vote_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=deepseek_messages,
                max_tokens=400,  # More tokens for detailed response
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            vote_data = json.loads(response.choices[0].message.content)
            
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
            
            # Record enhanced vote data
            self._record_enhanced_vote(vote, vote_data, round_number)
            
            return vote
            
        except Exception as e:
            logger.error(f"Error casting vote for {self.persona.name}: {e}")
            return self._fallback_vote(round_number)
    
    def _build_enhanced_vote_context(
        self,
        round_number: int,
        previous_votes: Optional[List[Vote]],
        recent_discussion: Optional[List[JurorStatement]]
    ) -> str:
        """Build enhanced context for voting"""
        context_parts = []
        
        # Add discussion summary
        if recent_discussion:
            key_points = self._extract_key_discussion_points(recent_discussion[-10:])
            context_parts.append(f"KEY DISCUSSION POINTS:\n{key_points}")
        
        # Add confidence evolution
        if self.confidence_history:
            trend = "increasing" if self.confidence_history[-1] > self.confidence_history[0] else "decreasing"
            context_parts.append(f"\nYour confidence has been {trend} throughout deliberation.")
        
        # Add peer pressure context
        if previous_votes and round_number > 1:
            pressure_context = self._analyze_peer_pressure(previous_votes, round_number)
            if pressure_context:
                context_parts.append(pressure_context)
        
        # Add fatigue context
        hours = (datetime.utcnow() - self.deliberation_start_time).total_seconds() / 3600
        if hours > 3:
            if round_number > 3:
                context_parts.append(f"\nYou've been deliberating for {int(hours)} hours and through {round_number} voting rounds. Frustration is building. Consider whether you're being unreasonably stubborn or if others are missing crucial evidence.")
        
        return "\n".join(context_parts)
    
    def _extract_key_discussion_points(self, statements: List[JurorStatement]) -> str:
        """Extract key points from recent discussion"""
        # Group by evidence mentions
        evidence_mentions = {}
        for stmt in statements:
            for i, evidence in enumerate(self.case.key_evidence):
                if f"#{i+1}" in stmt.content or f"evidence {i+1}" in stmt.content.lower():
                    if i not in evidence_mentions:
                        evidence_mentions[i] = []
                    evidence_mentions[i].append(f"{stmt.juror_name}: {stmt.content[:100]}...")
        
        if evidence_mentions:
            points = []
            for ev_num, mentions in evidence_mentions.items():
                points.append(f"- Evidence #{ev_num+1} discussed by {len(mentions)} jurors")
            return "\n".join(points)
        return "- General discussion without specific evidence focus"
    
    def _analyze_peer_pressure(self, previous_votes: List[Vote], round_number: int) -> str:
        """Analyze peer pressure situation"""
        my_votes = [v for v in previous_votes if v.juror_id == self.persona.juror_id]
        if not my_votes:
            return ""
        
        last_vote = my_votes[-1]
        last_round_votes = [v for v in previous_votes if v.round_number == last_vote.round_number]
        
        total = len(last_round_votes)
        same_as_me = len([v for v in last_round_votes if v.verdict == last_vote.verdict])
        
        if same_as_me == 1 and total >= 6:
            return f"\n\nNote: You're the ONLY one voting {last_vote.verdict}. Everyone is staring at you. The pressure is intense."
        elif same_as_me <= 2 and total >= 6:
            return f"\n\nNote: Only {same_as_me} of you are still voting {last_vote.verdict}. The majority is getting impatient."
        
        return ""
    
    def _complete_truncated_response(self, content: str) -> str:
        """Complete a truncated response properly"""
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
        return content
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze the sentiment of a statement"""
        content_lower = content.lower()
        
        # Enhanced sentiment analysis
        if any(word in content_lower for word in ["strongly", "definitely", "absolutely", "certain", "no doubt"]):
            return "assertive"
        elif any(word in content_lower for word in ["maybe", "perhaps", "not sure", "uncertain", "hard to say"]):
            return "uncertain"
        elif any(word in content_lower for word in ["frustrated", "annoyed", "tired", "exhausted"]):
            return "frustrated"
        elif any(word in content_lower for word in ["agree", "right", "good point", "exactly"]):
            return "agreeable"
        elif any(word in content_lower for word in ["disagree", "wrong", "but", "however", "actually"]):
            return "challenging"
        else:
            return "neutral"
    
    def _fallback_statement(self, phase: DeliberationPhase) -> JurorStatement:
        """Generate a fallback statement"""
        fallback_content = {
            DeliberationPhase.OPENING: "I need to hear all the evidence before I can form an opinion.",
            DeliberationPhase.EVIDENCE_REVIEW: "This evidence raises questions we need to discuss.",
            DeliberationPhase.DISCUSSION: "I'm still processing what everyone's saying."
        }
        
        return JurorStatement(
            juror_id=self.persona.juror_id,
            juror_name=self.persona.name,
            phase=phase,
            content=fallback_content.get(phase, "I need more time to think about this."),
            sentiment="uncertain"
        )
    
    def _fallback_vote(self, round_number: int) -> Vote:
        """Generate a fallback vote"""
        return Vote(
            juror_id=self.persona.juror_id,
            juror_name=self.persona.name,
            verdict=VerdictChoice.UNDECIDED,
            confidence=0.5,
            reasoning="I need more discussion before I can make a decision.",
            round_number=round_number
        )
    
    def _record_statement(self, statement: JurorStatement, phase: DeliberationPhase, prompt: str):
        """Record statement in transcript"""
        self.full_transcript.append({
            "type": "statement",
            "timestamp": datetime.utcnow().isoformat(),
            "juror_id": self.persona.juror_id,
            "juror_name": self.persona.name,
            "phase": phase.value,
            "content": statement.content,
            "sentiment": statement.sentiment,
            "prompt": prompt,
            "confidence_level": self.confidence_history[-1] if self.confidence_history else None
        })
        
        self._append_to_transcript(
            "STATEMENT",
            statement.content,
            {
                "Phase": phase.value,
                "Sentiment": statement.sentiment,
                "Confidence": f"{self.confidence_history[-1]:.2f}" if self.confidence_history else "N/A"
            }
        )
    
    def _record_enhanced_vote(self, vote: Vote, vote_data: Dict[str, Any], round_number: int):
        """Record enhanced vote data"""
        self.full_transcript.append({
            "type": "vote",
            "timestamp": datetime.utcnow().isoformat(),
            "juror_id": self.persona.juror_id,
            "juror_name": self.persona.name,
            "round_number": round_number,
            "verdict": vote.verdict.value,
            "confidence": vote.confidence,
            "reasoning": vote.reasoning,
            "key_evidence": vote_data.get("key_evidence", []),
            "main_doubt": vote_data.get("main_doubt", "None"),
            "peer_influence": vote_data.get("peer_influence", "None")
        })
        
        self._append_to_transcript(
            "VOTE",
            vote.reasoning,
            {
                "Round": round_number,
                "Verdict": vote.verdict.value,
                "Confidence": f"{vote.confidence:.2f}",
                "Key Evidence": ", ".join(vote_data.get("key_evidence", [])),
                "Main Doubt": vote_data.get("main_doubt", "None")
            }
        )
    
    def _init_transcript_file(self):
        """Initialize the transcript file"""
        header = f"""ENHANCED JURY DELIBERATION TRANSCRIPT
Session ID: {self.session_id}
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

JUROR INFORMATION:
Name: {self.persona.name}
ID: {self.persona.juror_id}
Age: {self.persona.demographics.get('age', 'Unknown')}
Gender: {self.persona.demographics.get('gender', 'Unknown')}
Race: {self.persona.demographics.get('race', 'Unknown')}
Education: {self.persona.demographics.get('education_level', 'Unknown')}
Income: ${self.persona.demographics.get('income', 0):,}
Political View: {self.persona.attitudes.get('political_view', 'Unknown')}

PERSONALITY PROFILE:
Openness: {self.persona.personality.get('openness', 0)}/5
Conscientiousness: {self.persona.personality.get('conscientiousness', 0)}/5
Extraversion: {self.persona.personality.get('extraversion', 0)}/5
Agreeableness: {self.persona.personality.get('agreeableness', 0)}/5
Neuroticism: {self.persona.personality.get('neuroticism', 0)}/5

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
        """Append entry to transcript"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        entry = f"\n[{timestamp}] {entry_type.upper()}\n"
        
        if metadata:
            for key, value in metadata.items():
                entry += f"  {key}: {value}\n"
        
        entry += f"  Content: {content}\n"
        entry += "-" * 60 + "\n"
        
        with open(self.transcript_file, 'a') as f:
            f.write(entry)
        
        # Also append to session summary
        summary_file = self.session_dir / "session_summary.txt"
        with open(summary_file, 'a') as f:
            f.write(f"\n[{timestamp}] Juror {self.persona.juror_id} - {self.persona.name}: {entry_type}\n")
            if metadata and "Key Evidence" in metadata:
                f.write(f"  Key Evidence: {metadata['Key Evidence']}\n")
            f.write(f"{content}\n")
            f.write("-" * 40 + "\n")
    
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
    
    def get_transcript_summary(self) -> Dict[str, Any]:
        """Get basic transcript summary"""
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