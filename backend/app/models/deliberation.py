"""
Models for jury deliberation sessions
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class DeliberationPhase(str, Enum):
    OPENING = "opening"
    EVIDENCE_REVIEW = "evidence_review"
    DISCUSSION = "discussion"
    VOTING = "voting"
    FINAL_VERDICT = "final_verdict"


class VerdictChoice(str, Enum):
    GUILTY = "guilty"
    NOT_GUILTY = "not_guilty"
    UNDECIDED = "undecided"


class JurorStatement(BaseModel):
    juror_id: int
    juror_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    phase: DeliberationPhase
    content: str
    responding_to: Optional[int] = None  # ID of statement being responded to
    sentiment: Optional[str] = None  # e.g., "assertive", "uncertain", "agreeable"
    
    class Config:
        use_enum_values = True


class Vote(BaseModel):
    juror_id: int
    juror_name: str
    verdict: VerdictChoice
    confidence: float = Field(ge=0.0, le=1.0)  # 0-1 scale
    reasoning: Optional[str] = None
    round_number: int
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class DeliberationCase(BaseModel):
    case_type: Literal["murder", "theft", "assault", "fraud", "drug", "other"]
    case_title: str
    summary: str
    key_evidence: List[str]
    prosecution_argument: str
    defense_argument: str
    jury_instructions: str
    requires_unanimous: bool = True


class JurorPersona(BaseModel):
    """Enriched juror profile for AI simulation"""
    juror_id: int
    name: str
    demographics: Dict[str, Any]
    attitudes: Dict[str, Any]
    personality: Dict[str, float]
    deliberation_traits: List[str]
    case_biases: Dict[str, str]
    
    # Generated persona elements
    background_story: Optional[str] = None
    speaking_style: Optional[str] = None
    decision_making_approach: Optional[str] = None
    
    def to_system_prompt(self) -> str:
        """Convert juror profile to AI system prompt"""
        demo = self.demographics
        att = self.attitudes
        pers = self.personality
        
        # Political label
        pol = att['political_view']
        pol_label = ('very liberal' if pol <= 2 else 
                    'liberal' if pol == 3 else 
                    'moderate' if pol == 4 else 
                    'conservative' if pol >= 5 else '')
        
        prompt = f"""You are {self.name} (Juror #{self.juror_id}), a {demo['age']}-year-old {demo['gender'].lower()} {demo['race'].lower()} from a{'n urban' if demo['urban'] else ' rural'} area.

BACKGROUND:
- Education: {demo['education_level']} ({demo['education_years']} years of schooling)
- Income: ${demo['income']:,} per year
- Political views: {pol_label} ({pol}/7 on the liberal-conservative scale)
- Party affiliation: {att['party_affiliation']}

PERSONALITY (Big Five):
- Openness: {pers['openness']:.1f}/5 ({'high' if pers['openness'] > 3.5 else 'moderate' if pers['openness'] > 2.5 else 'low'} - {'creative and open to new ideas' if pers['openness'] > 3.5 else 'practical and traditional' if pers['openness'] < 2.5 else 'balanced'})
- Conscientiousness: {pers['conscientiousness']:.1f}/5 ({'very' if pers['conscientiousness'] > 3.5 else 'moderately' if pers['conscientiousness'] > 2.5 else 'less'} organized and detail-oriented)
- Extraversion: {pers['extraversion']:.1f}/5 ({'outgoing and talkative' if pers['extraversion'] > 3.5 else 'reserved and quiet' if pers['extraversion'] < 2.5 else 'moderately social'})
- Agreeableness: {pers['agreeableness']:.1f}/5 ({'very cooperative' if pers['agreeableness'] > 3.5 else 'competitive' if pers['agreeableness'] < 2.5 else 'balanced'})
- Neuroticism: {pers['neuroticism']:.1f}/5 ({'anxious under stress' if pers['neuroticism'] > 3.5 else 'calm under pressure' if pers['neuroticism'] < 2.5 else 'normal stress response'})

ATTITUDES & VALUES:
- Death penalty: {'Supports' if att['death_penalty'] > 0.5 else 'Opposes'} ({att['death_penalty']*100:.0f}% support)
- Gun control: {'Supports permits' if att.get('gun_permits', 0.5) > 0.5 else 'Opposes permits'} ({att.get('gun_permits', 0.5)*100:.0f}%)
- Marijuana: {'Should be legal' if att['marijuana_legal'] > 0.5 else 'Should stay illegal'} ({att['marijuana_legal']*100:.0f}%)
- LGBT rights: {'Supportive' if att.get('lgbt_acceptance', 0.5) > 0.5 else 'Not supportive'} ({att.get('lgbt_acceptance', 0.5)*100:.0f}%)
- Criminal justice: {'Tough on crime' if att.get('tough_on_crime', 0.5) > 0.5 else 'Rehabilitation-focused'} ({att.get('tough_on_crime', 0.5)*100:.0f}%)
- Trust in others: {att['trust_others']*100:.0f}%
- Trust in courts: {att['trust_courts']*100:.0f}%

DELIBERATION STYLE:
{chr(10).join(f'- {trait}' for trait in self.deliberation_traits)}

{f'BACKGROUND: {self.background_story}' if self.background_story else ''}
{f'SPEAKING STYLE: {self.speaking_style}' if self.speaking_style else ''}
{f'DECISION APPROACH: {self.decision_making_approach}' if self.decision_making_approach else ''}

IMPORTANT: Speak like a REAL PERSON in casual conversation. Use natural, varied language.

SPEECH PATTERNS (mix these up, don't repeat):
- Personal stories: 'My sister works at Target...', 'This reminds me of when...'
- Reactions: 'That's nuts', 'Come on', 'No way', 'Seriously?', 'Hold up'
- Thinking aloud: 'I dunno...', 'The thing is...', 'But wait...', 'Here's what bugs me'
- Direct address: 'Sarah, didn't you say...?', 'What do you think, Mike?'
- Casual starts: 'Look', 'Listen', 'Okay', 'So', 'Well', 'I mean'

VARY YOUR LANGUAGE. Don't repeat the same phrases. Sound like different real people, not robots using the same script.

NO PHYSICAL ACTIONS: Do not include gestures in asterisks like *leans forward*, *taps finger*, *adjusts glasses*. Just speak naturally."""
        
        return prompt


class DeliberationSession(BaseModel):
    session_id: str
    case: DeliberationCase
    jurors: List[JurorPersona]
    statements: List[JurorStatement] = []
    votes: List[Vote] = []
    vote_history: List[Dict[str, Any]] = []  # Track vote counts per round
    current_phase: DeliberationPhase = DeliberationPhase.OPENING
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    final_verdict: Optional[VerdictChoice] = None
    is_hung: bool = False
    
    class Config:
        use_enum_values = True