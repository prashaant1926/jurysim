"""
Responsive Jury Deliberation Engine with dynamic speaking order
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable, Set, Tuple
import random
import re
from datetime import datetime
import uuid
from app.models.deliberation import (
    DeliberationSession, JurorPersona, JurorStatement, Vote,
    DeliberationPhase, DeliberationCase, VerdictChoice
)
from app.services.ai_juror_agent import AIJurorAgent
from app.services.juror_generator import JurorGenerator
from app.services.discussion_tracker import DiscussionTracker
from app.services.transcript_manager import TranscriptManager
import logging

logger = logging.getLogger(__name__)


class ResponsiveDeliberationEngine:
    """Deliberation engine with responsive speaking based on mentions"""
    
    def __init__(
        self,
        case: DeliberationCase,
        jurors: List[Dict[str, Any]],
        county: str = "Unknown",
        state: str = "Unknown",
        on_statement: Optional[Callable[[JurorStatement], None]] = None,
        on_vote: Optional[Callable[[List[Vote]], None]] = None,
        stream_callback_factory: Optional[Callable[[str, int], Callable[[str], None]]] = None
    ):
        self.case = case
        self.county = county
        self.state = state
        self.on_statement = on_statement
        self.on_vote = on_vote
        self.stream_callback_factory = stream_callback_factory
        
        # Convert juror dicts to personas
        self.juror_personas = self._create_juror_personas(jurors)
        
        # Create AI agents
        self.agents: Dict[int, AIJurorAgent] = {}
        
        # Map names to juror IDs for mention detection
        self.name_to_id: Dict[str, int] = {}
        
        # Initialize session
        session_id = str(uuid.uuid4())
        self.session = DeliberationSession(
            session_id=session_id,
            case=case,
            jurors=self.juror_personas,
            current_phase=DeliberationPhase.OPENING
        )
        
        # Initialize transcript manager
        self.transcript_manager = TranscriptManager(
            session_id=session_id,
            case=case,
            jurors=self.juror_personas,
            county=county,
            state=state
        )
        
        # Initialize agents with session ID
        for persona in self.juror_personas:
            self.agents[persona.juror_id] = AIJurorAgent(persona, case, session_id)
            
            # Map various name formats to ID
            full_name = persona.name.lower()
            first_name = persona.name.split()[0].lower()
            last_name = persona.name.split()[-1].lower() if len(persona.name.split()) > 1 else ""
            
            self.name_to_id[full_name] = persona.juror_id
            self.name_to_id[first_name] = persona.juror_id
            if last_name:
                self.name_to_id[last_name] = persona.juror_id
                self.name_to_id[f"mr. {last_name}"] = persona.juror_id
                self.name_to_id[f"ms. {last_name}"] = persona.juror_id
                self.name_to_id[f"mrs. {last_name}"] = persona.juror_id
        
        # Track who has spoken
        self.has_spoken: Set[int] = set()
        self.waiting_to_respond: List[int] = []
        
        # Keep recent statements for context
        self.recent_statements: List[JurorStatement] = []
        
        # Select foreperson
        self.foreperson_id = self._select_foreperson()
        self.foreperson_name = self.agents[self.foreperson_id].persona.name
        
        # Initialize discussion tracker to avoid repetition
        self.discussion_tracker = DiscussionTracker()
        
    def _create_juror_personas(self, jurors: List[Dict[str, Any]]) -> List[JurorPersona]:
        """Create juror personas from raw juror data"""
        personas = []
        generator = JurorGenerator()
        
        # Define name pools locally
        name_pools = {
            'White': {
                'Male': ['John', 'Michael', 'Robert', 'David', 'Christopher', 'Thomas', 'Charles'],
                'Female': ['Sarah', 'Linda', 'Susan', 'Barbara', 'Mary', 'Jennifer']
            },
            'Black': {
                'Male': ['James', 'William', 'Marcus', 'Anthony'],
                'Female': ['Patricia', 'Michelle', 'Angela', 'Donna']
            },
            'Hispanic': {
                'Male': ['Carlos', 'Miguel', 'Juan', 'Luis'],
                'Female': ['Maria', 'Ana', 'Rosa', 'Elena']
            },
            'Asian': {
                'Male': ['David', 'Kevin', 'Steven', 'James'],
                'Female': ['Jennifer', 'Amy', 'Lisa', 'Grace']
            },
            'Other': {
                'Male': ['David', 'Michael', 'Robert'],
                'Female': ['Sarah', 'Mary', 'Linda']
            }
        }
        
        surname_pools = {
            'White': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis'],
            'Black': ['Johnson', 'Williams', 'Brown', 'Jones', 'Davis', 'Wilson'],
            'Hispanic': ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Gonzalez', 'Hernandez'],
            'Asian': ['Lee', 'Chen', 'Kim', 'Wang', 'Patel', 'Nguyen'],
            'Other': ['Smith', 'Johnson', 'Brown']
        }
        
        used_names = set()
        
        for i, juror in enumerate(jurors):
            # Generate unique name
            demo = juror['demographics']
            race = demo.get('race', 'Other')
            gender = demo.get('gender', 'Male')
            
            first_names = name_pools.get(race, name_pools['Other']).get(gender, name_pools['Other']['Male'])
            last_names = surname_pools.get(race, surname_pools['Other'])
            
            # Generate unique name
            attempts = 0
            while attempts < 50:
                first = random.choice(first_names)
                last = random.choice(last_names)
                full_name = f"{first} {last}"
                if full_name not in used_names:
                    used_names.add(full_name)
                    break
                attempts += 1
            
            if attempts >= 50:
                full_name = f"Juror {i+1}"
            
            persona = JurorPersona(
                juror_id=i + 1,
                name=full_name,
                demographics=demo,
                attitudes=juror['attitudes'],
                personality=juror['personality'],
                deliberation_traits=self._determine_deliberation_traits(juror),
                case_biases=self._determine_case_biases(juror),
                background_story=self._generate_background(juror),
                speaking_style=self._determine_speaking_style(juror),
                decision_making_approach=self._determine_decision_approach(juror)
            )
            
            personas.append(persona)
        
        return personas
    
    def _generate_interview_summary(self, juror: Dict[str, Any]) -> str:
        """Generate a summary of the juror's interview"""
        demo = juror['demographics']
        att = juror['attitudes']
        pers = juror['personality']
        
        summary = f"During the interview, this {demo['age']}-year-old {demo['occupation']} "
        
        # Add personality insights
        if pers['extraversion'] > 3.5:
            summary += "spoke confidently and at length about their views. "
        else:
            summary += "was more reserved but thoughtful in their responses. "
        
        # Add relevant attitudes
        if att['law_enforcement_trust'] > 3:
            summary += "They expressed trust in law enforcement. "
        else:
            summary += "They expressed skepticism about law enforcement. "
        
        # Add decision-making style
        if pers['openness'] > 3.5:
            summary += "They indicated they consider multiple perspectives before deciding."
        else:
            summary += "They indicated they rely on established facts and precedent."
        
        return summary
    
    def _determine_deliberation_traits(self, juror: Dict[str, Any]) -> List[str]:
        """Determine how this juror will act in deliberation"""
        traits = []
        pers = juror['personality']
        att = juror['attitudes']
        
        # Leadership traits
        if pers['extraversion'] > 3.5 and pers['conscientiousness'] > 3.5:
            traits.append("Natural leader, organizes discussion")
        elif pers['extraversion'] > 4:
            traits.append("Vocal participant, speaks frequently")
        elif pers['extraversion'] < 2.5:
            traits.append("Quiet observer, speaks when necessary")
        
        # Conflict style
        if pers['agreeableness'] < 2.5:
            traits.append("Confrontational when disagreeing")
        elif pers['agreeableness'] > 4:
            traits.append("Seeks consensus and compromise")
        
        # Decision style
        if pers['conscientiousness'] > 4:
            traits.append("Demands thorough evidence review")
        elif pers['openness'] > 4:
            traits.append("Considers alternative theories")
        
        # Trust in system
        if att.get('trust_courts', 0.5) < 0.3:
            traits.append("Skeptical of prosecution")
        elif att.get('trust_courts', 0.5) > 0.7:
            traits.append("Trusts law enforcement")
        
        return traits
    
    def _determine_case_biases(self, juror: Dict[str, Any]) -> Dict[str, str]:
        """Determine initial leanings based on background"""
        biases = {}
        att = juror['attitudes']
        demo = juror['demographics']
        
        # Political ideology affects crime views
        if att['political_view'] <= 2:  # Very liberal
            biases['initial_lean'] = 'defense'
            biases['reason'] = 'concerned about systemic bias'
        elif att['political_view'] >= 6:  # Conservative
            biases['initial_lean'] = 'prosecution'
            biases['reason'] = 'believes in law and order'
        else:
            biases['initial_lean'] = 'neutral'
            biases['reason'] = 'wants to hear all evidence'
        
        # Personal experience
        if demo.get('income', 50000) < 30000:
            biases['sympathy'] = 'understands economic desperation'
        elif demo.get('income', 50000) > 100000:
            biases['sympathy'] = 'less tolerant of property crime'
        
        return biases
    
    def _generate_background(self, juror: Dict[str, Any]) -> str:
        """Generate relevant background story"""
        demo = juror['demographics']
        
        backgrounds = {
            'retail': "Worked in retail for years, seen shoplifting firsthand",
            'security': "Former security guard, knows how stores operate",
            'teacher': "Educator who believes in second chances",
            'healthcare': "Healthcare worker who's seen all walks of life",
            'business': "Small business owner concerned about theft",
            'student': "College student on a tight budget",
            'unemployed': "Currently between jobs, understands hardship",
            'retired': "Retired, has time to consider all angles"
        }
        
        # Choose based on demographics
        if demo['education_level'] == 'Graduate degree':
            return backgrounds.get('teacher', 'Professional with analytical mindset')
        elif demo['age'] > 65:
            return backgrounds.get('retired')
        elif demo['income'] < 25000:
            return backgrounds.get('unemployed')
        else:
            return random.choice(list(backgrounds.values()))
    
    def _determine_speaking_style(self, juror: Dict[str, Any]) -> str:
        """Determine how they speak"""
        styles = []
        demo = juror['demographics']
        pers = juror['personality']
        
        # Education affects vocabulary
        edu = demo.get('education_years', 12)
        if edu >= 16:
            styles.append("uses professional vocabulary")
        elif edu < 12:
            styles.append("speaks plainly and directly")
        
        # Personality affects delivery
        if pers['extraversion'] > 3.5:
            styles.append("animated and expressive")
        else:
            styles.append("measured and thoughtful")
        
        if pers['agreeableness'] < 2.5:
            styles.append("can be blunt or sarcastic")
        
        # Simple style description
        base_style = ", ".join(styles) if styles else "speaks clearly"
        return base_style
    
    def _determine_decision_approach(self, juror: Dict[str, Any]) -> str:
        """How they approach decisions"""
        pers = juror['personality']
        
        if pers['conscientiousness'] > 4:
            return "methodically analyzes each piece of evidence"
        elif pers['openness'] > 4:
            return "looks for alternative explanations"
        elif pers['neuroticism'] > 3.5:
            return "worries about making wrong decision"
        elif pers['extraversion'] > 4:
            return "trusts gut instinct and speaks mind"
        else:
            return "weighs evidence carefully before deciding"
    
    def _add_statement(self, statement: JurorStatement):
        """Add a statement to the session and transcript"""
        self.session.statements.append(statement)
        self.recent_statements.append(statement)
        
        # Add to transcript
        self.transcript_manager.add_statement(statement)
        
        # Callback
        if self.on_statement:
            self.on_statement(statement)
    
    def _add_votes(self, votes: List[Vote]):
        """Add votes to the session and transcript"""
        for vote in votes:
            self.session.votes.append(vote)
        
        # Add to transcript
        self.transcript_manager.add_voting_round(votes)
        
        # Callback
        if self.on_vote:
            self.on_vote(votes)
    
    def _select_foreperson(self) -> int:
        """Select a foreperson based on personality traits"""
        candidates = []
        
        for persona in self.juror_personas:
            score = 0
            
            # Prefer educated jurors
            if persona.demographics.get('education_years', 12) >= 14:
                score += 2
            
            # Prefer middle-aged (35-55)
            age = persona.demographics.get('age', 40)
            if 35 <= age <= 55:
                score += 2
            elif 25 <= age <= 65:
                score += 1
            
            # Prefer high extraversion and conscientiousness
            if hasattr(persona, 'personality'):
                if persona.personality.get('extraversion', 0) > 3.5:
                    score += 1
                if persona.personality.get('conscientiousness', 0) > 3.5:
                    score += 1
            
            # Avoid extreme political views
            if hasattr(persona, 'attitudes'):
                if 3 <= persona.attitudes.get('political_view', 4) <= 5:
                    score += 1
            
            candidates.append((persona.juror_id, score))
        
        # Sort by score and pick from top 3
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates[:3]
        
        # Random selection from top candidates
        selected = random.choice(top_candidates)[0]
        
        logger.info(f"Selected Juror {selected} ({self.agents[selected].persona.name}) as foreperson")
        return selected
    
    async def _foreperson_statement(self, message: str, phase: DeliberationPhase = None):
        """Have the foreperson make a procedural statement"""
        if phase is None:
            phase = self.session.current_phase
            
        statement = JurorStatement(
            juror_id=self.foreperson_id,
            juror_name=f"{self.foreperson_name} (Foreperson)",
            phase=phase,
            content=message,
            sentiment="neutral"
        )
        
        self._add_statement(statement)
        
        await asyncio.sleep(0.5)
    
    def _detect_mentions(self, statement: str) -> List[int]:
        """Detect which jurors are mentioned in a statement"""
        mentioned_ids = []
        statement_lower = statement.lower()
        
        # Check for direct name mentions
        for name, juror_id in self.name_to_id.items():
            if name in statement_lower:
                if juror_id not in mentioned_ids:
                    mentioned_ids.append(juror_id)
        
        # Check for indirect references
        indirect_patterns = [
            r"what (\w+) said",
            r"agree with (\w+)",
            r"disagree with (\w+)",
            r"(\w+) has a point",
            r"(\w+) mentioned",
            r"like (\w+) said",
            r"(\w+)'s point"
        ]
        
        for pattern in indirect_patterns:
            matches = re.findall(pattern, statement_lower)
            for match in matches:
                if match in self.name_to_id:
                    juror_id = self.name_to_id[match]
                    if juror_id not in mentioned_ids:
                        mentioned_ids.append(juror_id)
        
        return mentioned_ids
    
    async def run_full_deliberation(self, max_rounds: int = 8) -> DeliberationSession:
        """Run complete deliberation with responsive speaking"""
        
        # Announce foreperson selection
        await self._announce_foreperson()
        
        # Phase 1: Opening statements - everyone speaks once, no interruptions
        await self._run_opening_statements()
        
        # Phase 2: Evidence review - focused discussion
        await self._run_evidence_review()
        
        # Phase 3: Discussion with responsive speaking
        for round_num in range(max_rounds):
            await self._run_responsive_discussion(round_num)
            
            # Voting round
            await self._run_voting_round(round_num + 1)
            
            # Check for verdict
            if self._check_verdict():
                break
            
            # Check if we're making progress
            if round_num >= 2 and self._is_deadlocked():
                # Extra push if jury seems stuck
                await self._foreperson_statement(
                    "We seem to be at an impasse. Let me suggest we each identify the ONE piece of evidence that most influences our decision. Then let's discuss those specific points."
                )
            
            # Post-vote persuasion phase
            await self._run_post_vote_persuasion()
            
            # Foreperson summarizes if not final round
            if round_num < max_rounds - 1:
                await self._foreperson_summary()
        
        # Finalize
        self._finalize_deliberation()
        
        return self.session
    
    async def _announce_foreperson(self):
        """Announce the foreperson selection"""
        print(f"\n{'-'*60}")
        print(f"FOREPERSON SELECTED: {self.foreperson_name}")
        print(f"{'-'*60}\n")
        
        # Foreperson introduces themselves and reads jury instructions
        intro_message = f"Hello everyone. I've been selected as foreperson. Before we begin, let me remind everyone of our duties and the rules we must follow."
        
        await self._foreperson_statement(intro_message)
        
        # Read the jury rules
        jury_rules = """As jurors, our goal is to:
1. Decide the facts based solely on evidence presented
2. Apply the law as instructed by the judge
3. Reach a verdict of guilty or not guilty
4. Remain impartial and disregard personal prejudices

The judge has instructed us that:
- The prosecution must prove guilt beyond a reasonable doubt
- The defendant is presumed innocent until proven guilty
- We must consider only the evidence presented in this case
- We should evaluate witness testimony and physical evidence carefully

During our deliberations:
- Keep an open mind until all evidence is considered
- Engage in respectful discussion and consider each other's views
- Work toward a unanimous verdict if possible
- Do not abandon your honest conviction, but be willing to change if compelling reasons are presented
- Avoid repetitive discussions - bring new insights when revisiting evidence

Let's proceed with opening statements where everyone shares their initial thoughts."""
        
        await self._foreperson_statement(jury_rules)
    
    def _increment_all_jurors_time(self, hours: float):
        """Increment simulated time for all jurors"""
        for agent in self.agents.values():
            agent.increment_simulated_time(hours)
    
    async def _run_opening_statements(self):
        """Everyone gives their initial take without interruption"""
        self.session.current_phase = DeliberationPhase.OPENING
        self.transcript_manager.add_phase_marker(DeliberationPhase.OPENING)
        
        # Foreperson opens the floor
        await self._foreperson_statement(
            "Let's begin with opening statements. Each of you will share your initial thoughts on the case. Please keep it brief and focus on your reaction to the evidence."
        )
        
        # Random order for opening statements, but foreperson goes last
        order = [j_id for j_id in self.agents.keys() if j_id != self.foreperson_id]
        random.shuffle(order)
        order.append(self.foreperson_id)  # Foreperson speaks last
        
        for i, juror_id in enumerate(order):
            agent = self.agents[juror_id]
            
            # Foreperson calls on each juror
            if i > 0 and i % 3 == 0 and juror_id != self.foreperson_id:
                await self._foreperson_statement(
                    f"Thank you. Let's hear from {agent.persona.name} next."
                )
            
            # Get guidance for avoiding repetition
            guidance = self.discussion_tracker.get_guidance_for_next_speaker(agent.persona.name)

            # Create stream callback if factory provided
            stream_callback = None
            if self.stream_callback_factory:
                stream_callback = self.stream_callback_factory(agent.persona.name, juror_id)

            # Generate opening statement - no previous statements passed
            statement = await agent.generate_statement(
                DeliberationPhase.OPENING,
                [],  # Empty list ensures no cross-talk
                prompt_addition=f"Give your initial reaction to the evidence. {guidance}" if guidance else "Give your initial reaction to the evidence.",
                stream_callback=stream_callback
            )
            
            self._add_statement(statement)
            
            # Update discussion tracker
            self.discussion_tracker.update_from_statement(agent.persona.name, statement.content)
            
            # Small delay between speakers
            await asyncio.sleep(0.5)
        
        # Foreperson transitions to next phase
        await self._foreperson_statement(
            "Thank you everyone for sharing your initial thoughts. Now let's examine the evidence more closely."
        )
        
        # Opening statements take about 30 minutes
        self._increment_all_jurors_time(0.5)
    
    async def _run_evidence_review(self):
        """Focused evidence discussion"""
        self.session.current_phase = DeliberationPhase.EVIDENCE_REVIEW
        self.transcript_manager.add_phase_marker(DeliberationPhase.EVIDENCE_REVIEW)
        
        # Pick 3-5 jurors to lead evidence discussion
        leaders = random.sample(list(self.agents.keys()), min(5, len(self.agents)))
        
        for juror_id in leaders:
            agent = self.agents[juror_id]
            
            # Get guidance for this speaker
            guidance = self.discussion_tracker.get_guidance_for_next_speaker(agent.persona.name)
            
            # Pass only opening statements for context
            opening_statements = [s for s in self.session.statements 
                               if s.phase == DeliberationPhase.OPENING]
            
            prompt = "Focus on specific evidence that concerns you."
            if guidance:
                prompt += f" {guidance}"

            # Create stream callback if factory provided
            stream_callback = None
            if self.stream_callback_factory:
                stream_callback = self.stream_callback_factory(agent.persona.name, juror_id)

            statement = await agent.generate_statement(
                DeliberationPhase.EVIDENCE_REVIEW,
                opening_statements[-10:],  # Last 10 statements
                prompt_addition=prompt,
                stream_callback=stream_callback
            )
            
            self._add_statement(statement)
            
            # Update tracker
            self.discussion_tracker.update_from_statement(agent.persona.name, statement.content)
            
            await asyncio.sleep(0.5)
        
        # Evidence review takes about 45 minutes
        self._increment_all_jurors_time(0.75)
    
    async def _run_responsive_discussion(self, round_num: int):
        """Discussion phase with responsive speaking based on mentions"""
        self.session.current_phase = DeliberationPhase.DISCUSSION
        self.transcript_manager.add_phase_marker(DeliberationPhase.DISCUSSION)
        
        # Foreperson opens discussion
        discussion_prompts = [
            "Let's discuss what we've heard. Who has concerns about the evidence?",
            "We need to talk through the key issues. What's troubling you about this case?",
            "Let's have an open discussion. Who wants to address the points raised?"
        ]
        await self._foreperson_statement(random.choice(discussion_prompts))
        
        # Reset tracking
        self.has_spoken.clear()
        speakers_this_round = 0
        max_speakers = len(self.agents)
        
        # Foreperson can interject to keep order
        interruption_count = 0
        
        # Start with 2-3 random speakers
        initial_speakers = random.sample(list(self.agents.keys()), min(3, len(self.agents)))
        
        for juror_id in initial_speakers:
            if juror_id not in self.has_spoken:
                await self._have_juror_speak(juror_id)
                speakers_this_round += 1
                self.has_spoken.add(juror_id)
                interruption_count += 1
        
        # Continue with responsive speaking
        while speakers_this_round < max_speakers and (self.waiting_to_respond or len(self.has_spoken) < len(self.agents)):
            # Natural conversation flow - sometimes multiple quick exchanges
            if self.waiting_to_respond and random.random() < 0.7:
                # 70% chance of immediate response when someone is mentioned
                await asyncio.sleep(0.2)  # Quick response
            else:
                await asyncio.sleep(0.5)  # Natural pause
            
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
                    await self._have_juror_speak(next_speaker)
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
                        await self._have_juror_speak(quiet_juror)
                        speakers_this_round += 1
                        self.has_spoken.add(quiet_juror)
                        interruption_count += 1
                    else:
                        next_speaker = random.choice(remaining)
                        await self._have_juror_speak(next_speaker)
                        speakers_this_round += 1
                        self.has_spoken.add(next_speaker)
                        interruption_count += 1
                else:
                    break
        
        # Each discussion round takes about 45 minutes
        self._increment_all_jurors_time(0.75)
    
    async def _have_juror_speak(self, juror_id: int):
        """Have a specific juror speak and detect mentions"""
        agent = self.agents[juror_id]
        
        # Get recent context
        recent_context = self.recent_statements[-10:]
        
        # Get guidance to avoid repetition
        guidance = self.discussion_tracker.get_guidance_for_next_speaker(agent.persona.name)
        
        # Create conversational prompts based on context
        discussion_prompt = None
        
        # Check if this is a direct response to being mentioned
        if juror_id in self.waiting_to_respond:
            # Direct response - keep it short and reactive
            discussion_prompt = "Someone just addressed you directly. Give a quick, natural response in 1-2 sentences."
        elif len(self.recent_statements) > 0 and "?" in self.recent_statements[-1].content:
            # Someone asked a question - answer it
            discussion_prompt = "Answer the question that was just asked. Be direct and conversational, 1-2 sentences."
        elif guidance:
            # General discussion with guidance
            discussion_prompt = f"{guidance} Keep it conversational and brief."
        else:
            # Default conversational prompt
            discussion_prompt = "Jump into the conversation naturally. React, question, or add a quick point. 1-2 sentences max."

        # Create stream callback if factory provided
        stream_callback = None
        if self.stream_callback_factory:
            stream_callback = self.stream_callback_factory(agent.persona.name, juror_id)

        statement = await agent.generate_statement(
            DeliberationPhase.DISCUSSION,
            recent_context,
            prompt_addition=discussion_prompt,
            stream_callback=stream_callback
        )
        
        self._add_statement(statement)
        
        # Update discussion tracker
        self.discussion_tracker.update_from_statement(agent.persona.name, statement.content)
        
        # Detect mentions and add to response queue
        mentioned_ids = self._detect_mentions(statement.content)
        for mentioned_id in mentioned_ids:
            if mentioned_id != juror_id and mentioned_id not in self.has_spoken:
                if mentioned_id not in self.waiting_to_respond:
                    self.waiting_to_respond.append(mentioned_id)
                    print(f"  → {self.agents[mentioned_id].persona.name} was mentioned and will respond next")
        
        await asyncio.sleep(0.5)
    
    async def _run_voting_round(self, round_number: int):
        """Conduct a voting round"""
        self.session.current_phase = DeliberationPhase.VOTING
        self.transcript_manager.add_phase_marker(DeliberationPhase.VOTING)
        
        # Foreperson calls for vote with reminder of standards
        vote_instructions = f"""Let's take a vote. This is round {round_number}. 

Before you vote, remember:
- The defendant is presumed innocent
- Guilt must be proven beyond a reasonable doubt
- Base your decision solely on the evidence presented
- Do not abandon your honest conviction without compelling reason

Please state your verdict clearly."""
        
        await self._foreperson_statement(vote_instructions)
        
        votes = []
        
        # Get recent discussion for context
        recent_discussion = [s for s in self.recent_statements[-20:] 
                           if s.phase == DeliberationPhase.DISCUSSION]
        
        # Collect votes - foreperson manages the process
        vote_order = list(self.agents.keys())
        random.shuffle(vote_order)
        
        for i, juror_id in enumerate(vote_order):
            agent = self.agents[juror_id]
            
            # Foreperson calls on jurors
            if i % 4 == 0 and i > 0:
                await self._foreperson_statement(
                    f"Thank you. {agent.persona.name}, your vote?"
                )
            
            vote = await agent.cast_vote(round_number, self.session.votes, recent_discussion)
            votes.append(vote)
            self.session.votes.append(vote)
        
        # Tally results
        verdict_counts = {}
        for vote in votes:
            verdict = vote.verdict
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        self.session.vote_history.append({
            'round': round_number,
            'counts': verdict_counts,
            'timestamp': datetime.utcnow()
        })
        
        # Foreperson announces results
        guilty = verdict_counts.get(VerdictChoice.GUILTY, 0)
        not_guilty = verdict_counts.get(VerdictChoice.NOT_GUILTY, 0)
        undecided = verdict_counts.get(VerdictChoice.UNDECIDED, 0)
        
        result_message = f"The vote is {guilty} guilty, {not_guilty} not guilty"
        if undecided > 0:
            result_message += f", {undecided} undecided"
        result_message += "."
        
        await self._foreperson_statement(result_message)
        
        # Callback
        if self.on_vote:
            self.on_vote(votes)
        
        # Log results
        logger.info(f"Round {round_number} voting: {verdict_counts}")
        
        # Voting round takes about 15 minutes
        self._increment_all_jurors_time(0.25)
    
    async def _run_post_vote_persuasion(self):
        """After voting, groups try to persuade the other side based on personality"""
        if not self.session.votes:
            return
            
        # Get the most recent votes
        recent_votes = self.session.votes[-len(self.agents):]
        
        # Group jurors by their votes
        guilty_voters = []
        not_guilty_voters = []
        undecided_voters = []
        
        for vote in recent_votes:
            if vote.verdict == VerdictChoice.GUILTY:
                guilty_voters.append(vote.juror_id)
            elif vote.verdict == VerdictChoice.NOT_GUILTY:
                not_guilty_voters.append(vote.juror_id)
            else:
                undecided_voters.append(vote.juror_id)
        
        # Skip if unanimous or no clear groups
        if not guilty_voters or not not_guilty_voters:
            return
            
        # Foreperson acknowledges the split
        await self._foreperson_statement(
            f"We're split {len(guilty_voters)} guilty, {len(not_guilty_voters)} not guilty" +
            (f", {len(undecided_voters)} undecided" if undecided_voters else "") +
            ". Let's hear from both sides. Remember, you should only change your conviction if presented with compelling reasons based on the evidence. No one should abandon an honest conviction they believe is correct."
        )
        
        # Select persuaders based on personality traits
        guilty_persuaders = self._select_persuaders(guilty_voters)
        not_guilty_persuaders = self._select_persuaders(not_guilty_voters)
        
        # Guilty side makes their case
        for juror_id in guilty_persuaders[:2]:  # Limit to 2 speakers
            agent = self.agents[juror_id]
            persona = agent.persona
            
            # Craft persuasion prompt based on personality
            if persona.personality.get('extraversion', 3) > 3.5:
                style = "Make a passionate, direct appeal"
            elif persona.personality.get('conscientiousness', 3) > 3.5:
                style = "Present a methodical, evidence-based argument"
            elif persona.personality.get('agreeableness', 3) > 3.5:
                style = "Appeal to shared values and common ground"
            else:
                style = "Make your case clearly"
            
            prompt = f"{style} for why the defendant is guilty. Address the concerns of those voting not guilty. Reference specific evidence that supports conviction."

            # Create stream callback if factory provided
            stream_callback = None
            if self.stream_callback_factory:
                stream_callback = self.stream_callback_factory(agent.persona.name, juror_id)

            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.recent_statements[-5:],
                prompt_addition=prompt,
                stream_callback=stream_callback
            )
            
            self._add_statement(statement)
            self.discussion_tracker.update_from_statement(agent.persona.name, statement.content)
            
            await asyncio.sleep(0.5)
        
        # Not guilty side responds
        for juror_id in not_guilty_persuaders[:2]:  # Limit to 2 speakers
            agent = self.agents[juror_id]
            persona = agent.persona
            
            # Craft persuasion prompt based on personality
            if persona.personality.get('openness', 3) > 3.5:
                style = "Challenge assumptions and present alternative interpretations"
            elif persona.personality.get('neuroticism', 3) > 3.5:
                style = "Express your deep concerns about convicting"
            elif persona.attitudes.get('trust_courts', 0.5) < 0.3:
                style = "Question the reliability of the evidence and system"
            else:
                style = "Explain the reasonable doubt"
            
            prompt = f"{style} that prevents conviction. Address why the guilty voters should reconsider. Focus on weaknesses in the prosecution's case."

            # Create stream callback if factory provided
            stream_callback = None
            if self.stream_callback_factory:
                stream_callback = self.stream_callback_factory(agent.persona.name, juror_id)

            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.recent_statements[-5:],
                prompt_addition=prompt,
                stream_callback=stream_callback
            )
            
            self._add_statement(statement)
            self.discussion_tracker.update_from_statement(agent.persona.name, statement.content)
            
            await asyncio.sleep(0.5)
        
        # If there are undecided jurors, they ask questions
        if undecided_voters:
            undecided_speaker = random.choice(undecided_voters)
            agent = self.agents[undecided_speaker]
            
            prompt = "You're undecided. Ask specific questions about the evidence or arguments that would help you make a decision. What are your key concerns?"

            # Create stream callback if factory provided
            stream_callback = None
            if self.stream_callback_factory:
                stream_callback = self.stream_callback_factory(agent.persona.name, undecided_speaker)

            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.recent_statements[-5:],
                prompt_addition=prompt,
                stream_callback=stream_callback
            )
            
            self._add_statement(statement)
            self.discussion_tracker.update_from_statement(agent.persona.name, statement.content)
        
        # Persuasion phase takes about 30 minutes
        self._increment_all_jurors_time(0.5)
    
    def _select_persuaders(self, voter_ids: List[int]) -> List[int]:
        """Select the most persuasive jurors from a group based on personality"""
        if not voter_ids:
            return []
            
        # Score each juror's persuasiveness
        persuasion_scores = []
        
        for juror_id in voter_ids:
            persona = self.agents[juror_id].persona
            score = 0
            
            # High extraversion = more likely to speak up
            if persona.personality.get('extraversion', 3) > 3.5:
                score += 2
            
            # High conscientiousness = organized arguments
            if persona.personality.get('conscientiousness', 3) > 3.5:
                score += 1
            
            # Education = articulate
            if persona.demographics.get('education_years', 12) >= 16:
                score += 1
            
            # Leadership traits
            if any('leader' in trait.lower() for trait in persona.deliberation_traits):
                score += 2
            
            persuasion_scores.append((juror_id, score))
        
        # Sort by score and return top persuaders
        persuasion_scores.sort(key=lambda x: x[1], reverse=True)
        return [juror_id for juror_id, _ in persuasion_scores]
    
    async def _foreperson_summary(self):
        """Foreperson summarizes the current state of deliberation"""
        latest_vote = self.session.vote_history[-1]['counts'] if self.session.vote_history else {}
        
        guilty = latest_vote.get(VerdictChoice.GUILTY, 0)
        not_guilty = latest_vote.get(VerdictChoice.NOT_GUILTY, 0)
        
        if guilty > not_guilty:
            lean = "leaning toward guilty"
        elif not_guilty > guilty:
            lean = "leaning toward not guilty"
        else:
            lean = "evenly split"
        
        # More active foreperson guidance based on vote count
        if guilty == not_guilty:
            summary_messages = [
                f"We're evenly split. Those voting guilty - what specific evidence convinces you? Those voting not guilty - what creates reasonable doubt for you?",
                f"We're deadlocked at {guilty}-{not_guilty}. Let's identify our key disagreements. What would it take to change your mind?",
                f"Equal split. Let's try to understand each other's perspectives. What evidence matters most to each side?"
            ]
        elif abs(guilty - not_guilty) <= 2:
            majority = "guilty" if guilty > not_guilty else "not guilty"
            minority = "not guilty" if guilty > not_guilty else "guilty"
            summary_messages = [
                f"We're {lean} with a close {guilty}-{not_guilty} split. Those in the minority - what specific concerns prevent you from joining the majority?",
                f"Close vote at {guilty}-{not_guilty}. Those voting {minority} - explain what evidence creates doubt about the {majority} verdict.",
                f"We're nearly there but not unanimous. Let's address the specific concerns of those still voting {minority}."
            ]
        else:
            majority = "guilty" if guilty > not_guilty else "not guilty"
            minority = "not guilty" if guilty > not_guilty else "guilty"
            summary_messages = [
                f"Strong lean toward {majority} at {guilty}-{not_guilty}. Holdouts - what would need to change for you to reconsider?",
                f"Majority favors {majority}. Let's understand why some still see it differently. Focus on specific evidence.",
                f"We're {lean}. Those in the minority - help us understand your key objections to the majority view."
            ]
        
        await self._foreperson_statement(random.choice(summary_messages))
    
    def _is_deadlocked(self) -> bool:
        """Check if jury appears deadlocked based on voting patterns"""
        if len(self.session.vote_history) < 2:
            return False
        
        # Check if votes haven't changed much in last 2 rounds
        recent_votes = self.session.vote_history[-2:]
        vote_changes = 0
        
        for verdict in [VerdictChoice.GUILTY, VerdictChoice.NOT_GUILTY]:
            count1 = recent_votes[0]['counts'].get(verdict, 0)
            count2 = recent_votes[1]['counts'].get(verdict, 0)
            vote_changes += abs(count2 - count1)
        
        # If less than 2 votes changed, we might be stuck
        return vote_changes < 2
    
    def _check_verdict(self) -> bool:
        """Check if a verdict has been reached"""
        if not self.session.vote_history:
            return False
        
        latest = self.session.vote_history[-1]['counts']
        total_jurors = len(self.agents)
        
        # Check for unanimous verdict
        for verdict, count in latest.items():
            if verdict != VerdictChoice.UNDECIDED and count == total_jurors:
                self.session.final_verdict = verdict
                return True
        
        # Check if we need unanimous verdict
        if not self.case.requires_unanimous:
            # Check for majority
            for verdict, count in latest.items():
                if verdict != VerdictChoice.UNDECIDED and count >= (total_jurors // 2 + 1):
                    self.session.final_verdict = verdict
                    return True
        
        return False
    
    def _finalize_deliberation(self):
        """Finalize the deliberation session"""
        if not self.session.final_verdict:
            # Check if this is truly a hung jury
            rounds_completed = len(self.session.vote_history)
            latest = self.session.vote_history[-1]['counts'] if self.session.vote_history else {}
            
            # Only declare hung jury if we've had substantial deliberation
            if rounds_completed >= 6:  # At least 6 rounds of voting
                self.session.is_hung = True
                logger.info(f"Hung jury after {rounds_completed} rounds. Final vote: {latest}")
            else:
                # Not enough deliberation yet
                logger.info(f"Deliberation ended early after {rounds_completed} rounds. Final vote: {latest}")
        else:
            # Handle both string and enum cases
            verdict_str = self.session.final_verdict if isinstance(self.session.final_verdict, str) else self.session.final_verdict.value
            logger.info(f"Verdict reached: {verdict_str}")
        
        self.session.end_time = datetime.utcnow()
        
        # Add verdict to transcript
        verdict_str = None
        if self.session.final_verdict:
            verdict_str = self.session.final_verdict if isinstance(self.session.final_verdict, str) else self.session.final_verdict.value
        
        # Get the final votes for the transcript
        final_votes = []
        if self.session.votes:
            # Get the last round of votes
            last_round = max(v.round_number for v in self.session.votes)
            final_votes = [v for v in self.session.votes if v.round_number == last_round]
        
        self.transcript_manager.add_verdict(verdict_str, final_votes)
        
        # Save JSON summary
        self.transcript_manager.save_json_summary()