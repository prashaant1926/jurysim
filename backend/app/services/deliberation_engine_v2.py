"""
Improved Jury Deliberation Engine with realistic dynamics
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable, Tuple
import random
from datetime import datetime
import uuid
from app.models.deliberation import (
    DeliberationSession, JurorPersona, JurorStatement, Vote,
    DeliberationPhase, DeliberationCase, VerdictChoice
)
from app.services.ai_juror_agent_reasoning import AIJurorAgentReasoning
from app.services.juror_generator import JurorGenerator
import logging

logger = logging.getLogger(__name__)


class ImprovedDeliberationEngine:
    """Enhanced deliberation engine with realistic jury dynamics"""
    
    def __init__(
        self, 
        case: DeliberationCase,
        jurors: List[Dict[str, Any]],
        on_statement: Optional[Callable[[JurorStatement], None]] = None,
        on_vote: Optional[Callable[[List[Vote]], None]] = None
    ):
        self.case = case
        self.on_statement = on_statement
        self.on_vote = on_vote
        
        # Convert juror dicts to personas with names
        self.juror_personas = self._create_juror_personas(jurors)
        
        # Create AI agents with reasoning model
        self.agents: Dict[int, AIJurorAgentReasoning] = {
            persona.juror_id: AIJurorAgentReasoning(persona, case)
            for persona in self.juror_personas
        }
        
        # Track voting blocs and dynamics
        self.voting_history: Dict[int, List[VerdictChoice]] = {
            persona.juror_id: [] for persona in self.juror_personas
        }
        
        # Initialize session
        self.session = DeliberationSession(
            session_id=str(uuid.uuid4()),
            case=case,
            jurors=self.juror_personas,
            current_phase=DeliberationPhase.OPENING
        )
        
    def _create_juror_personas(self, jurors: List[Dict[str, Any]]) -> List[JurorPersona]:
        """Create juror personas with distinct characteristics"""
        personas = []
        
        # Names that match demographics better
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
        
        # Common surnames by ethnicity
        surname_pools = {
            'White': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis'],
            'Black': ['Johnson', 'Williams', 'Brown', 'Jones', 'Davis', 'Wilson'],
            'Hispanic': ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Gonzalez', 'Hernandez'],
            'Asian': ['Lee', 'Chen', 'Kim', 'Wang', 'Patel', 'Nguyen'],
            'Other': ['Smith', 'Johnson', 'Brown']
        }
        
        used_names = set()
        
        for i, juror in enumerate(jurors):
            demo = juror['demographics']
            race = demo.get('race', 'Other')
            gender = demo.get('gender', 'Male')
            
            # Get appropriate name pools
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
            
            # Determine personality-based traits
            traits = self._determine_deliberation_traits(juror)
            
            persona = JurorPersona(
                juror_id=i + 1,
                name=full_name,
                demographics=demo,
                attitudes=juror['attitudes'],
                personality=juror['personality'],
                deliberation_traits=traits,
                case_biases=self._determine_case_biases(juror),
                background_story=self._generate_background(juror),
                speaking_style=self._determine_speaking_style(juror),
                decision_making_approach=self._determine_decision_approach(juror)
            )
            
            personas.append(persona)
        
        return personas
    
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
        if att['trust_courts'] < 0.3:
            traits.append("Skeptical of prosecution")
        elif att['trust_courts'] > 0.7:
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
        
        # Add unique speech patterns
        unique_patterns = self._get_speech_patterns(demo, pers)
        
        base_style = ", ".join(styles) if styles else "speaks clearly"
        return f"{base_style}. {unique_patterns}"
    
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
    
    def _get_speech_patterns(self, demo: Dict[str, Any], pers: Dict[str, float]) -> str:
        """Generate unique speech patterns to avoid repetition"""
        age = demo.get('age', 40)
        edu = demo.get('education_years', 12)
        
        patterns = []
        
        # Age-based speech
        if age > 60:
            patterns.append("Uses phrases like 'back in my day', 'now hold on'")
        elif age < 30:
            patterns.append("Uses 'like', 'honestly', 'kinda' frequently")
        else:
            patterns.append("Uses straightforward adult speech")
        
        # Education-based
        if edu >= 16:
            patterns.append("avoids slang, complete sentences")
        elif edu < 12:
            patterns.append("uses 'ain't', 'don't', casual grammar")
        
        # Personality quirks
        if pers['agreeableness'] < 2.5:
            patterns.append("can be blunt: 'that's wrong', 'come on'")
        elif pers['extraversion'] > 4:
            patterns.append("interrupts, speaks enthusiastically")
        elif pers['extraversion'] < 2.5:
            patterns.append("waits turn, speaks briefly")
        
        return ". ".join(patterns[:3])  # Limit to avoid too long descriptions
    
    async def run_deliberation(self, max_rounds: int = 3) -> DeliberationSession:
        """Run improved deliberation with realistic dynamics"""
        
        # Phase 1: Opening statements (everyone speaks)
        await self._run_opening_statements()
        
        # Phase 2: Evidence review (focused discussion)
        await self._run_evidence_review()
        
        # Phase 3: Iterative discussion and voting
        for round_num in range(max_rounds):
            # Discussion with conflict
            await self._run_dynamic_discussion(round_num)
            
            # Vote
            await self._run_voting_round(round_num + 1)
            
            # Check for verdict
            if self._check_verdict():
                break
            
            # If hung after max rounds, do final push
            if round_num == max_rounds - 1:
                await self._run_final_arguments()
        
        # Finalize
        await self._finalize_deliberation()
        
        return self.session
    
    async def _run_opening_statements(self):
        """Everyone gives their initial take"""
        self.session.current_phase = DeliberationPhase.OPENING
        
        # Randomize order
        order = list(self.agents.keys())
        random.shuffle(order)
        
        for juror_id in order:
            agent = self.agents[juror_id]
            statement = await agent.generate_statement(
                DeliberationPhase.OPENING,
                []  # No previous statements for opening
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            
            await asyncio.sleep(0.3)
    
    async def _run_evidence_review(self):
        """Focused evidence discussion"""
        self.session.current_phase = DeliberationPhase.EVIDENCE_REVIEW
        
        # Pick jurors with strong opinions to lead
        leaders = self._identify_leaders()
        others = [j for j in self.agents.keys() if j not in leaders]
        
        # Leaders speak first
        for juror_id in leaders[:3]:
            agent = self.agents[juror_id]
            statement = await agent.generate_statement(
                DeliberationPhase.EVIDENCE_REVIEW,
                self.session.statements[-5:]
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            
            await asyncio.sleep(0.3)
        
        # Others respond
        responders = random.sample(others, min(4, len(others)))
        for juror_id in responders:
            agent = self.agents[juror_id]
            statement = await agent.generate_statement(
                DeliberationPhase.EVIDENCE_REVIEW,
                self.session.statements[-5:]
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            
            await asyncio.sleep(0.3)
    
    async def _run_dynamic_discussion(self, round_num: int):
        """Dynamic discussion with conflicts and alliances"""
        self.session.current_phase = DeliberationPhase.DISCUSSION
        
        # Identify factions based on voting history
        if self.voting_history[1]:  # If we have previous votes
            guilty_bloc = [j for j, votes in self.voting_history.items() 
                          if votes and votes[-1] == VerdictChoice.GUILTY]
            not_guilty_bloc = [j for j, votes in self.voting_history.items() 
                              if votes and votes[-1] == VerdictChoice.NOT_GUILTY]
            undecided = [j for j, votes in self.voting_history.items() 
                        if not votes or votes[-1] == VerdictChoice.UNDECIDED]
            
            # Create targeted discussions
            await self._faction_debate(guilty_bloc, not_guilty_bloc, undecided)
        else:
            # First round - general discussion
            await self._general_discussion()
    
    async def _faction_debate(self, guilty_bloc: List[int], not_guilty_bloc: List[int], undecided: List[int]):
        """Facilitate debate between factions"""
        
        # Pick spokespersons
        if guilty_bloc:
            guilty_speaker = random.choice(guilty_bloc)
            agent = self.agents[guilty_speaker]
            
            # Guilty argument
            prompt = "Make a strong argument for why the defendant is guilty. Address the doubters directly."
            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.session.statements[-5:],
                prompt
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            await asyncio.sleep(0.3)
        
        # Not guilty response
        if not_guilty_bloc:
            not_guilty_speaker = random.choice(not_guilty_bloc)
            agent = self.agents[not_guilty_speaker]
            
            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.session.statements[-5:]
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            await asyncio.sleep(0.3)
        
        # Undecided jurors ask questions
        if undecided:
            questioner = random.choice(undecided)
            agent = self.agents[questioner]
            
            prompt = "You're undecided. Ask pointed questions about the evidence or arguments that concern you."
            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.session.statements[-5:],
                prompt
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            await asyncio.sleep(0.3)
        
        # Additional back-and-forth
        speakers = random.sample(list(self.agents.keys()), min(3, len(self.agents)))
        for juror_id in speakers:
            agent = self.agents[juror_id]
            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.session.statements[-5:]
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            await asyncio.sleep(0.3)
    
    async def _general_discussion(self):
        """General discussion when no clear factions"""
        
        # Pick diverse speakers
        speakers = self._select_diverse_speakers()
        
        for juror_id in speakers:
            agent = self.agents[juror_id]
            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.session.statements[-8:]
            )
            
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
            await asyncio.sleep(0.3)
    
    async def _run_voting_round(self, round_number: int):
        """Conduct realistic voting"""
        self.session.current_phase = DeliberationPhase.VOTING
        
        round_votes = []
        
        # Get previous votes
        prev_votes = [v for v in self.session.votes if v.round_number == round_number - 1] if round_number > 1 else None
        
        # Vote in random order
        order = list(self.agents.keys())
        random.shuffle(order)
        
        for juror_id in order:
            agent = self.agents[juror_id]
            
            try:
                vote = await agent.cast_vote(round_number, prev_votes)
                round_votes.append(vote)
                self.session.votes.append(vote)
                
                # Track voting history
                self.voting_history[juror_id].append(vote.verdict)
                
            except Exception as e:
                logger.error(f"Error casting vote for {agent.persona.name}: {e}")
                # Create fallback vote
                vote = Vote(
                    juror_id=juror_id,
                    juror_name=agent.persona.name,
                    verdict=VerdictChoice.UNDECIDED,
                    confidence=0.5,
                    reasoning="Need more discussion",
                    round_number=round_number
                )
                round_votes.append(vote)
                self.session.votes.append(vote)
        
        # Announce results
        if self.on_vote:
            self.on_vote(round_votes)
        
        # Add foreperson announcement
        guilty_count = sum(1 for v in round_votes if v.verdict == VerdictChoice.GUILTY)
        not_guilty_count = sum(1 for v in round_votes if v.verdict == VerdictChoice.NOT_GUILTY)
        
        announcement = JurorStatement(
            juror_id=0,
            juror_name="Foreperson",
            phase=DeliberationPhase.VOTING,
            content=f"Vote count - Guilty: {guilty_count}, Not Guilty: {not_guilty_count}, Undecided: {12 - guilty_count - not_guilty_count}",
            sentiment="neutral"
        )
        
        self.session.statements.append(announcement)
        if self.on_statement:
            self.on_statement(announcement)
    
    async def _run_final_arguments(self):
        """Last ditch arguments before hung jury"""
        
        # Find the most convinced jurors
        most_guilty = None
        most_not_guilty = None
        
        for juror_id, votes in self.voting_history.items():
            if votes and votes[-1] == VerdictChoice.GUILTY:
                most_guilty = juror_id
            elif votes and votes[-1] == VerdictChoice.NOT_GUILTY:
                most_not_guilty = juror_id
        
        # Final pleas
        if most_guilty:
            agent = self.agents[most_guilty]
            prompt = "Make a final, passionate plea for why the jury must convict. This is your last chance."
            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.session.statements[-5:],
                prompt
            )
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
        
        if most_not_guilty:
            agent = self.agents[most_not_guilty]
            prompt = "Make a final, passionate plea for why there's reasonable doubt. Lives are at stake."
            statement = await agent.generate_statement(
                DeliberationPhase.DISCUSSION,
                self.session.statements[-5:],
                prompt
            )
            self.session.statements.append(statement)
            if self.on_statement:
                self.on_statement(statement)
    
    def _identify_leaders(self) -> List[int]:
        """Identify natural leaders based on traits"""
        leaders = []
        
        for persona in self.juror_personas:
            if any('leader' in trait.lower() for trait in persona.deliberation_traits):
                leaders.append(persona.juror_id)
            elif persona.personality['extraversion'] > 4 and persona.personality['conscientiousness'] > 3.5:
                leaders.append(persona.juror_id)
        
        return leaders
    
    def _select_diverse_speakers(self) -> List[int]:
        """Select speakers with diverse viewpoints"""
        speakers = []
        
        # Get one from each initial bias
        for bias_type in ['prosecution', 'defense', 'neutral']:
            candidates = [p.juror_id for p in self.juror_personas 
                         if p.case_biases.get('initial_lean') == bias_type]
            if candidates:
                speakers.append(random.choice(candidates))
        
        # Add some random others
        remaining = [j for j in self.agents.keys() if j not in speakers]
        if remaining:
            speakers.extend(random.sample(remaining, min(2, len(remaining))))
        
        return speakers[:5]  # Limit to 5
    
    def _check_verdict(self) -> bool:
        """Check if we have unanimous verdict"""
        recent_votes = self.session.votes[-12:]  # Last 12 votes
        
        if len(recent_votes) < 12:
            return False
        
        verdicts = [v.verdict for v in recent_votes]
        
        # Check unanimous guilty
        if all(v == VerdictChoice.GUILTY for v in verdicts):
            self.session.final_verdict = VerdictChoice.GUILTY
            return True
        
        # Check unanimous not guilty
        if all(v == VerdictChoice.NOT_GUILTY for v in verdicts):
            self.session.final_verdict = VerdictChoice.NOT_GUILTY
            return True
        
        return False
    
    async def _finalize_deliberation(self):
        """Finalize the session"""
        self.session.current_phase = DeliberationPhase.FINAL_VERDICT
        self.session.end_time = datetime.now()
        
        if not self.session.final_verdict:
            self.session.is_hung = True