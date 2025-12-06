"""Quick test of improved deliberation with minimal output"""
import asyncio
from app.cli.deliberation_interface import SAMPLE_CASES
from app.services.juror_generator import JurorGenerator
from app.services.deliberation_engine_v2 import ImprovedDeliberationEngine
from app.models.deliberation import VerdictChoice

async def test_quick():
    # Generate jury
    generator = JurorGenerator()
    jurors = generator.generate_jury_pool("San Francisco", "CA", 12)
    
    print(f"Generated {len(jurors)} jurors")
    
    # Create engine
    engine = ImprovedDeliberationEngine(
        case=SAMPLE_CASES["theft"],
        jurors=jurors,
        on_statement=lambda s: print(f"[{s.juror_name}]"),
        on_vote=lambda v: print(f"Vote round complete")
    )
    
    # Run short deliberation
    print("\nStarting deliberation...")
    try:
        session = await engine.run_deliberation(max_rounds=2)
        print(f"\nFinal verdict: {session.final_verdict if session.final_verdict else 'HUNG JURY'}")
        
        # Show final votes
        final_votes = session.votes[-12:] if len(session.votes) >= 12 else []
        if final_votes:
            guilty = sum(1 for v in final_votes if v.verdict == VerdictChoice.GUILTY)
            not_guilty = sum(1 for v in final_votes if v.verdict == VerdictChoice.NOT_GUILTY)
            print(f"Final vote: {guilty} guilty, {not_guilty} not guilty")
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_quick())