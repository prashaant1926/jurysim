"""
Test the fixed ResponsiveDeliberationEngine with foreperson
"""
import asyncio
from app.cli.deliberation_interface import SAMPLE_CASES
from app.services.juror_generator import JurorGenerator
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine
from app.models.deliberation import JurorStatement

async def test_foreperson_deliberation():
    """Test foreperson functionality"""
    generator = JurorGenerator()
    
    # Use theft case for quick test
    case = SAMPLE_CASES["theft"]
    
    # Generate small jury
    print("Generating jury...")
    jurors = generator.generate_jury_pool("Los Angeles", "CA", 6)  # Small jury for quick test
    
    # Simple callbacks
    def on_statement(statement: JurorStatement):
        if statement.juror_id == 0:  # Foreperson
            print(f"\n[FOREPERSON]: {statement.content}")
        else:
            print(f"[{statement.juror_name}]: {statement.content[:80]}...")
    
    def on_vote(votes):
        print(f"\nVoting completed: {len(votes)} votes cast")
    
    # Create engine
    engine = ResponsiveDeliberationEngine(
        case=case,
        jurors=jurors,
        on_statement=on_statement,
        on_vote=on_vote
    )
    
    print(f"\nForeperson selected: {engine.foreperson_name}")
    print("\nStarting deliberation...")
    
    try:
        # Run just 1 round for quick test
        session = await engine.run_full_deliberation(max_rounds=1)
        
        print(f"\nDeliberation complete!")
        if session.final_verdict:
            print(f"Verdict: {session.final_verdict.value.upper()}")
        else:
            print("Hung jury")
            
        # Show vote breakdown
        if session.vote_history:
            final_vote = session.vote_history[-1]['counts']
            print(f"Final vote: {final_vote}")
            
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_foreperson_deliberation())