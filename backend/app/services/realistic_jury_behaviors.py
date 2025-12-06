"""
Realistic jury behaviors and personality-driven responses
"""
from typing import Dict, List, Optional
import random
from app.models.deliberation import JurorPersona

class RealisticJuryBehaviors:
    """Generate authentic, messy human behaviors for jury deliberation"""
    
    @staticmethod
    def get_confusion_responses() -> List[str]:
        """Common confusions about legal concepts"""
        return [
            "Wait, what's reasonable doubt again? Like 51% sure or...?",
            "So beyond reasonable doubt means we have to be 100% certain? That seems impossible.",
            "I'm confused - are we supposed to consider what wasn't presented as evidence?",
            "Hold up, can someone explain again what 'presumed innocent' means if there's all this evidence?",
            "Does unanimous mean we ALL have to agree? What if we can't?",
            "I thought if someone doesn't testify, that means they're guilty?",
            "Are we allowed to talk about the sentence? Like what happens if we convict?",
            "Can we ask to see that evidence again? I forgot what number 7 was."
        ]
    
    @staticmethod
    def get_emotional_reactions() -> Dict[str, List[str]]:
        """Emotional responses based on deliberation stress"""
        return {
            "overwhelmed": [
                "This is too much responsibility. Someone's life is in our hands here.",
                "I can't handle this. What if we're wrong?",
                "I need a break. This is making me sick to my stomach.",
                "I didn't sleep at all last night thinking about this.",
                "My hands are literally shaking. This is so much pressure."
            ],
            "frustrated": [
                "Are we seriously still talking about the same thing?",
                "Oh my God, we've been over this fifty times!",
                "I can't do this anymore. Some of you just aren't listening.",
                "This is ridiculous. How are we still split?",
                "I'm done. You people are impossible."
            ],
            "impatient": [
                "Can we just vote already? I have to pick up my kids.",
                "Look, I've got work tomorrow. How long is this going to take?",
                "We're going in circles here, people.",
                "I've been here for 8 hours. EIGHT HOURS.",
                "My parking meter expired 3 hours ago..."
            ]
        }
    
    @staticmethod
    def get_personality_clashes() -> Dict[str, List[str]]:
        """Different personality types causing friction"""
        return {
            "know_it_all": [
                "Actually, let me explain how DNA evidence really works...",
                "Well, as someone who watches a lot of true crime shows...",
                "You're all missing the obvious here. Let me break it down for you.",
                "No, no, no. That's not how the legal system works. I know because...",
                "I read an article about this exact type of case once..."
            ],
            "quiet_intimidated": [
                "I... um... never mind.",
                "Sorry, I'll just... yeah.",
                "*mumbles something inaudible*",
                "I don't know... whatever you all think...",
                "..."
            ],
            "domineering": [
                "LISTEN! Everyone needs to hear this!",
                "Stop interrupting me! I'm trying to make a point!",
                "Okay, here's what we're going to do...",
                "No, you're wrong. Period. Next topic.",
                "I've made up my mind and nothing you say will change it."
            ],
            "people_pleaser": [
                "Maybe we can find a middle ground?",
                "I don't want to upset anyone, but...",
                "Can't we all just agree on something?",
                "I hate conflict. Can we please stop arguing?",
                "Whatever makes everyone happy, I guess..."
            ]
        }
    
    @staticmethod
    def get_irrelevant_tangents() -> List[str]:
        """Off-topic comments that derail discussion"""
        return [
            "This reminds me of my divorce actually...",
            "You know, my neighbor had something similar happen...",
            "Speaking of blood, I can't stand the sight of it. Makes me queasy.",
            "Anyone else hungry? We've been here since breakfast.",
            "My cousin's a cop and he says... wait, what were we talking about?",
            "I saw a documentary about wrongful convictions once. Scary stuff.",
            "Does anyone else think the defendant looks like that actor from...?",
            "The bathroom here is disgusting, by the way."
        ]
    
    @staticmethod
    def get_fatigue_responses(hours_in: int) -> List[str]:
        """Responses based on deliberation duration"""
        if hours_in < 2:
            return [
                "Let's think this through carefully.",
                "We need to review all the evidence.",
                "Take our time, this is important."
            ]
        elif hours_in < 4:
            return [
                "Okay, we've been at this a while now...",
                "Can we speed this up a bit?",
                "I'm starting to get a headache."
            ]
        elif hours_in < 6:
            return [
                "I need coffee. Or wine. Preferably wine.",
                "My back is killing me from these chairs.",
                "Can we PLEASE just make a decision?"
            ]
        else:
            return [
                "I literally cannot think straight anymore.",
                "Someone else decide. I'm done.",
                "If I have to hear about that glove one more time...",
                "I'll vote whatever just to get out of here."
            ]
    
    @staticmethod
    def get_bias_slips() -> List[str]:
        """Unconscious biases that slip through"""
        return [
            "I mean, look at his lifestyle... that says something.",
            "People from that neighborhood, you know...",
            "Well, statistically speaking, certain groups...",
            "He just looks guilty to me. Call it intuition.",
            "A man like that, with all that money...",
            "I'm not prejudiced, but...",
            "Where there's smoke, there's fire, right?"
        ]
    
    @staticmethod
    def get_authentic_vote_changes() -> Dict[str, List[str]]:
        """Realistic reasons people change their votes"""
        return {
            "peer_pressure": [
                "Fine! If everyone else thinks so... I guess I'll change my vote.",
                "I don't want to be the only holdout. Okay, guilty.",
                "You're all looking at me like I'm crazy. Maybe I am wrong.",
                "I can't fight all 11 of you. I give up."
            ],
            "exhaustion": [
                "I'm too tired to argue anymore. Whatever.",
                "Can we just... okay, fine. Not guilty. Happy now?",
                "My brain is mush. I don't even know what I think anymore.",
                "If I change my vote, can we go home?"
            ],
            "genuine_persuasion": [
                "You know what... that actually makes sense. I hadn't thought of it that way.",
                "Okay, when you put it like that... maybe I was wrong.",
                "That's... huh. That's a good point. Let me reconsider.",
                "I hate to admit it, but you might be right."
            ],
            "emotional": [
                "Looking at those crime scene photos again... I can't let a killer walk free.",
                "Thinking about the victims' families... we owe them justice.",
                "What if it was my daughter? I'd want someone convicted.",
                "I keep seeing those kids without their mom... *starts crying*"
            ]
        }
    
    @staticmethod
    def get_stubborn_holdout_responses() -> List[str]:
        """Responses from jurors who won't budge"""
        return [
            "I don't care what any of you say. Not guilty.",
            "You can talk until you're blue in the face. My mind's made up.",
            "Nope. Nope. Nope. Still not convinced.",
            "I said what I said. Move on.",
            "Been listening for hours. Still think he's innocent.",
            "11 people can be wrong, you know.",
            "I'm not changing my vote just because you want to go home.",
            "My gut says not guilty, and I trust my gut."
        ]
    
    @staticmethod
    def generate_authentic_response(persona: JurorPersona, 
                                  context: str,
                                  deliberation_hours: float) -> Optional[str]:
        """Generate contextually appropriate realistic responses"""
        
        # Personality-based response selection
        pers = persona.personality
        
        # High neuroticism = more emotional/overwhelmed
        if pers.get('neuroticism', 3) > 4 and random.random() < 0.3:
            responses = RealisticJuryBehaviors.get_emotional_reactions()
            return random.choice(responses['overwhelmed'])
        
        # Low agreeableness = more confrontational
        if pers.get('agreeableness', 3) < 2.5 and random.random() < 0.4:
            responses = RealisticJuryBehaviors.get_personality_clashes()
            return random.choice(responses['domineering'])
        
        # Low education = more confusion
        if persona.demographics.get('education_years', 12) < 12 and random.random() < 0.3:
            return random.choice(RealisticJuryBehaviors.get_confusion_responses())
        
        # Fatigue effects everyone
        if deliberation_hours > 4 and random.random() < 0.2:
            return random.choice(RealisticJuryBehaviors.get_fatigue_responses(int(deliberation_hours)))
        
        # Random tangents for some personalities
        if pers.get('openness', 3) > 4 and random.random() < 0.15:
            return random.choice(RealisticJuryBehaviors.get_irrelevant_tangents())
        
        return None