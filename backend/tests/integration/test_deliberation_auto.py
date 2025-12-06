#!/usr/bin/env python3
"""
Automated test of jury deliberation system
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.cli.deliberation_interface import DeliberationCLI, SAMPLE_CASES
from app.services.juror_generator import JurorGenerator
from app.services.deliberation_engine import DeliberationEngine
from app.models.deliberation import JurorStatement, Vote
from colorama import init, Fore, Style

init()

class AutomatedDeliberationTest:
    def __init__(self):
        self.cli = DeliberationCLI()
        self.statements = []
        self.votes = []
    
    def handle_statement(self, statement: JurorStatement):
        """Collect statements for summary"""
        self.statements.append(statement)
        self.cli._print_statement(statement)
    
    def handle_votes(self, votes):
        """Collect votes for summary"""
        self.votes.extend(votes)
        self.cli._print_votes(votes)
    
    async def run_test(self):
        print(f"{Style.BRIGHT}AUTOMATED JURY DELIBERATION TEST{Style.RESET_ALL}")
        print("=" * 80)
        
        # Test configuration
        county = "San Francisco"
        state = "CA"
        case = SAMPLE_CASES["theft"]  # Simple theft case
        pool_size = 6  # Smaller jury for faster test
        
        print(f"\nConfiguration:")
        print(f"  Location: {county}, {state}")
        print(f"  Case: {case.case_title}")
        print(f"  Jury Size: {pool_size}")
        
        # Generate jury
        print("\nGenerating jury pool...")
        generator = JurorGenerator()
        jurors = generator.generate_jury_pool(county, state, pool_size)
        
        print(f"\nJury Members:")
        for juror in jurors:
            demo = juror['demographics']
            color = self.cli._get_juror_color(juror['id'])
            print(f"{color}  Juror {juror['id']}: {demo['age']}yo {demo['gender']} {demo['race']} - {demo['education_level']}{Style.RESET_ALL}")
        
        # Create deliberation engine
        print("\nStarting deliberation...")
        print("-" * 80)
        
        engine = DeliberationEngine(
            case=case,
            jurors=jurors,
            on_statement=self.handle_statement,
            on_vote=self.handle_votes
        )
        
        # Run deliberation with fewer rounds
        session = await engine.run_deliberation(max_rounds=2)
        
        # Print results
        print("\n" + "=" * 80)
        print("DELIBERATION COMPLETE")
        print("=" * 80)
        
        if session.final_verdict:
            verdict_color = Fore.GREEN if session.final_verdict == "not_guilty" else Fore.RED
            print(f"\n{verdict_color}Final Verdict: {session.final_verdict.upper()}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Result: HUNG JURY{Style.RESET_ALL}")
        
        # Statistics
        print(f"\nStatistics:")
        print(f"  Total Statements: {len(self.statements)}")
        print(f"  Total Votes: {len(self.votes)}")
        print(f"  Duration: {(session.end_time - session.start_time).total_seconds():.1f} seconds")
        
        # Final vote breakdown
        if self.votes:
            final_round_votes = [v for v in self.votes if v.round_number == max(v.round_number for v in self.votes)]
            guilty = sum(1 for v in final_round_votes if v.verdict == "guilty")
            not_guilty = sum(1 for v in final_round_votes if v.verdict == "not_guilty")
            print(f"  Final Vote: {guilty} Guilty, {not_guilty} Not Guilty")
        
        print("\n✅ Test completed successfully!")

async def main():
    test = AutomatedDeliberationTest()
    await test.run_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\n{Fore.RED}Error during test: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()