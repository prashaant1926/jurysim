"""
Jury Deliberation Engine - Orchestrates AI juror interactions
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable
import random
from datetime import datetime
import uuid
from app.models.deliberation import (
    DeliberationSession, JurorPersona, JurorStatement, Vote,
    DeliberationPhase, DeliberationCase, VerdictChoice
)
from app.services.ai_juror_agent_deepseek import AIJurorAgentDeepSeek
from app.services.juror_generator import JurorGenerator
import logging

logger = logging.getLogger(__name__)


class DeliberationEngine:
    """Orchestrates jury deliberation with AI agents"""
    
    def __init__(
        self, 
        case: DeliberationCase,
        jurors: List[Dict[str, Any]],
        on_statement: Optional[Callable[[JurorStatement], None]] = None,
        on_vote: Optional[Callable[[List[Vote]], None]] = None
    ):
        self.case = case
        self.on_statement = on_statement  # Callback for UI updates
        self.on_vote = on_vote
        
        # Convert juror dicts to personas with names
        self.juror_personas = self._create_juror_personas(jurors)
        
        # Create AI agents
        self.agents: Dict[int, AIJurorAgentDeepSeek] = {
            persona.juror_id: AIJurorAgentDeepSeek(persona, case)
            for persona in self.juror_personas
        }
        
        # Initialize session
        self.session = DeliberationSession(
            session_id=str(uuid.uuid4()),
            case=case,
            jurors=self.juror_personas,
            current_phase=DeliberationPhase.OPENING
        )
        
        # Track speaking order
        self.speaking_queue: List[int] = []
        self.has_spoken: Dict[int, bool] = {j.juror_id: False for j in self.juror_personas}
        
    def _create_juror_personas(self, jurors: List[Dict[str, Any]]) -> List[JurorPersona]:
        """Convert juror dicts to personas with generated names"""
        first_names = {
            'Male': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 
                    'Richard', 'Joseph', 'Thomas', 'Charles', 'Christopher', 'Daniel'],
            'Female': ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara',
                      'Susan', 'Jessica', 'Sarah', 'Karen', 'Nancy', 'Lisa']
        }
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                     'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez']
        
        personas = []
        used_names = set()
        
        for juror in jurors:
            # Generate unique name
            gender = juror['demographics']['gender']
            first = random.choice(first_names.get(gender, first_names['Male']))
            last = random.choice(last_names)
            name = f"{first} {last}"
            
            # Ensure unique
            while name in used_names:
                first = random.choice(first_names.get(gender, first_names['Male']))
                last = random.choice(last_names)
                name = f"{first} {last}"
            used_names.add(name)
            
            # Create persona
            persona = JurorPersona(
                juror_id=juror['id'],
                name=name,
                demographics=juror['demographics'],
                attitudes=juror['attitudes'],
                personality=juror['personality'],
                deliberation_traits=juror['deliberation_traits'],
                case_biases=juror['case_biases']
            )
            
            # Add background elements based on demographics
            persona.background_story = self._generate_background(juror)
            persona.speaking_style = self._determine_speaking_style(juror)
            persona.decision_making_approach = self._determine_decision_approach(juror)
            
            personas.append(persona)
        
        return personas
    
    def _generate_background(self, juror: Dict[str, Any]) -> str:
        """Generate a brief background story"""
        demo = juror['demographics']
        occupation = self._guess_occupation(demo)
        
        if demo['urban']:
            location = "city"
        else:
            location = "small town"
            
        return f"Works as {occupation} and has lived in the {location} for many years."
    
    def _guess_occupation(self, demographics: Dict[str, Any]) -> str:
        """Guess occupation based on education and income"""
        edu_years = demographics['education_years']
        income = demographics['income']
        
        if edu_years >= 20:
            if income > 150000:
                return random.choice(["a doctor", "a lawyer", "a business executive"])
            else:
                return random.choice(["a professor", "a researcher", "a teacher"])
        elif edu_years >= 16:
            if income > 100000:
                return random.choice(["a manager", "an engineer", "an accountant"])
            else:
                return random.choice(["a teacher", "a nurse", "a social worker"])
        elif edu_years >= 14:
            return random.choice(["a technician", "a salesperson", "an office worker"])
        else:
            return random.choice(["a construction worker", "a retail worker", "a driver"])
    
    def _determine_speaking_style(self, juror: Dict[str, Any]) -> str:
        """Determine speaking style based on personality"""
        pers = juror['personality']
        edu = juror['demographics']['education_years']
        
        styles = []
        
        if pers['extraversion'] > 3.5:
            styles.append("speaks confidently and at length")
        elif pers['extraversion'] < 2.5:
            styles.append("speaks briefly and only when necessary")
        
        if edu >= 18:
            styles.append("uses sophisticated vocabulary")
        elif edu < 12:
            styles.append("uses simple, direct language")
        
        if pers['agreeableness'] > 3.5:
            styles.append("polite and respectful")
        elif pers['agreeableness'] < 2.5:
            styles.append("blunt and direct")
        
        return ", ".join(styles) if styles else "speaks normally"
    
    def _determine_decision_approach(self, juror: Dict[str, Any]) -> str:
        """Determine decision-making approach"""
        pers = juror['personality']
        
        if pers['conscientiousness'] > 3.5:
            return "carefully weighs all evidence"
        elif pers['openness'] > 3.5:
            return "considers alternative interpretations"
        elif pers['neuroticism'] > 3.5:
            return "worries about making the wrong decision"
        else:
            return "relies on gut instinct"
    
    async def run_deliberation(self, max_rounds: int = 5) -> DeliberationSession:
        """Run the complete deliberation process"""
        
        # Phase 1: Opening statements
        await self._run_opening_statements()
        
        # Phase 2: Evidence review
        await self._run_evidence_review()
        
        # Phase 3: Discussion rounds
        for round_num in range(max_rounds):
            await self._run_discussion_round()
            
            # Vote after each round
            await self._run_voting_round(round_num + 1)
            
            # Check if we have a verdict
            if self._check_verdict():
                break
        
        # Final phase
        await self._finalize_deliberation()
        
        return self.session
    
    async def _run_opening_statements(self):
        """Each juror gives opening statement"""
        self.session.current_phase = DeliberationPhase.OPENING
        
        # Random speaking order
        order = list(range(1, len(self.juror_personas) + 1))
        random.shuffle(order)
        
        for juror_id in order:
            agent = self.agents[juror_id]
            statement = await agent.generate_statement(
                DeliberationPhase.OPENING,
                self.session.statements
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            
            # Small delay for realism
            await asyncio.sleep(0.5)
    
    async def _run_evidence_review(self):
        """Jurors discuss evidence"""
        self.session.current_phase = DeliberationPhase.EVIDENCE_REVIEW
        
        # Select 4-6 jurors to speak about evidence
        speakers = random.sample(list(self.agents.keys()), min(6, len(self.agents)))
        
        for juror_id in speakers:
            agent = self.agents[juror_id]
            statement = await agent.generate_statement(
                DeliberationPhase.EVIDENCE_REVIEW,
                self.session.statements
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            
            await asyncio.sleep(0.5)
    
    async def _run_discussion_round(self):
        """Run a discussion round with natural turn-taking"""
        self.session.current_phase = DeliberationPhase.DISCUSSION
        
        # Determine who wants to speak based on personality
        speakers = self._determine_speakers()
        
        for juror_id in speakers:
            agent = self.agents[juror_id]
            
            # Generate response to recent discussion
            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.session.statements[-10:]  # Last 10 statements
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            
            await asyncio.sleep(0.5)
    
    def _determine_speakers(self) -> List[int]:
        """Determine who speaks based on personality"""
        speakers = []
        
        for persona in self.juror_personas:
            # Extraverts more likely to speak
            speak_prob = 0.3 + (persona.personality['extraversion'] - 3) * 0.2
            
            # Leaders always speak
            if any('leader' in trait.lower() for trait in persona.deliberation_traits):
                speak_prob = 0.9
            
            # Adjust for recent speaking
            if persona.juror_id in [s.juror_id for s in self.session.statements[-3:]]:
                speak_prob *= 0.5  # Less likely if just spoke
            
            if random.random() < speak_prob:
                speakers.append(persona.juror_id)
        
        # Ensure at least 2 speakers
        if len(speakers) < 2:
            remaining = [j.juror_id for j in self.juror_personas if j.juror_id not in speakers]
            speakers.extend(random.sample(remaining, min(2, len(remaining))))
        
        # Limit to 5 speakers per round
        return speakers[:5]
    
    async def _run_voting_round(self, round_number: int):
        """Conduct a voting round"""
        self.session.current_phase = DeliberationPhase.VOTING
        
        round_votes = []
        
        # Get previous votes for this round if any
        previous_round_votes = [
            v for v in self.session.votes 
            if v.round_number == round_number - 1
        ] if round_number > 1 else None
        
        # Each juror votes
        for juror_id, agent in self.agents.items():
            vote = await agent.cast_vote(round_number, previous_round_votes)
            round_votes.append(vote)
            self.session.votes.append(vote)
        
        if self.on_vote:
            self.on_vote(round_votes)
        
        # Announce results
        guilty_count = sum(1 for v in round_votes if v.verdict == VerdictChoice.GUILTY)
        not_guilty_count = sum(1 for v in round_votes if v.verdict == VerdictChoice.NOT_GUILTY)
        
        result_statement = JurorStatement(
            juror_id=0,  # System message
            juror_name="Foreperson",
            phase=DeliberationPhase.VOTING,
            content=f"Vote count - Guilty: {guilty_count}, Not Guilty: {not_guilty_count}, Undecided: {12 - guilty_count - not_guilty_count}"
        )
        
        self.session.statements.append(result_statement)
        if self.on_statement:
            self.on_statement(result_statement)
    
    def _check_verdict(self) -> bool:
        """Check if we have reached a verdict"""
        latest_votes = self.session.votes[-12:]  # Last 12 votes (one round)
        
        if len(latest_votes) < 12:
            return False
        
        guilty_count = sum(1 for v in latest_votes if v.verdict == VerdictChoice.GUILTY)
        not_guilty_count = sum(1 for v in latest_votes if v.verdict == VerdictChoice.NOT_GUILTY)
        
        if self.case.requires_unanimous:
            if guilty_count == 12:
                self.session.final_verdict = VerdictChoice.GUILTY
                return True
            elif not_guilty_count == 12:
                self.session.final_verdict = VerdictChoice.NOT_GUILTY
                return True
        else:
            # Simple majority
            if guilty_count > 6:
                self.session.final_verdict = VerdictChoice.GUILTY
                return True
            elif not_guilty_count > 6:
                self.session.final_verdict = VerdictChoice.NOT_GUILTY
                return True
        
        return False
    
    async def _finalize_deliberation(self):
        """Finalize the deliberation"""
        self.session.current_phase = DeliberationPhase.FINAL_VERDICT
        self.session.end_time = datetime.now()
        
        if not self.session.final_verdict:
            self.session.is_hung = True
            
        # Final statement
        if self.session.final_verdict:
            verdict_text = "GUILTY" if self.session.final_verdict == VerdictChoice.GUILTY else "NOT GUILTY"
            final_statement = JurorStatement(
                juror_id=0,
                juror_name="Foreperson",
                phase=DeliberationPhase.FINAL_VERDICT,
                content=f"We the jury find the defendant {verdict_text}."
            )
        else:
            final_statement = JurorStatement(
                juror_id=0,
                juror_name="Foreperson",
                phase=DeliberationPhase.FINAL_VERDICT,
                content="We the jury are unable to reach a unanimous verdict."
            )
        
        self.session.statements.append(final_statement)
        if self.on_statement:
            self.on_statement(final_statement)