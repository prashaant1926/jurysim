"""
Test a single AI agent call to check API response time
"""
import asyncio
import time
from app.models.deliberation import DeliberationCase, DeliberationPhase, JurorPersona
from app.services.ai_juror_agent import AIJurorAgent

async def test_single_agent():
    """Test a single agent response"""
    
    # Create minimal case
    case = DeliberationCase(
        case_type="theft",
        case_title="Test Case",
        summary="Testing API response time",
        key_evidence=["Evidence 1", "Evidence 2"],
        prosecution_argument="Test",
        defense_argument="Test",
        jury_instructions="Test",
        requires_unanimous=True
    )
    
    # Create minimal persona
    persona = JurorPersona(
        juror_id=1,
        name="Test Juror",
        demographics={
            "age": 30, 
            "gender": "Male", 
            "race": "White",
            "urban": True,
            "education_level": "Bachelor's degree",
            "education_years": 16,
            "income": 50000
        },
        attitudes={
            "political_view": 4,
            "party_affiliation": "Independent",
            "death_penalty": 0.5,
            "marijuana_legal": 0.5,
            "trust_others": 0.5,
            "trust_courts": 0.5
        },
        personality={
            "extraversion": 3, 
            "agreeableness": 3, 
            "conscientiousness": 3, 
            "openness": 3, 
            "neuroticism": 3
        },
        deliberation_traits=["Test trait"],
        case_biases={"initial_lean": "neutral"}
    )
    
    # Create agent
    agent = AIJurorAgent(persona, case, "test")
    
    print("Testing AI agent response time...")
    
    # Time the response
    start = time.time()
    try:
        statement = await agent.generate_statement(DeliberationPhase.OPENING, [])
        elapsed = time.time() - start
        
        print(f"\nResponse time: {elapsed:.2f} seconds")
        print(f"Response length: {len(statement.content.split())} words")
        print(f"Response: {statement.content}")
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"\nError after {elapsed:.2f} seconds: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_agent())