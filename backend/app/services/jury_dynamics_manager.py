"""
Jury Dynamics Manager - Simulates realistic interpersonal dynamics
"""
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from app.models.deliberation import JurorPersona, DeliberationPhase

class JurorRole(Enum):
    """Archetypal roles that emerge in jury deliberations"""
    LEADER = "leader"  # Takes charge, organizes discussion
    CHALLENGER = "challenger"  # Questions everything, devil's advocate
    PEACEMAKER = "peacemaker"  # Tries to keep harmony
    SILENT_OBSERVER = "silent_observer"  # Rarely speaks until crucial moments
    BULLY = "bully"  # Dominates conversation, dismissive of others
    FENCE_SITTER = "fence_sitter"  # Can't make up their mind
    DETAIL_ORIENTED = "detail_oriented"  # Focuses on evidence minutiae
    EMOTIONAL_APPEALER = "emotional_appealer"  # Makes emotional arguments
    REBEL = "rebel"  # Contrarian, goes against majority
    FOLLOWER = "follower"  # Goes with the flow

@dataclass
class JurorState:
    """Tracks individual juror's emotional and physical state"""
    energy_level: float = 1.0  # 0-1, decreases over time
    frustration_level: float = 0.0  # 0-1, increases with conflict
    confidence_level: float = 0.5  # 0-1, affects how strongly they argue
    hunger_level: float = 0.0  # 0-1, increases over time
    needs_bathroom: bool = False
    times_interrupted: int = 0
    times_spoke: int = 0
    allies: List[int] = None  # Juror IDs they align with
    enemies: List[int] = None  # Juror IDs they clash with
    
    def __post_init__(self):
        if self.allies is None:
            self.allies = []
        if self.enemies is None:
            self.enemies = []

