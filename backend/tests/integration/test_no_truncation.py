"""
Test that juror statements are not truncated mid-sentence
"""
import asyncio
from app.models.deliberation import DeliberationPhase, DeliberationCase, JurorPersona
from app.services.ai_juror_agent import AIJurorAgent

async def test_no_truncation():
    """Test that responses end properly without truncation"""
    
    # Create test case with many evidence items to encourage longer responses
    case = DeliberationCase(
        case_type="murder",
        case_title="Test Case",
        summary="Complex case with multiple evidence items",
        key_evidence=[
            f"Evidence #{i}: Test evidence item {i}" for i in range(1, 11)
        ],
        prosecution_argument="Multiple evidence items prove guilt",
        defense_argument="Evidence is circumstantial",
        jury_instructions="Consider all evidence",
        requires_unanimous=True
    )
    
    # Create test persona
    persona = JurorPersona(
        juror_id=1,
        name="Test Juror",
        demographics={
            "age": 45,
            "gender": "Female",
            "race": "White",
            "urban": True,
            "education_level": "Graduate degree",
            "education_years": 18,
            "income": 75000
        },
        attitudes={
            "political_view": 4,
            "party_affiliation": "Independent",
            "death_penalty": 0.5,
            "marijuana_legal": 0.6,
            "trust_others": 0.5,
            "trust_courts": 0.4
        },
        personality={
            "extraversion": 4.0,  # High - more talkative
            "agreeableness": 3.5,
            "conscientiousness": 4.5,  # High - detailed
            "openness": 4.0,
            "neuroticism": 2.5
        },
        deliberation_traits=["Vocal participant", "Demands thorough evidence review"],
        case_biases={"initial_lean": "neutral"}
    )
    
    agent = AIJurorAgent(persona, case, "test")
    
    print("Testing statement completeness...\n")
    
    # Test multiple statements
    truncated_count = 0
    
    for i in range(3):
        print(f"\nTest {i+1}:")
        statement = await agent.generate_statement(DeliberationPhase.OPENING, [])
        
        # Check for common truncation indicators
        content = statement.content
        last_char = content.rstrip()[-1] if content.rstrip() else ''
        
        # Check if ends with punctuation
        properly_ended = last_char in '.!?…'
        
        # Check for mid-word cutoff
        words = content.split()
        last_word = words[-1] if words else ''
        mid_word_cutoff = not last_word or (
            last_word[-1] not in '.!?…' and 
            not last_word[0].isupper() and
            len(last_word) > 2
        )
        
        if not properly_ended or mid_word_cutoff:
            truncated_count += 1
            print(f"❌ TRUNCATED: {content[-50:]}")
        else:
            print(f"✓ Complete: {content[-50:]}")
        
        print(f"Length: {len(content.split())} words")
        print(f"Ends with: '{last_char}'")
    
    print(f"\n{'='*60}")
    print(f"Results: {3 - truncated_count}/3 statements ended properly")
    
    if truncated_count == 0:
        print("✓ All statements completed without truncation!")
    else:
        print(f"⚠ {truncated_count} statements were truncated")

if __name__ == "__main__":
    asyncio.run(test_no_truncation())