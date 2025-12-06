"""
Realistic Speech Pattern Generator for Jury Deliberations
"""
import random
from typing import Dict, List, Tuple
from app.models.deliberation import JurorPersona

class RealisticSpeechGenerator:
    """Generate realistic, imperfect jury speech patterns"""
    
    def __init__(self):
        # Speech fillers and interruptions
        self.fillers = [
            "um", "uh", "well", "I mean", "you know", "like", 
            "basically", "honestly", "look", "listen", "so anyway"
        ]
        
        # Interruption patterns
        self.interruptions = [
            "Wait, hold on—",
            "Can I just—",
            "Sorry, but—",
            "No, no, no, that's not—",
            "Hang on a second—",
            "But what about—",
            "Yeah, but—",
            "OK but seriously—"
        ]
        
        # Emotional reactions - removed physical gestures
        self.frustration_markers = []
        
        # Colloquialisms by region/background
        self.colloquialisms = {
            "urban": ["for real", "straight up", "no cap", "facts", "bet"],
            "rural": ["I reckon", "ain't that something", "bless their heart", "fixin' to"],
            "professional": ["at the end of the day", "bottom line", "let's circle back", "my take is"],
            "blue_collar": ["tell you what", "here's the deal", "no bull", "plain and simple"],
            "academic": ["empirically speaking", "statistically", "logically", "theoretically"]
        }
        
        # Incomplete thoughts
        self.trail_offs = [
            "...", "... whatever", "... I don't know", "... forget it",
            "... you know what I mean?", "... does that make sense?"
        ]
        
        # Agreement/disagreement patterns
        self.agreements = {
            "strong": ["Exactly!", "100%", "That's what I'm saying!", "Thank you!", "Finally, someone gets it"],
            "mild": ["Yeah, maybe", "I guess so", "Could be", "Fair point", "I see where you're coming from"],
            "reluctant": ["I... suppose", "Well... when you put it that way", "OK fine", "Whatever, sure"]
        }
        
        self.disagreements = {
            "polite": ["I hear you, but", "With all due respect", "I see it differently", "That's one way to look at it"],
            "firm": ["No way", "That's not right", "Absolutely not", "I completely disagree", "You're wrong"],
            "hostile": ["Are you serious?", "That's ridiculous", "What are you even talking about?", "That's the dumbest thing I've heard"]
        }
        
    def add_speech_realism(self, content: str, persona: JurorPersona, emotional_state: str = "neutral") -> str:
        """Transform clean text into realistic speech"""
        
        # Determine speech style based on persona
        style = self._determine_speech_style(persona)
        
        # Apply various realistic elements
        content = self._add_fillers(content, style)
        content = self._add_colloquialisms(content, style)
        content = self._add_emotional_markers(content, emotional_state)
        content = self._add_interruptions(content, emotional_state)
        content = self._simplify_vocabulary(content, persona)
        
        # Sometimes trail off
        if random.random() < 0.15:
            content = content.rstrip('.!?') + random.choice(self.trail_offs)
        
        return content
    
    def _determine_speech_style(self, persona: JurorPersona) -> str:
        """Determine speech style based on persona attributes"""
        education = persona.demographics.education_years
        occupation = persona.demographics.occupation.lower()
        
        if education > 16:
            if 'professor' in occupation or 'doctor' in occupation:
                return 'academic'
            else:
                return 'professional'
        elif any(word in occupation for word in ['construction', 'mechanic', 'factory', 'driver']):
            return 'blue_collar'
        elif persona.demographics.community_type == 'rural':
            return 'rural'
        else:
            return 'urban'
    
    def _add_fillers(self, content: str, style: str) -> str:
        """Add um, uh, and other fillers"""
        words = content.split()
        
        # More fillers for less educated/nervous speakers
        filler_rate = 0.1 if style == 'academic' else 0.2
        
        result = []
        for i, word in enumerate(words):
            if random.random() < filler_rate and i > 0:
                result.append(random.choice(self.fillers))
            result.append(word)
        
        return ' '.join(result)
    
    def _add_colloquialisms(self, content: str, style: str) -> str:
        """Replace formal phrases with colloquialisms"""
        if style in self.colloquialisms:
            phrases = self.colloquialisms[style]
            
            # Simple replacements
            replacements = {
                "I believe": random.choice(["I think", "Seems to me", "Way I see it"]),
                "certainly": random.choice(["for sure", "definitely", "totally"]),
                "perhaps": random.choice(["maybe", "could be", "might be"]),
                "evidence suggests": random.choice(["looks like", "seems like", "shows"]),
                "in my opinion": random.choice(["you ask me", "if you ask me", "way I see it"])
            }
            
            for formal, informal in replacements.items():
                if formal in content.lower():
                    content = content.replace(formal, informal)
            
            # Add style-specific phrases
            if random.random() < 0.3:
                content = f"{random.choice(phrases)}, {content}"
        
        return content
    
    def _add_emotional_markers(self, content: str, emotional_state: str) -> str:
        """Add emotional emphasis without physical gestures"""
        # No physical gesture markers - just return content as-is
        return content
    
    def _add_interruptions(self, content: str, emotional_state: str) -> str:
        """Add interruption patterns for heated moments"""
        if emotional_state in ["angry", "defensive", "passionate"]:
            if random.random() < 0.4:
                content = f"{random.choice(self.interruptions)} {content.lower()}"
        return content
    
    def _simplify_vocabulary(self, content: str, persona: JurorPersona) -> str:
        """Replace sophisticated words with simpler alternatives"""
        if persona.demographics.education_years < 14:
            simple_replacements = {
                "utilize": "use",
                "demonstrate": "show",
                "indication": "sign",
                "substantial": "big",
                "insufficient": "not enough",
                "corroborate": "back up",
                "testimony": "what they said",
                "deliberate": "talk about",
                "unanimous": "everyone agrees",
                "reasonable doubt": "not sure enough"
            }
            
            for sophisticated, simple in simple_replacements.items():
                content = content.replace(sophisticated, simple)
        
        return content
    
    def generate_interruption(self, interrupting_persona: JurorPersona, 
                            interrupted_content: str,
                            emotional_state: str = "frustrated") -> Tuple[str, str]:
        """Generate an interruption scenario"""
        
        # Cut off the interrupted speaker mid-sentence
        words = interrupted_content.split()
        cutoff_point = random.randint(len(words)//3, 2*len(words)//3)
        interrupted = ' '.join(words[:cutoff_point]) + "—"
        
        # Generate interrupting statement
        interruption_start = random.choice(self.interruptions)
        
        # What they wanted to say but got cut off
        remaining = ' '.join(words[cutoff_point:])
        
        return interrupted, f"{interruption_start} {remaining}"
    
    def generate_agreement_response(self, persona: JurorPersona, 
                                  agreement_level: str = "mild") -> str:
        """Generate realistic agreement responses"""
        response = random.choice(self.agreements[agreement_level])
        
        # Add personal touch based on style
        style = self._determine_speech_style(persona)
        if style == "blue_collar" and random.random() < 0.5:
            response += " That's common sense right there."
        elif style == "academic" and random.random() < 0.5:
            response += " The logic is sound."
        
        return response
    
    def generate_disagreement_response(self, persona: JurorPersona,
                                     disagreement_level: str = "firm") -> str:
        """Generate realistic disagreement responses"""
        response = random.choice(self.disagreements[disagreement_level])
        
        # Add follow-up based on personality
        if persona.attitudes.political_view < 3:  # Liberal
            if random.random() < 0.3:
                response += " We need to consider the bigger picture here."
        elif persona.attitudes.political_view > 5:  # Conservative  
            if random.random() < 0.3:
                response += " Let's stick to the facts."
                
        return response