class JuryDynamicsManager:
    """Manages realistic group dynamics in jury deliberations"""
    
    def __init__(self, jurors: List[JurorPersona]):
        self.jurors = jurors
        self.juror_roles: Dict[int, JurorRole] = {}
        self.juror_states: Dict[int, JurorState] = {}
        self.faction_map: Dict[str, List[int]] = {}
        self.deliberation_time = 0  # Minutes
        self.last_break_time = 0
        
        # Initialize roles and states
        self._assign_roles()
        self._initialize_states()
        self._form_initial_factions()
        
    def _assign_roles(self):
        """Assign realistic roles based on personalities"""
        available_roles = list(JurorRole)
        
        for juror in self.jurors:
            # Assign based on personality traits
            if juror.attitudes.leadership_tendency > 7:
                role = JurorRole.LEADER if JurorRole.LEADER in available_roles else JurorRole.CHALLENGER
            elif juror.attitudes.death_penalty and juror.attitudes.political_view > 6:
                role = JurorRole.BULLY if random.random() < 0.3 else JurorRole.CHALLENGER
            elif juror.personality_traits.compassionate > 7:
                role = JurorRole.PEACEMAKER if JurorRole.PEACEMAKER in available_roles else JurorRole.EMOTIONAL_APPEALER
            elif juror.personality_traits.analytical > 8:
                role = JurorRole.DETAIL_ORIENTED
            elif juror.demographics.age < 25:
                role = JurorRole.REBEL if random.random() < 0.4 else JurorRole.FOLLOWER
            elif juror.personality_traits.skeptical < 3:
                role = JurorRole.FOLLOWER
            else:
                # Random assignment from remaining
                role = random.choice([r for r in available_roles if r not in 
                                    [JurorRole.LEADER, JurorRole.BULLY, JurorRole.PEACEMAKER]])
            
            self.juror_roles[juror.juror_id] = role
            
            # Ensure only one leader and bully
            if role in [JurorRole.LEADER, JurorRole.BULLY]:
                available_roles.remove(role)
                
            # Limit silent observers
            if role == JurorRole.SILENT_OBSERVER and sum(1 for r in self.juror_roles.values() 
                                                         if r == JurorRole.SILENT_OBSERVER) >= 2:
                self.juror_roles[juror.juror_id] = JurorRole.FENCE_SITTER
    
    def _initialize_states(self):
        """Initialize emotional and physical states"""
        for juror in self.jurors:
            initial_confidence = 0.7 if self.juror_roles[juror.juror_id] in 
                                      [JurorRole.LEADER, JurorRole.BULLY] else 0.5
            
            if self.juror_roles[juror.juror_id] == JurorRole.SILENT_OBSERVER:
                initial_confidence = 0.3
                
            self.juror_states[juror.juror_id] = JurorState(
                confidence_level=initial_confidence
            )
    
    def _form_initial_factions(self):
        """Form natural alliances and oppositions"""
        # Group by similar backgrounds/views
        for i, juror1 in enumerate(self.jurors):
            for j, juror2 in enumerate(self.jurors[i+1:], i+1):
                # Check for natural alliances
                similarity_score = self._calculate_similarity(juror1, juror2)
                
                if similarity_score > 0.7:
                    self.juror_states[juror1.juror_id].allies.append(juror2.juror_id)
                    self.juror_states[juror2.juror_id].allies.append(juror1.juror_id)
                elif similarity_score < 0.3:
                    # Natural opposition
                    if random.random() < 0.5:  # Not all opposites become enemies
                        self.juror_states[juror1.juror_id].enemies.append(juror2.juror_id)
                        self.juror_states[juror2.juror_id].enemies.append(juror1.juror_id)
    
    def _calculate_similarity(self, juror1: JurorPersona, juror2: JurorPersona) -> float:
        """Calculate how similar two jurors are"""
        factors = []
        
        # Political alignment
        political_diff = abs(juror1.attitudes.political_view - juror2.attitudes.political_view)
        factors.append(1 - (political_diff / 7))
        
        # Education level
        edu_diff = abs(juror1.demographics.education_years - juror2.demographics.education_years)
        factors.append(1 - (edu_diff / 10))
        
        # Age similarity
        age_diff = abs(juror1.demographics.age - juror2.demographics.age)
        factors.append(1 - (age_diff / 50))
        
        # Community type
        if juror1.demographics.community_type == juror2.demographics.community_type:
            factors.append(1.0)
        else:
            factors.append(0.3)
            
        return sum(factors) / len(factors)
    
    def update_dynamics(self, phase: DeliberationPhase, minutes_elapsed: int = 15):
        """Update emotional states and dynamics"""
        self.deliberation_time += minutes_elapsed
        
        for juror_id, state in self.juror_states.items():
            # Fatigue increases over time
            state.energy_level -= (minutes_elapsed / 480)  # 8 hour max
            state.energy_level = max(0.1, state.energy_level)
            
            # Hunger increases
            state.hunger_level += (minutes_elapsed / 240)  # Very hungry after 4 hours
            state.hunger_level = min(1.0, state.hunger_level)
            
            # Bathroom needs
            if self.deliberation_time - self.last_break_time > 90 and random.random() < 0.3:
                state.needs_bathroom = True
            
            # Frustration builds in later phases
            if phase in [DeliberationPhase.DISCUSSION, DeliberationPhase.VOTING]:
                if state.times_interrupted > 2:
                    state.frustration_level += 0.1
                state.frustration_level = min(1.0, state.frustration_level)
    
    def get_emotional_state(self, juror_id: int) -> str:
        """Get current emotional state of juror"""
        state = self.juror_states[juror_id]
        
        if state.frustration_level > 0.7:
            return "angry"
        elif state.frustration_level > 0.5:
            return "frustrated"
        elif state.energy_level < 0.3:
            return "exhausted"
        elif state.hunger_level > 0.7:
            return "irritable"
        elif state.confidence_level > 0.8:
            return "assertive"
        elif state.confidence_level < 0.3:
            return "uncertain"
        else:
            return "neutral"
    
    def should_interrupt(self, speaker_id: int, listener_id: int) -> bool:
        """Determine if listener should interrupt speaker"""
        listener_role = self.juror_roles[listener_id]
        listener_state = self.juror_states[listener_id]
        
        # Bullies interrupt frequently
        if listener_role == JurorRole.BULLY:
            return random.random() < 0.4
        
        # Leaders interrupt to maintain control
        if listener_role == JurorRole.LEADER and listener_state.frustration_level > 0.5:
            return random.random() < 0.3
        
        # Enemies interrupt each other
        if speaker_id in listener_state.enemies:
            return random.random() < 0.35
        
        # Silent observers rarely interrupt
        if listener_role == JurorRole.SILENT_OBSERVER:
            return False
        
        # General interruption based on frustration
        return random.random() < (listener_state.frustration_level * 0.2)
    
    def get_speaking_order(self, phase: DeliberationPhase) -> List[int]:
        """Determine realistic speaking order"""
        order = []
        
        # Leaders and bullies tend to speak first
        priority_speakers = [j_id for j_id, role in self.juror_roles.items() 
                           if role in [JurorRole.LEADER, JurorRole.BULLY]]
        
        # Silent observers speak rarely but at crucial moments
        silent_observers = [j_id for j_id, role in self.juror_roles.items()
                          if role == JurorRole.SILENT_OBSERVER]
        
        # Others
        regular_speakers = [j_id for j_id in self.juror_roles.keys()
                          if j_id not in priority_speakers + silent_observers]
        
        # Build speaking order
        order.extend(random.sample(priority_speakers, len(priority_speakers)))
        
        # Mix in regular speakers
        random.shuffle(regular_speakers)
        order.extend(regular_speakers)
        
        # Silent observers speak occasionally
        for silent_id in silent_observers:
            if phase == DeliberationPhase.VOTING or random.random() < 0.2:
                insert_pos = random.randint(len(order)//2, len(order))
                order.insert(insert_pos, silent_id)
        
        return order
    
    def needs_break(self) -> Tuple[bool, str]:
        """Check if jury needs a break"""
        # Bathroom break
        bathroom_needs = sum(1 for state in self.juror_states.values() if state.needs_bathroom)
        if bathroom_needs >= 2:
            return True, "bathroom"
        
        # Meal break
        avg_hunger = sum(state.hunger_level for state in self.juror_states.values()) / len(self.juror_states)
        if avg_hunger > 0.7:
            return True, "meal"
        
        # Tension break
        avg_frustration = sum(state.frustration_level for state in self.juror_states.values()) / len(self.juror_states)
        if avg_frustration > 0.8:
            return True, "cooling_off"
        
        # Regular break every 2 hours
        if self.deliberation_time - self.last_break_time > 120:
            return True, "scheduled"
        
        return False, ""
    
    def take_break(self, break_type: str):
        """Process effects of taking a break"""
        self.last_break_time = self.deliberation_time
        
        for state in self.juror_states.values():
            if break_type == "bathroom":
                state.needs_bathroom = False
            elif break_type == "meal":
                state.hunger_level = 0
                state.energy_level = min(1.0, state.energy_level + 0.3)
            elif break_type == "cooling_off":
                state.frustration_level *= 0.5
            
            # All breaks provide some energy recovery
            state.energy_level = min(1.0, state.energy_level + 0.1)
    
    def record_interaction(self, speaker_id: int, interrupted: bool = False):
        """Record speaking/interruption events"""
        self.juror_states[speaker_id].times_spoke += 1
        if interrupted:
            self.juror_states[speaker_id].times_interrupted += 1
            self.juror_states[speaker_id].frustration_level += 0.15