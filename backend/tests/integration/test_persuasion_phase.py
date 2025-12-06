"""
Test the post-vote persuasion phase where groups try to convince each other
"""
import asyncio
from app.cli.deliberation_interface import SAMPLE_CASES
from app.services.juror_generator import JurorGenerator
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine
from app.models.deliberation import JurorStatement, DeliberationPhase

async def test_persuasion_phase():
    """Test post-vote persuasion dynamics"""
    generator = JurorGenerator()
    
    # Use a divisive case
    case = SAMPLE_CASES["oj_simpson"]
    
    # Generate diverse jury
    print("Generating diverse jury...")
    jurors = generator.generate_jury_pool("San Francisco", "CA", 8)  # Smaller for quick test
    
    # Track persuasion attempts
    persuasion_statements = []
    vote_counts = []
    
    def track_statement(statement: JurorStatement):
        if statement.juror_id == 0:  # Foreperson
            print(f"\n[FOREPERSON]: {statement.content}")
            if "split" in statement.content.lower():
                print("=" * 60)
                print("POST-VOTE PERSUASION PHASE")
                print("=" * 60)
        else:
            # Check if this is a persuasion statement
            if any(phrase in statement.content.lower() for phrase in 
                   ["guilty voters", "not guilty voters", "reconsider", "conviction", "reasonable doubt"]):
                persuasion_statements.append(statement)
                print(f"\n[PERSUASION - {statement.juror_name}]:")
                print(f"  {statement.content}")
            else:
                print(f"[{statement.juror_name}]: {statement.content[:80]}...")
    
    def track_votes(votes):
        guilty = sum(1 for v in votes if v.verdict.value == "guilty")
        not_guilty = sum(1 for v in votes if v.verdict.value == "not_guilty")
        undecided = sum(1 for v in votes if v.verdict.value == "undecided")
        
        vote_counts.append({
            'guilty': guilty,
            'not_guilty': not_guilty,
            'undecided': undecided
        })
        
        print(f"\nVOTE: {guilty} guilty, {not_guilty} not guilty, {undecided} undecided")
    
    # Create engine
    engine = ResponsiveDeliberationEngine(
        case=case,
        jurors=jurors,
        on_statement=track_statement,
        on_vote=track_votes
    )
    
    print(f"\nForeperson: {engine.foreperson_name}")
    print("\nRunning deliberation to see persuasion phase...\n")
    
    try:
        # Run 2 rounds to see persuasion after first vote
        session = await engine.run_full_deliberation(max_rounds=2)
        
        print("\n" + "="*60)
        print("PERSUASION ANALYSIS")
        print("="*60)
        
        print(f"\nTotal persuasion attempts: {len(persuasion_statements)}")
        
        if vote_counts:
            print("\nVote progression:")
            for i, count in enumerate(vote_counts):
                print(f"  Round {i+1}: {count['guilty']}G / {count['not_guilty']}NG / {count['undecided']}U")
            
            # Check if persuasion changed votes
            if len(vote_counts) >= 2:
                change_g = vote_counts[1]['guilty'] - vote_counts[0]['guilty']
                change_ng = vote_counts[1]['not_guilty'] - vote_counts[0]['not_guilty']
                
                if change_g != 0 or change_ng != 0:
                    print(f"\nVotes changed after persuasion!")
                    print(f"  Guilty: {'+' if change_g > 0 else ''}{change_g}")
                    print(f"  Not Guilty: {'+' if change_ng > 0 else ''}{change_ng}")
                else:
                    print("\nNo votes changed after persuasion")
        
        # Analyze persuasion styles
        if persuasion_statements:
            print("\nPersuasion styles detected:")
            for stmt in persuasion_statements[:3]:  # Show first 3
                if "passionate" in stmt.content.lower() or "!" in stmt.content:
                    print(f"  • {stmt.juror_name}: Emotional appeal")
                elif "evidence" in stmt.content.lower() and "#" in stmt.content:
                    print(f"  • {stmt.juror_name}: Evidence-based")
                elif "concern" in stmt.content.lower() or "worry" in stmt.content.lower():
                    print(f"  • {stmt.juror_name}: Doubt-raising")
                else:
                    print(f"  • {stmt.juror_name}: General argument")
        
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_persuasion_phase())