"""Test responsive deliberation engine with foreperson"""
import asyncio
from datetime import datetime
from app.cli.deliberation_interface import SAMPLE_CASES, load_oj_simpson_complete
from app.services.juror_generator import JurorGenerator
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine
from app.models.deliberation import DeliberationPhase, JurorStatement

async def test_deliberation():
    generator = JurorGenerator()
    
    # Test with OJ Simpson case in Oklahoma
    county = "Oklahoma"
    state = "OK"
    case = load_oj_simpson_complete()
    
    print(f"Generating jury for {county}, {state}...")
    jurors = generator.generate_jury_pool(county, state, 12)
    
    print(f"\nGenerated {len(jurors)} jurors")
    
    # Simple callbacks for testing
    def on_statement(statement: JurorStatement):
        if statement.juror_id == 0:  # System/Foreperson announcements
            print(f"\n>>> {statement.content}")
        else:
            print(f"[{statement.juror_name}]: {statement.content[:100]}...")
    
    def on_vote(votes):
        print(f"\nVoting round completed with {len(votes)} votes")
    
    # Create responsive deliberation engine with foreperson
    engine = ResponsiveDeliberationEngine(
        case=case,
        jurors=jurors,
        on_statement=on_statement,
        on_vote=on_vote
    )
    
    print(f"\nSelected foreperson: {engine.foreperson_name}")
    
    # Run deliberation
    try:
        print("\nStarting deliberation with responsive speaking order...")
        session = await engine.run_full_deliberation(max_rounds=1)
        
        if session.final_verdict:
            print(f"\n✓ Deliberation completed. Final verdict: {session.final_verdict.value.upper()}")
        else:
            print(f"\n✗ Hung jury - no unanimous verdict reached")
            
        # Print final vote counts
        if session.vote_history:
            final_vote = session.vote_history[-1]['counts']
            print(f"\nFinal vote breakdown: {final_vote}")
            
    except Exception as e:
        print(f"Error during deliberation: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deliberation())