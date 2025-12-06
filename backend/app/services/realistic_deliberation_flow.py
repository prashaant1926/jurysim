"""
Realistic Deliberation Flow Manager
"""
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum
from app.models.deliberation import VerdictChoice, DeliberationPhase

class VotingPattern(Enum):
    """Realistic voting pattern types"""
    STEADY_SHIFT = "steady_shift"  # Gradual movement toward consensus
    DEADLOCK = "deadlock"  # Stuck for multiple rounds
    VOLATILE = "volatile"  # Votes swing back and forth
    FACTION_BASED = "faction_based"  # Clear groups that move together
    CASCADE = "cascade"  # Sudden shift when key juror changes
    HOLDOUT = "holdout"  # One or two refuse to budge

class RealisticDeliberationFlow:
    """Manages realistic, non-linear deliberation progression"""
    
    def __init__(self, initial_vote_split: Tuple[int, int, int]):
        """
        initial_vote_split: (guilty, not_guilty, undecided)
        """
        self.guilty_count, self.not_guilty_count, self.undecided_count = initial_vote_split
        self.vote_history = [initial_vote_split]
        self.pattern = self._determine_pattern(initial_vote_split)
        self.rounds_in_deadlock = 0
        self.key_influencers = []  # Juror IDs who can trigger cascades
        self.faction_membership = {}  # juror_id -> faction_name
        
    def _determine_pattern(self, initial_split: Tuple[int, int, int]) -> VotingPattern:
        """Determine likely voting pattern based on initial split"""
        guilty, not_guilty, undecided = initial_split
        total = guilty + not_guilty + undecided
        
        # Close split likely leads to deadlock or volatility
        if abs(guilty - not_guilty) <= 2 and undecided <= 2:
            return random.choice([VotingPattern.DEADLOCK, VotingPattern.VOLATILE])
        
        # Many undecided leads to faction formation
        if undecided >= total * 0.3:
            return VotingPattern.FACTION_BASED
        
        # Strong majority might have holdouts
        if max(guilty, not_guilty) >= total * 0.75:
            return VotingPattern.HOLDOUT if random.random() < 0.4 else VotingPattern.STEADY_SHIFT
        
        # Otherwise cascade or steady
        return random.choice([VotingPattern.CASCADE, VotingPattern.STEADY_SHIFT])
    
    def predict_next_vote(self, 
                         round_number: int,
                         juror_states: Dict[int, any],
                         faction_dynamics: Dict[str, List[int]]) -> Dict[int, VerdictChoice]:
        """Predict how votes will change based on pattern and dynamics"""
        
        predictions = {}
        
        if self.pattern == VotingPattern.DEADLOCK:
            predictions = self._handle_deadlock(round_number, juror_states)
        elif self.pattern == VotingPattern.VOLATILE:
            predictions = self._handle_volatile(round_number, juror_states)
        elif self.pattern == VotingPattern.FACTION_BASED:
            predictions = self._handle_factions(faction_dynamics)
        elif self.pattern == VotingPattern.CASCADE:
            predictions = self._handle_cascade(round_number, juror_states)
        elif self.pattern == VotingPattern.HOLDOUT:
            predictions = self._handle_holdout(round_number)
        else:
            predictions = self._handle_steady_shift(round_number)
        
        return predictions
    
    def _handle_deadlock(self, round_number: int, juror_states: Dict) -> Dict[int, VerdictChoice]:
        """Handle deadlocked jury dynamics"""
        changes = {}
        self.rounds_in_deadlock += 1
        
        # After several rounds, frustration might cause position hardening
        if self.rounds_in_deadlock > 3:
            # Some undecided jurors pick sides out of frustration
            for juror_id, state in juror_states.items():
                if state.frustration_level > 0.7 and random.random() < 0.3:
                    # Frustrated undecided voters pick a side
                    changes[juror_id] = random.choice([VerdictChoice.GUILTY, VerdictChoice.NOT_GUILTY])
        
        # Small chance of breakthrough
        if self.rounds_in_deadlock > 5 and random.random() < 0.2:
            self.pattern = VotingPattern.CASCADE
            self.rounds_in_deadlock = 0
        
        return changes
    
    def _handle_volatile(self, round_number: int, juror_states: Dict) -> Dict[int, VerdictChoice]:
        """Handle volatile voting where positions swing"""
        changes = {}
        
        # 30% of jurors might switch positions
        switching_candidates = random.sample(list(juror_states.keys()), 
                                           k=int(len(juror_states) * 0.3))
        
        for juror_id in switching_candidates:
            if juror_states[juror_id].confidence_level < 0.5:
                # Low confidence jurors more likely to switch
                if random.random() < 0.5:
                    # Switch between guilty and not guilty
                    changes[juror_id] = VerdictChoice.NOT_GUILTY  # This would need current vote info
        
        return changes
    
    def _handle_factions(self, faction_dynamics: Dict[str, List[int]]) -> Dict[int, VerdictChoice]:
        """Handle faction-based movement"""
        changes = {}
        
        # Factions move together
        for faction_name, members in faction_dynamics.items():
            if random.random() < 0.3:  # 30% chance a faction shifts
                # Entire faction moves together
                new_verdict = random.choice([VerdictChoice.GUILTY, VerdictChoice.NOT_GUILTY])
                for member_id in members:
                    changes[member_id] = new_verdict
        
        return changes
    
    def _handle_cascade(self, round_number: int, juror_states: Dict) -> Dict[int, VerdictChoice]:
        """Handle cascade effect when influential juror changes"""
        changes = {}
        
        if round_number > 2 and random.random() < 0.4:
            # Pick a key influencer
            influencer = random.choice([j_id for j_id, state in juror_states.items() 
                                      if state.confidence_level > 0.7])
            
            # Influencer changes position
            new_position = random.choice([VerdictChoice.GUILTY, VerdictChoice.NOT_GUILTY])
            changes[influencer] = new_position
            
            # Others follow
            for juror_id, state in juror_states.items():
                if juror_id != influencer:
                    # Allies very likely to follow
                    if influencer in state.allies:
                        if random.random() < 0.8:
                            changes[juror_id] = new_position
                    # Others might follow based on confidence
                    elif state.confidence_level < 0.5 and random.random() < 0.4:
                        changes[juror_id] = new_position
        
        return changes
    
    def _handle_holdout(self, round_number: int) -> Dict[int, VerdictChoice]:
        """Handle stubborn holdout scenario"""
        changes = {}
        
        # Holdouts rarely change their mind
        if round_number > 5 and random.random() < 0.1:
            # Even holdouts might eventually cave to pressure
            changes["holdout"] = VerdictChoice.GUILTY  # Would need actual holdout ID
        
        return changes
    
    def _handle_steady_shift(self, round_number: int) -> Dict[int, VerdictChoice]:
        """Handle gradual shift toward consensus"""
        changes = {}
        
        # 1-2 jurors change per round toward majority
        num_changes = random.randint(1, 2)
        
        # Determine current majority
        # This would need actual vote counts
        majority_position = VerdictChoice.GUILTY  # Placeholder
        
        # Random jurors shift toward majority
        for _ in range(num_changes):
            changes[random.randint(0, 11)] = majority_position
        
        return changes
    
    def is_consensus_reached(self, current_votes: Dict[int, VerdictChoice]) -> bool:
        """Check if consensus has been reached"""
        vote_counts = {
            VerdictChoice.GUILTY: 0,
            VerdictChoice.NOT_GUILTY: 0,
            VerdictChoice.UNDECIDED: 0
        }
        
        for vote in current_votes.values():
            vote_counts[vote] += 1
        
        # Check for unanimous verdict (or hung jury conditions)
        if vote_counts[VerdictChoice.GUILTY] == len(current_votes):
            return True
        if vote_counts[VerdictChoice.NOT_GUILTY] == len(current_votes):
            return True
        
        # Check for hung jury after many rounds
        if len(self.vote_history) > 10 and self.rounds_in_deadlock > 5:
            return True  # Declared hung
        
        return False
    
    def get_procedural_confusion(self, phase: DeliberationPhase) -> Optional[str]:
        """Generate realistic procedural confusion"""
        confusions = {
            DeliberationPhase.OPENING: [
                "Wait, are we supposed to pick a foreman first?",
                "Can we see the evidence again?",
                "What exactly does 'beyond reasonable doubt' mean legally?"
            ],
            DeliberationPhase.EVIDENCE_REVIEW: [
                "Are we allowed to consider things not presented in court?",
                "Can we request to see specific evidence again?",
                "What if we remember something differently than it was presented?"
            ],
            DeliberationPhase.DISCUSSION: [
                "Do we all have to agree for it to be unanimous?",
                "What happens if we can't reach a verdict?",
                "Can we send questions to the judge?"
            ],
            DeliberationPhase.VOTING: [
                "Do we vote out loud or secret ballot?",
                "Can we change our vote after we say it?",
                "What if someone refuses to vote?"
            ]
        }
        
        if phase in confusions and random.random() < 0.2:
            return random.choice(confusions[phase])
        
        return None
    
    def generate_time_pressure_comment(self, deliberation_hours: float) -> Optional[str]:
        """Generate time-based pressure comments"""
        if deliberation_hours < 2:
            return None
            
        comments = []
        
        if deliberation_hours > 3:
            comments.extend([
                "Look, we've been at this for hours...",
                "I've got to pick up my kids at 5...",
                "How much longer are we going to go in circles?"
            ])
        
        if deliberation_hours > 5:
            comments.extend([
                "I'm too tired to think straight anymore",
                "Can we just take another vote and see where we are?",
                "My parking meter expired 2 hours ago"
            ])
        
        if deliberation_hours > 7:
            comments.extend([
                "This is ridiculous, we're never going to agree",
                "I'm done. I'm not changing my mind.",
                "Judge is going to make us come back tomorrow at this rate"
            ])
        
        if comments and random.random() < 0.3:
            return random.choice(comments)
        
        return None