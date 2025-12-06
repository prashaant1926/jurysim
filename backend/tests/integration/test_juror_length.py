"""
Test if jurors are giving longer, more thoughtful responses
"""
import asyncio
from app.models.deliberation import DeliberationPhase, DeliberationCase, JurorPersona
from app.services.juror_generator import JurorGenerator
from app.services.ai_juror_agent import AIJurorAgent
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine

async def test_juror_response_length():
    """Test a single juror's response length"""
    
    # Create a simple test case
    case = DeliberationCase(
        case_type="murder",
        case_title="Test Case",
        summary="A test case for checking response length",
        key_evidence=[
            "Evidence #1: DNA match with 1 in 170 million probability",
            "Evidence #2: Blood trail from scene to defendant's home",
            "Evidence #3: Witness saw defendant at scene",
            "Evidence #4: Defendant had motive - prior threats",
            "Evidence #5: No alibi for time of crime"
        ],
        prosecution_argument="Evidence proves guilt beyond reasonable doubt",
        defense_argument="Evidence was mishandled and defendant was framed",
        jury_instructions="Consider all evidence carefully",
        requires_unanimous=True
    )
    
    # Generate a single juror
    generator = JurorGenerator()
    jurors = generator.generate_jury_pool("San Francisco", "CA", 1)
    
    if not jurors:
        print("Failed to generate juror")
        return
    
    # Create a minimal ResponsiveDeliberationEngine to get properly formed personas
    engine = ResponsiveDeliberationEngine(case, jurors[:1])
    juror_persona = engine.juror_personas[0]
    
    # Create agent for the juror
    agent = AIJurorAgent(juror_persona, case, "test_session")
    
    print(f"Testing with juror: {juror_persona.name}")
    print(f"Demographics: {juror_persona.demographics['age']}yo {juror_persona.demographics['gender']} {juror_persona.demographics['race']}")
    print("-" * 80)
    
    # Test opening statement
    print("\nOPENING STATEMENT:")
    opening = await agent.generate_statement(DeliberationPhase.OPENING, [])
    print(f"Length: {len(opening.content.split())} words")
    print(f"Content: {opening.content}")
    print("-" * 80)
    
    # Test evidence review
    print("\nEVIDENCE REVIEW:")
    evidence = await agent.generate_statement(DeliberationPhase.EVIDENCE_REVIEW, [])
    print(f"Length: {len(evidence.content.split())} words")
    print(f"Content: {evidence.content}")
    print("-" * 80)
    
    # Test voting
    print("\nVOTING:")
    vote = await agent.cast_vote(1, None)
    print(f"Verdict: {vote.verdict}")
    print(f"Confidence: {vote.confidence}")
    print(f"Reasoning length: {len(vote.reasoning.split())} words")
    print(f"Reasoning: {vote.reasoning}")

if __name__ == "__main__":
    asyncio.run(test_juror_response_length())