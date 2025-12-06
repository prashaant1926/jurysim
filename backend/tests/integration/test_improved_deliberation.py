"""Test the improved deliberation engine with realistic dynamics"""
import asyncio
from datetime import datetime
from app.cli.deliberation_interface import SAMPLE_CASES
from app.services.juror_generator import JurorGenerator
from app.services.deliberation_engine_v2 import ImprovedDeliberationEngine
from app.models.deliberation import DeliberationPhase, VerdictChoice
from colorama import init, Fore, Style, Back

# Initialize colorama
init()

async def test_improved_deliberation():
    generator = JurorGenerator()
    
    # Test with theft case in San Francisco
    county = "San Francisco"
    state = "CA"
    case = SAMPLE_CASES["theft"]
    
    print(f"{Style.BRIGHT}Generating jury for {county}, {state}...{Style.RESET_ALL}")
    jurors = generator.generate_jury_pool(county, state, 12)
    
    print(f"\nGenerated {len(jurors)} jurors")
    
    # Show juror profiles
    print(f"\n{Style.BRIGHT}JUROR PROFILES:{Style.RESET_ALL}")
    for juror in jurors[:6]:  # Show first 6
        demo = juror['demographics']
        att = juror['attitudes']
        print(f"  Juror {juror['id']}: {demo['age']}yo {demo['gender']} {demo['race']}")
        print(f"    Education: {demo['education_level']}")
        print(f"    Political: {att['political_view']}/7 (1=very liberal, 7=very conservative)")
        print(f"    Trust courts: {att['trust_courts']*100:.0f}%")
        print()
    
    # Statement handler with colors
    def handle_statement(statement):
        phase_color = {
            DeliberationPhase.OPENING: Fore.CYAN,
            DeliberationPhase.EVIDENCE_REVIEW: Fore.YELLOW,
            DeliberationPhase.DISCUSSION: Fore.GREEN,
            DeliberationPhase.VOTING: Fore.MAGENTA,
            DeliberationPhase.FINAL_VERDICT: Fore.RED
        }
        
        color = phase_color.get(statement.phase, Fore.WHITE)
        print(f"{color}[{statement.phase}] {statement.juror_name}: {statement.content[:100]}...{Style.RESET_ALL}")
        
        # Show sentiment
        if statement.sentiment == "assertive":
            print(f"  {Fore.RED}(Assertive statement){Style.RESET_ALL}")
        elif statement.sentiment == "challenging":
            print(f"  {Fore.YELLOW}(Challenging another juror){Style.RESET_ALL}")
    
    # Vote handler
    def handle_votes(votes):
        print(f"\n{Back.BLUE}{Fore.WHITE} VOTING ROUND {votes[0].round_number} {Style.RESET_ALL}")
        
        guilty = sum(1 for v in votes if v.verdict == VerdictChoice.GUILTY)
        not_guilty = sum(1 for v in votes if v.verdict == VerdictChoice.NOT_GUILTY)
        undecided = sum(1 for v in votes if v.verdict == VerdictChoice.UNDECIDED)
        
        print(f"  Guilty: {guilty}")
        print(f"  Not Guilty: {not_guilty}")
        print(f"  Undecided: {undecided}")
        
        # Show some individual votes
        for vote in votes[:3]:
            verdict_color = Fore.RED if vote.verdict == VerdictChoice.GUILTY else Fore.GREEN
            print(f"  {vote.juror_name}: {verdict_color}{vote.verdict}{Style.RESET_ALL} (confidence: {vote.confidence:.0%})")
    
    # Create improved deliberation engine
    engine = ImprovedDeliberationEngine(
        case=case,
        jurors=jurors,
        on_statement=handle_statement,
        on_vote=handle_votes
    )
    
    # Run deliberation
    try:
        print(f"\n{Style.BRIGHT}Starting improved deliberation...{Style.RESET_ALL}\n")
        session = await engine.run_deliberation(max_rounds=4)
        
        print(f"\n{Style.BRIGHT}DELIBERATION COMPLETED{Style.RESET_ALL}")
        print(f"Final verdict: {session.final_verdict if session.final_verdict else 'HUNG JURY'}")
        print(f"Total statements: {len(session.statements)}")
        print(f"Voting rounds: {len(session.votes) // 12}")
        
        # Analyze voting patterns
        print(f"\n{Style.BRIGHT}VOTING ANALYSIS:{Style.RESET_ALL}")
        for juror_id in range(1, 13):
            juror_votes = [v for v in session.votes if v.juror_id == juror_id]
            if juror_votes:
                juror_name = juror_votes[0].juror_name
                vote_progression = " -> ".join([v.verdict for v in juror_votes])
                print(f"  {juror_name}: {vote_progression}")
        
    except Exception as e:
        print(f"{Fore.RED}Error during deliberation: {type(e).__name__}: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_improved_deliberation())