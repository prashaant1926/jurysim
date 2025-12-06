"""
CLI Interface for Jury Deliberation
"""
import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from colorama import init, Fore, Style, Back
import textwrap
import json
import os
from app.models.deliberation import (
    JurorStatement, Vote, DeliberationCase, DeliberationPhase,
    VerdictChoice
)
from app.services.juror_generator import JurorGenerator
from app.services.deliberation_engine_v2 import ImprovedDeliberationEngine
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine

# Initialize colorama for cross-platform colored output
init()


class DeliberationCLI:
    """Interactive CLI for jury deliberation"""
    
    def __init__(self):
        self.generator = JurorGenerator()
        self.colors = self._assign_colors()
        self.width = 80  # Terminal width
        
    def _assign_colors(self) -> List[str]:
        """Assign colors to jurors with bright, vibrant colors"""
        return [
            Fore.LIGHTRED_EX + Style.BRIGHT,
            Fore.LIGHTGREEN_EX + Style.BRIGHT,
            Fore.LIGHTYELLOW_EX + Style.BRIGHT,
            Fore.LIGHTBLUE_EX + Style.BRIGHT,
            Fore.LIGHTMAGENTA_EX + Style.BRIGHT,
            Fore.LIGHTCYAN_EX + Style.BRIGHT,
            Fore.RED + Style.BRIGHT,
            Fore.GREEN + Style.BRIGHT,
            Fore.YELLOW + Style.BRIGHT,
            Fore.BLUE + Style.BRIGHT,
            Fore.MAGENTA + Style.BRIGHT,
            Fore.CYAN + Style.BRIGHT
        ]

    def _get_juror_icon(self, juror_id: int) -> str:
        """Get a unique symbol for each juror"""
        icons = ["►", "◆", "●", "■", "▲", "▼", "◄", "♦", "♠", "♣", "♥", "★"]
        return icons[(juror_id - 1) % len(icons)] if juror_id > 0 else "►"
    
    def _get_juror_color(self, juror_id: int) -> str:
        """Get color for a specific juror"""
        if juror_id == 0:  # System messages
            return Fore.WHITE + Style.BRIGHT
        return self.colors[(juror_id - 1) % len(self.colors)]
    
    def _print_ascii_logo(self):
        """Print ASCII art logo for the jury system"""
        logo = f"""
{Fore.CYAN}{Style.BRIGHT}
    ██╗██╗   ██╗██████╗ ██╗   ██╗    ██████╗ ███████╗██╗     ██╗██████╗
    ██║██║   ██║██╔══██╗╚██╗ ██╔╝    ██╔══██╗██╔════╝██║     ██║██╔══██╗
    ██║██║   ██║██████╔╝ ╚████╔╝     ██║  ██║█████╗  ██║     ██║██████╔╝
    ██║██║   ██║██╔══██╗  ╚██╔╝      ██║  ██║██╔══╝  ██║     ██║██╔══██╗
    ██║╚██████╔╝██║  ██║   ██║       ██████╔╝███████╗███████╗██║██████╔╝
    ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚══════╝╚══════╝╚═╝╚═════╝
{Style.RESET_ALL}"""
        print(logo)

    def _print_header(self, text: str, char: str = "="):
        """Print a formatted header with ASCII art"""
        border = "╔" + ("═" * (self.width - 2)) + "╗"
        bottom = "╚" + ("═" * (self.width - 2)) + "╝"
        padding = " " * ((self.width - len(text) - 4) // 2)

        print(f"\n{Fore.CYAN}{Style.BRIGHT}{border}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}{padding}{Fore.WHITE}{Style.BRIGHT}{text}{Style.RESET_ALL}{padding}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{bottom}{Style.RESET_ALL}\n")
    
    def _create_stream_callback(self, juror_id: int, juror_name: str, sentiment: str):
        """Create a streaming callback for real-time text output"""
        color = self._get_juror_color(juror_id)
        icon = self._get_juror_icon(juror_id)
        time_str = datetime.now().strftime("%H:%M:%S")

        # Print header first
        print(f"{Fore.WHITE}{'─' * self.width}{Style.RESET_ALL}")
        header = f"{icon}  [{time_str}] {juror_name}"
        if sentiment:
            header += f" ({sentiment})"
        print(f"{color}{Style.BRIGHT}{header}{Style.RESET_ALL}")

        # Print opening box character
        print(f"{color}┃ {Style.RESET_ALL}", end='', flush=True)

        # State for tracking line wrapping
        current_line_length = 0
        max_line_length = self.width - 4  # Account for "┃ " prefix

        def stream_text(text: str):
            nonlocal current_line_length
            for char in text:
                # Check if we need to wrap
                if char == '\n' or current_line_length >= max_line_length:
                    print(f"{color}\n┃ {Style.RESET_ALL}", end='', flush=True)
                    current_line_length = 0
                    if char == '\n':
                        continue

                print(f"{color}{char}{Style.RESET_ALL}", end='', flush=True)
                current_line_length += 1

        return stream_text

    def _finish_stream(self, juror_id: int):
        """Finish a streaming statement"""
        color = self._get_juror_color(juror_id)
        print(f"\n{color}┗{Style.RESET_ALL}\n", flush=True)

    def _print_statement(self, statement: JurorStatement):
        """Print a juror statement with enhanced formatting and icons"""
        color = self._get_juror_color(statement.juror_id)
        icon = self._get_juror_icon(statement.juror_id)

        # Format timestamp
        time_str = statement.timestamp.strftime("%H:%M:%S")

        # Wrap text
        wrapped_lines = textwrap.wrap(statement.content, width=self.width - 20)

        # Print separator line
        print(f"{Fore.WHITE}{'─' * self.width}{Style.RESET_ALL}")

        # Print header with icon
        header = f"{icon}  [{time_str}] {statement.juror_name}"
        if statement.sentiment:
            header += f" ({statement.sentiment})"

        print(f"{color}{Style.BRIGHT}{header}{Style.RESET_ALL}")

        # Print content with box drawing
        for i, line in enumerate(wrapped_lines):
            prefix = "┃" if i < len(wrapped_lines) - 1 else "┗"
            print(f"{color}{prefix} {line}{Style.RESET_ALL}")
        print()
    
    def _print_votes(self, votes: List[Vote]):
        """Print voting results with enhanced ASCII art"""
        # Print voting header with box
        vote_header = f"VOTING ROUND {votes[0].round_number}"
        padding = (self.width - len(vote_header) - 4) // 2

        print(f"\n{Fore.CYAN}{'═' * self.width}{Style.RESET_ALL}")
        print(f"{' ' * padding}{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} {vote_header} {Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * self.width}{Style.RESET_ALL}\n")

        # Count votes
        guilty = []
        not_guilty = []
        undecided = []

        for vote in votes:
            if vote.verdict == VerdictChoice.GUILTY:
                guilty.append(vote)
            elif vote.verdict == VerdictChoice.NOT_GUILTY:
                not_guilty.append(vote)
            else:
                undecided.append(vote)

        # Print summary with colors
        print(f"{Fore.WHITE}┌{'─' * (self.width - 2)}┐{Style.RESET_ALL}")
        summary = f"│  {Fore.RED}[X] Guilty: {len(guilty)}{Fore.WHITE}  |  {Fore.GREEN}[✓] Not Guilty: {len(not_guilty)}{Fore.WHITE}  |  {Fore.YELLOW}[?] Undecided: {len(undecided)}{Fore.WHITE}"
        print(f"{summary.ljust(self.width + 35)}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}└{'─' * (self.width - 2)}┘{Style.RESET_ALL}\n")

        # Print individual votes
        for category, vote_list, verdict_color, symbol in [
            ("GUILTY", guilty, Fore.RED + Style.BRIGHT, "[X]"),
            ("NOT GUILTY", not_guilty, Fore.GREEN + Style.BRIGHT, "[✓]"),
            ("UNDECIDED", undecided, Fore.YELLOW + Style.BRIGHT, "[?]")
        ]:
            if vote_list:
                print(f"\n{verdict_color}╔══ {symbol} {category} ══╗{Style.RESET_ALL}")
                for vote in vote_list:
                    color = self._get_juror_color(vote.juror_id)
                    icon = self._get_juror_icon(vote.juror_id)
                    confidence_bar = "█" * int(vote.confidence * 10)
                    empty_bar = "░" * (10 - int(vote.confidence * 10))
                    print(f"{color}║ {icon} {vote.juror_name:15} [{confidence_bar}{empty_bar}] {vote.confidence:.0%}{Style.RESET_ALL}")
                    if vote.reasoning:
                        wrapped = textwrap.wrap(vote.reasoning, width=self.width - 22)
                        for line in wrapped:
                            print(f"{color}║   ↳ {line}{Style.RESET_ALL}")
                print(f"{verdict_color}╚{'═' * (self.width - 2)}╝{Style.RESET_ALL}")
        print()
    
    def _print_phase(self, phase: DeliberationPhase):
        """Print phase transition with enhanced visuals and ASCII art"""
        phase_info = {
            DeliberationPhase.OPENING: ("OPENING STATEMENTS", Fore.LIGHTBLUE_EX, Back.BLUE, """
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║        ██████╗ ██████╗ ███████╗███╗   ██╗██╗███╗   ██╗ ██████╗          ║
    ║       ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██║████╗  ██║██╔════╝          ║
    ║       ██║   ██║██████╔╝█████╗  ██╔██╗ ██║██║██╔██╗ ██║██║  ███╗         ║
    ║       ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║██║╚██╗██║██║   ██║         ║
    ║       ╚██████╔╝██║     ███████╗██║ ╚████║██║██║ ╚████║╚██████╔╝         ║
    ║        ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝          ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
"""),
            DeliberationPhase.EVIDENCE_REVIEW: ("EVIDENCE REVIEW", Fore.LIGHTCYAN_EX, Back.CYAN, """
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║     ███████╗██╗   ██╗██╗██████╗ ███████╗███╗   ██╗ ██████╗███████╗     ║
    ║     ██╔════╝██║   ██║██║██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝     ║
    ║     █████╗  ██║   ██║██║██║  ██║█████╗  ██╔██╗ ██║██║     █████╗       ║
    ║     ██╔══╝  ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║╚██╗██║██║     ██╔══╝       ║
    ║     ███████╗ ╚████╔╝ ██║██████╔╝███████╗██║ ╚████║╚██████╗███████╗     ║
    ║     ╚══════╝  ╚═══╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝     ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
"""),
            DeliberationPhase.DISCUSSION: ("JURY DISCUSSION", Fore.LIGHTYELLOW_EX, Back.YELLOW, """
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║   ██████╗ ██╗███████╗ ██████╗██╗   ██╗███████╗███████╗██╗ ██████╗ ██╗  ║
    ║   ██╔══██╗██║██╔════╝██╔════╝██║   ██║██╔════╝██╔════╝██║██╔═══██╗████╗ ║
    ║   ██║  ██║██║███████╗██║     ██║   ██║███████╗███████╗██║██║   ██║██╔██╗║
    ║   ██║  ██║██║╚════██║██║     ██║   ██║╚════██║╚════██║██║██║   ██║██║╚██║
    ║   ██████╔╝██║███████║╚██████╗╚██████╔╝███████║███████║██║╚██████╔╝██║ ╚═║
    ║   ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝   ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
"""),
            DeliberationPhase.VOTING: ("VOTING", Fore.LIGHTMAGENTA_EX, Back.MAGENTA, """
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║             ██╗   ██╗ ██████╗ ████████╗██╗███╗   ██╗ ██████╗            ║
    ║             ██║   ██║██╔═══██╗╚══██╔══╝██║████╗  ██║██╔════╝            ║
    ║             ██║   ██║██║   ██║   ██║   ██║██╔██╗ ██║██║  ███╗           ║
    ║             ╚██╗ ██╔╝██║   ██║   ██║   ██║██║╚██╗██║██║   ██║           ║
    ║              ╚████╔╝ ╚██████╔╝   ██║   ██║██║ ╚████║╚██████╔╝           ║
    ║               ╚═══╝   ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝            ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
"""),
            DeliberationPhase.FINAL_VERDICT: ("FINAL VERDICT", Fore.LIGHTGREEN_EX, Back.GREEN, """
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║         ██╗   ██╗███████╗██████╗ ██████╗ ██╗ ██████╗████████╗           ║
    ║         ██║   ██║██╔════╝██╔══██╗██╔══██╗██║██╔════╝╚══██╔══╝           ║
    ║         ██║   ██║█████╗  ██████╔╝██║  ██║██║██║        ██║              ║
    ║         ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║  ██║██║██║        ██║              ║
    ║          ╚████╔╝ ███████╗██║  ██║██████╔╝██║╚██████╗   ██║              ║
    ║           ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝ ╚═════╝   ╚═╝              ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
""")
        }

        phase_name, text_color, bg_color, ascii_art = phase_info.get(phase, (phase.upper(), Fore.WHITE, Back.BLACK, ""))

        # Print ASCII art banner
        if ascii_art:
            print(f"{text_color}{Style.BRIGHT}{ascii_art}{Style.RESET_ALL}")
    
    async def run_deliberation(
        self,
        county: str,
        state: str,
        case: DeliberationCase,
        pool_size: int = 6
    ):
        """Run an interactive jury deliberation"""
        
        # Clear screen
        print("\033[2J\033[1;1H")

        # Print ASCII logo
        self._print_ascii_logo()

        self._print_header("JURY DELIBERATION SIMULATION", "=")
        
        # Display case information
        print(f"{Style.BRIGHT}CASE:{Style.RESET_ALL} {case.case_title}")
        print(f"{Style.BRIGHT}TYPE:{Style.RESET_ALL} {case.case_type.replace('_', ' ').title()}")
        print(f"{Style.BRIGHT}LOCATION:{Style.RESET_ALL} {county}, {state}")

        # Display AI model information
        ai_model_box = f"""
{Fore.GREEN}{Style.BRIGHT}╔═══════════════════════════════════════════════════════════════════════════╗
║                          AI MODEL CONFIGURATION                           ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Model:        Claude Opus 4.5 (claude-opus-4-5-20251101)               ║
║  Provider:     Anthropic                                                  ║
║  Features:     - Randomized temperature (0.7-1.0)                        ║
║                - 12 varied prompt structures per phase                    ║
║                - Context-aware response selection                         ║
╚═══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}"""
        print(ai_model_box)
        print()
        
        # Generate jury pool
        print("Selecting jury...")
        jurors = self.generator.generate_jury_pool(county, state, pool_size)
        
        # Display juror list with enhanced formatting
        print(f"\n{Fore.CYAN}{'═' * self.width}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{Style.BRIGHT}JURY PANEL:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * self.width}{Style.RESET_ALL}\n")

        for juror in jurors:
            color = self._get_juror_color(juror['id'])
            icon = self._get_juror_icon(juror['id'])
            demo = juror['demographics']
            print(f"{color}{Style.BRIGHT}{icon} Juror #{juror['id']:2d} │ {demo['age']}yo {demo['gender']} {demo['race']} │ {demo['education_level']}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{'═' * self.width}{Style.RESET_ALL}")
        
        print("\nPress Enter to begin deliberation...")
        input()
        
        # Clear screen for deliberation
        print("\033[2J\033[1;1H")
        self._print_header(f"DELIBERATION: {case.case_title}")
        
        # Create stream callback factory
        self.active_stream_callback = None
        self.active_juror_id = None

        def create_stream_callback(juror_name: str, juror_id: int):
            """Factory function to create stream callbacks for each statement"""
            self.active_juror_id = juror_id
            self.active_stream_callback = self._create_stream_callback(juror_id, juror_name, "")
            return self.active_stream_callback

        # Create responsive deliberation engine for dynamic interactions
        engine = ResponsiveDeliberationEngine(
            case=case,
            jurors=jurors,
            county=county,
            state=state,
            on_statement=self._handle_statement,
            on_vote=self._handle_votes,
            stream_callback_factory=create_stream_callback
        )
        
        # Track current phase
        self.current_phase = None
        
        # Run deliberation
        try:
            session = await engine.run_full_deliberation(max_rounds=10)
            
            # Print final verdict with dramatic ASCII art
            verdict_banner = f"""
{Fore.CYAN}{Style.BRIGHT}
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ███████╗██╗███╗   ██╗ █████╗ ██╗         ██╗   ██╗███████╗██████╗     ║
║   ██╔════╝██║████╗  ██║██╔══██╗██║         ██║   ██║██╔════╝██╔══██╗    ║
║   █████╗  ██║██╔██╗ ██║███████║██║         ██║   ██║█████╗  ██████╔╝    ║
║   ██╔══╝  ██║██║╚██╗██║██╔══██║██║         ╚██╗ ██╔╝██╔══╝  ██╔══██╗    ║
║   ██║     ██║██║ ╚████║██║  ██║███████╗     ╚████╔╝ ███████╗██║  ██║    ║
║   ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝      ╚═══╝  ╚══════╝╚═╝  ╚═╝    ║
║                                                                           ║
║                    ██████╗ ██╗ ██████╗████████╗                          ║
║                    ██╔══██╗██║██╔════╝╚══██╔══╝                          ║
║                    ██║  ██║██║██║        ██║                             ║
║                    ██║  ██║██║██║        ██║                             ║
║                    ██████╔╝██║╚██████╗   ██║                             ║
║                    ╚═════╝ ╚═╝ ╚═════╝   ╚═╝                             ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
            print(verdict_banner)

            if session.final_verdict:
                # Handle both string and enum cases
                if isinstance(session.final_verdict, str):
                    verdict_text = "GUILTY" if session.final_verdict == "guilty" else "NOT GUILTY"
                    is_not_guilty = session.final_verdict == "not_guilty"
                else:
                    verdict_text = "GUILTY" if session.final_verdict == VerdictChoice.GUILTY else "NOT GUILTY"
                    is_not_guilty = session.final_verdict == VerdictChoice.NOT_GUILTY

                verdict_symbol = "[✓]" if is_not_guilty else "[X]"
                verdict_box = f"{verdict_symbol}  The jury finds the defendant {verdict_text}  {verdict_symbol}"
                padding = " " * ((self.width - len(verdict_box)) // 2)

                print(f"{padding}{Back.GREEN if is_not_guilty else Back.RED}"
                      f"{Fore.WHITE}{Style.BRIGHT} {verdict_box} {Style.RESET_ALL}\n")
            else:
                hung_text = "[?] HUNG JURY - No unanimous verdict reached [?]"
                padding = " " * ((self.width - len(hung_text)) // 2)
                print(f"{padding}{Back.YELLOW}{Fore.BLACK}{Style.BRIGHT} {hung_text} {Style.RESET_ALL}\n")
            
            # Print statistics
            print(f"\nDeliberation Statistics:")
            print(f"  Duration: {(session.end_time - session.start_time).total_seconds() / 60:.1f} minutes")
            print(f"  Total Statements: {len(session.statements)}")
            print(f"  Voting Rounds: {len(session.votes) // 12}")
            
            # Final vote breakdown
            final_votes = session.votes[-12:]
            if final_votes:
                guilty_count = sum(1 for v in final_votes if v.verdict == VerdictChoice.GUILTY)
                not_guilty_count = sum(1 for v in final_votes if v.verdict == VerdictChoice.NOT_GUILTY)
                print(f"  Final Vote: {guilty_count} Guilty, {not_guilty_count} Not Guilty")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}Deliberation interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n\n{Fore.RED}Error during deliberation: {e}{Style.RESET_ALL}")
    
    def _handle_statement(self, statement: JurorStatement):
        """Handle statement callback from engine"""
        # Check for phase change
        if self.current_phase != statement.phase:
            self.current_phase = statement.phase
            self._print_phase(statement.phase)

        # Check if this is a persuasion phase statement
        if statement.juror_id == 0 and "split" in statement.content.lower() and "let's hear from both sides" in statement.content.lower():
            print(f"\n{Back.MAGENTA}{Fore.WHITE} POST-VOTE PERSUASION {Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{'─' * 60}{Style.RESET_ALL}\n")

        # If streaming was active, finish it
        if self.active_stream_callback and self.active_juror_id == statement.juror_id:
            self._finish_stream(statement.juror_id)
            self.active_stream_callback = None
            self.active_juror_id = None
        else:
            # No streaming, print normally
            self._print_statement(statement)

        # Small delay for readability
        time.sleep(0.1)
    
    def _handle_votes(self, votes: List[Vote]):
        """Handle voting callback from engine"""
        self._print_votes(votes)
        time.sleep(0.5)


# Sample cases for testing
SAMPLE_CASES = {
    "theft": DeliberationCase(
        case_type="theft",
        case_title="Fictional Case Study: State v. Johnson - Retail Theft Simulation",
        summary="In this educational scenario, a defendant is accused of stealing $500 worth of electronics from a retail store.",
        key_evidence=[
            "Security camera footage showing defendant in store",
            "Receipt showing no purchase of items found in defendant's bag",
            "Defendant's explanation that items were a gift",
            "No witness saw defendant take items"
        ],
        prosecution_argument="Security footage and unpurchased items prove theft beyond reasonable doubt.",
        defense_argument="No direct evidence of theft; items could have been placed by someone else.",
        jury_instructions="Theft requires proof of intentional taking of property without permission.",
        requires_unanimous=True
    ),
    
    "assault": DeliberationCase(
        case_type="assault",
        case_title="State v. Martinez - Assault and Battery",
        summary="Bar fight resulting in serious injuries. Defendant claims self-defense.",
        key_evidence=[
            "Victim suffered broken nose and concussion",
            "Three witnesses with conflicting accounts",
            "Defendant has prior arrest for fighting (not admissible)",
            "Security footage is unclear due to crowd"
        ],
        prosecution_argument="Defendant used excessive force beyond self-defense.",
        defense_argument="Defendant reasonably believed he was in danger and acted in self-defense.",
        jury_instructions="Self-defense requires reasonable belief of imminent danger and proportional response.",
        requires_unanimous=True
    ),
    
    "murder": DeliberationCase(
        case_type="murder",
        case_title="State v. Williams - First Degree Murder",
        summary="Defendant accused of premeditated murder of business partner over financial dispute.",
        key_evidence=[
            "Defendant's fingerprints on murder weapon",
            "Text messages showing heated argument about money",
            "Defendant's alibi partially corroborated",
            "No eyewitnesses to the crime",
            "Victim's blood found in defendant's car"
        ],
        prosecution_argument="Physical evidence and motive prove premeditated murder.",
        defense_argument="Circumstantial evidence only; defendant was framed by real killer.",
        jury_instructions="First degree murder requires proof of premeditation and deliberate intent to kill.",
        requires_unanimous=True
    ),
    
    "oj_simpson": DeliberationCase(
        case_type="murder",
        case_title="People of the State of California v. Orenthal James Simpson",
        summary="O.J. Simpson was charged with the murders of his ex-wife Nicole Brown Simpson and Ronald Goldman on June 12, 1994, at Nicole's condominium at 875 South Bundy Drive in Brentwood.",
        key_evidence=[
            "Blood evidence found at Bundy crime scene matching defendant",
            "Blood evidence found at Rockingham (defendant's home)",
            "Blood evidence in white Ford Bronco",
            "Hair and fiber evidence consistent with defendant",
            "Bloody glove found at Rockingham matching glove at crime scene",
            "Footprints at crime scene consistent with Bruno Magli shoes (size 12)",
            "Defendant's history of domestic violence against Nicole Brown Simpson",
            "911 calls from Nicole Brown Simpson reporting abuse",
            "Defendant's whereabouts unaccounted for during time of murders",
            "Cuts on defendant's hand discovered after murders",
            "DNA evidence linking defendant to crime scene",
            "Autopsy reports showing violent nature of attacks",
            "Witness testimony about defendant's demeanor after murders",
            "Evidence of defendant's flight from police",
            "Suicide note found in defendant's possession"
        ],
        prosecution_argument="Physical evidence, DNA matches, history of domestic violence, and defendant's consciousness of guilt shown by flight attempt prove he murdered victims in jealous rage after being rejected.",
        defense_argument="Evidence was contaminated, mishandled, and planted by racist LAPD officers; timeline makes it physically impossible for defendant to have committed murders; glove doesn't fit.",
        jury_instructions="You must determine guilt beyond a reasonable doubt. Consider all evidence presented, but remember the defendant is presumed innocent until proven guilty.",
        requires_unanimous=True
    )
}


import time  # Add this import

def load_oj_simpson_complete() -> Optional[DeliberationCase]:
    """Load the complete OJ Simpson case with all transcript data"""
    json_path = "data/case_files/oj_simpson_complete_content.json"
    
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found. Using default OJ Simpson case.")
        return SAMPLE_CASES["oj_simpson"]
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            complete_content = json.load(f)
        
        # Extract additional context from transcripts
        testimony_excerpts = []
        key_moments = []
        
        for doc in complete_content:
            if doc['type'] == 'deposition' and 'Simpson' in doc['title']:
                # Extract key Q&A exchanges
                content = doc.get('content', '')
                if 'Q:' in content and 'A:' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('Q:') and i+1 < len(lines):
                            question = line.strip()
                            answer = lines[i+1].strip() if lines[i+1].strip().startswith('A:') else ''
                            if answer and len(question) < 200 and len(answer) < 200:
                                testimony_excerpts.append(f"{question} {answer}")
                                if len(testimony_excerpts) >= 5:
                                    break
            
            elif doc['type'] == 'evidence':
                # Extract key evidence descriptions
                if '911' in doc['title']:
                    key_moments.append("911 call: Nicole reported being afraid, said 'He's going to kill me'")
                elif 'DNA' in doc['title']:
                    key_moments.append("DNA evidence: Matches found at crime scene, Rockingham, and Bronco")
        
        # Create enhanced case with full context
        enhanced_case = DeliberationCase(
            case_type="murder",
            case_title="People of the State of California v. Orenthal James Simpson",
            summary=f"O.J. Simpson was charged with the murders of his ex-wife Nicole Brown Simpson and Ronald Goldman on June 12, 1994, at Nicole's condominium at 875 South Bundy Drive in Brentwood. This case includes {len(complete_content)} documents of evidence, depositions, and trial transcripts.",
            key_evidence=[
                "Blood evidence at Bundy crime scene with DNA matching defendant (1 in 170 million)",
                "Blood trail from Bundy to defendant's Bronco to Rockingham home",
                "Left-hand Aris leather glove at Bundy, matching right-hand glove at Rockingham",
                "Bruno Magli shoe prints (size 12) in blood at crime scene",
                "Hair consistent with defendant found on Goldman's shirt and knit cap",
                "Fiber evidence from Bronco carpet found at Bundy",
                "History of domestic violence: 1989 conviction, multiple 911 calls",
                "Nicole's diary entries documenting abuse and fear",
                "Defendant's whereabouts unaccounted for during murder window (10:15-10:40 PM)",
                "Fresh cuts on defendant's left hand morning after murders",
                "Blood inside Bronco on console, steering wheel, and door",
                "Autopsy: Nicole nearly decapitated, Goldman had defensive wounds",
                "Kato Kaelin heard thumps at 10:40 PM near where glove found",
                "Limousine driver saw defendant enter house at 10:54 PM",
                "Defendant's 'suicide note' and attempted flight with passport and cash"
            ],
            prosecution_argument="Mountain of physical evidence, clear motive from history of abuse and jealousy, consciousness of guilt from flight, and timeline placing defendant at scene prove murders beyond any doubt. DNA evidence alone is overwhelming.",
            defense_argument="LAPD conspiracy to frame defendant due to racial bias, especially by Det. Fuhrman who planted evidence. Glove doesn't fit. Timeline impossible - defendant couldn't commit murders and return home in time. Evidence contaminated and chain of custody broken.",
            jury_instructions="You must find the defendant guilty only if the prosecution proves guilt beyond a reasonable doubt. Consider all evidence, but if you have reasonable doubt, you must acquit. Circumstantial evidence can be sufficient if it excludes all reasonable theories of innocence.",
            requires_unanimous=True
        )
        
        print(f"\nLoaded complete OJ Simpson case with {len(complete_content)} source documents")
        return enhanced_case
        
    except Exception as e:
        print(f"Error loading complete OJ content: {e}")
        return SAMPLE_CASES["oj_simpson"]

def load_zimmerman_case() -> DeliberationCase:
    """Load the George Zimmerman case"""
    json_path = "zimmerman_case_deliberation.json"
    
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found. Using default Zimmerman case.")
        # Return a default version
        return DeliberationCase(
            case_type="murder",
            case_title="State of Florida v. George Zimmerman",
            summary="George Zimmerman, a neighborhood watch volunteer, shot and killed 17-year-old Trayvon Martin on February 26, 2012, in Sanford, Florida. Zimmerman claims self-defense under Florida's Stand Your Ground law.",
            key_evidence=[
                "911 call: Zimmerman reported Martin as suspicious person",
                "Physical evidence: Zimmerman had injuries from struggle",
                "Witness: Jonathan Good saw Martin on top of Zimmerman",
                "Forensics: Single gunshot wound at close range",
                "Martin was unarmed, carrying Skittles and iced tea",
                "Dispatcher told Zimmerman 'we don't need you to' follow",
                "Zimmerman's injuries: broken nose, head lacerations",
                "No witness saw initial confrontation",
                "Martin on phone with Rachel Jeantel during encounter",
                "Time gap between call and shooting: ~2 minutes"
            ],
            prosecution_argument="Zimmerman profiled and pursued Martin, creating confrontation. Minor injuries didn't justify deadly force against unarmed teenager.",
            defense_argument="Zimmerman acted in self-defense when Martin attacked him. He reasonably feared death or great bodily harm from concrete head strikes.",
            jury_instructions="For guilty verdict, must find depraved mind/ill will (murder 2) or intentional act causing death (manslaughter). Self-defense requires reasonable belief of imminent death/great bodily harm.",
            requires_unanimous=True
        )
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            case_data = json.load(f)
        
        return DeliberationCase(**case_data)
        
    except Exception as e:
        print(f"Error loading Zimmerman case: {e}")
        # Return default version
        return DeliberationCase(
            case_type="murder",
            case_title="State of Florida v. George Zimmerman",
            summary="George Zimmerman, a neighborhood watch volunteer, shot and killed 17-year-old Trayvon Martin on February 26, 2012, in Sanford, Florida. Zimmerman claims self-defense under Florida's Stand Your Ground law.",
            key_evidence=[
                "911 call: Zimmerman reported Martin as suspicious person",
                "Physical evidence: Zimmerman had injuries from struggle",
                "Witness: Jonathan Good saw Martin on top of Zimmerman",
                "Forensics: Single gunshot wound at close range",
                "Martin was unarmed, carrying Skittles and iced tea",
                "Dispatcher told Zimmerman 'we don't need you to' follow",
                "Zimmerman's injuries: broken nose, head lacerations",
                "No witness saw initial confrontation",
                "Martin on phone with Rachel Jeantel during encounter",
                "Time gap between call and shooting: ~2 minutes"
            ],
            prosecution_argument="Zimmerman profiled and pursued Martin, creating confrontation. Minor injuries didn't justify deadly force against unarmed teenager.",
            defense_argument="Zimmerman acted in self-defense when Martin attacked him. He reasonably feared death or great bodily harm from concrete head strikes.",
            jury_instructions="For guilty verdict, must find depraved mind/ill will (murder 2) or intentional act causing death (manslaughter). Self-defense requires reasonable belief of imminent death/great bodily harm.",
            requires_unanimous=True
        )

def create_custom_case() -> Optional[DeliberationCase]:
    """Create a custom case from user input"""
    print("\n" + "="*60)
    print("CREATE CUSTOM CASE")
    print("="*60)
    
    print("\nYou can either:")
    print("1. Enter case details step by step")
    print("2. Paste a full case description")
    
    input_choice = input("\nChoice (1-2): ")
    
    if input_choice == "2":
        return parse_case_from_text()
    else:
        return create_case_step_by_step()

def parse_case_from_text() -> Optional[DeliberationCase]:
    """Parse a case from pasted text"""
    print("\nPaste your case description (press Enter twice when done):")
    print("Format should include: case title, summary, evidence list, prosecution argument, defense argument")
    print("-" * 60)
    
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    text = "\n".join(lines).strip()
    
    if not text:
        print("No text entered")
        return None
    
    # Try to parse the text intelligently
    try:
        # Default values
        case_data = {
            "case_type": "other",
            "case_title": "Custom Case",
            "summary": "",
            "key_evidence": [],
            "prosecution_argument": "",
            "defense_argument": "",
            "jury_instructions": "You must determine guilt beyond a reasonable doubt.",
            "requires_unanimous": True
        }
        
        # Look for sections
        sections = text.lower()
        
        # Extract title
        if "title:" in sections or "case:" in sections:
            title_match = text[text.lower().find("title:" if "title:" in sections else "case:"):]
            case_data["case_title"] = title_match.split("\n")[0].split(":", 1)[1].strip()
        
        # Extract summary
        if "summary:" in sections:
            summary_start = text.lower().find("summary:")
            summary_text = text[summary_start:].split(":", 1)[1]
            # Find next section
            for keyword in ["evidence", "prosecution", "defense"]:
                if keyword in summary_text.lower():
                    summary_text = summary_text[:summary_text.lower().find(keyword)]
                    break
            case_data["summary"] = summary_text.strip()
        else:
            # Use first paragraph as summary
            case_data["summary"] = text.split("\n\n")[0][:200]
        
        # Extract evidence
        if "evidence" in sections:
            evidence_start = text.lower().find("evidence")
            evidence_text = text[evidence_start:]
            evidence_lines = evidence_text.split("\n")[1:]  # Skip the "evidence" line
            
            evidence_list = []
            for line in evidence_lines:
                line = line.strip()
                if line and not any(keyword in line.lower() for keyword in ["prosecution", "defense", "instruction"]):
                    # Remove bullet points or numbers
                    line = line.lstrip("•-*123456789. ")
                    if line:
                        evidence_list.append(line)
                elif any(keyword in line.lower() for keyword in ["prosecution", "defense"]):
                    break
            
            case_data["key_evidence"] = evidence_list[:10]  # Limit to 10 items
        
        # Extract prosecution argument
        if "prosecution" in sections:
            pros_start = text.lower().find("prosecution")
            pros_text = text[pros_start:].split(":", 1)[1] if ":" in text[pros_start:] else text[pros_start:].split("\n", 1)[1]
            # Find next section
            if "defense" in pros_text.lower():
                pros_text = pros_text[:pros_text.lower().find("defense")]
            case_data["prosecution_argument"] = pros_text.strip()[:200]
        
        # Extract defense argument
        if "defense" in sections:
            def_start = text.lower().find("defense")
            def_text = text[def_start:].split(":", 1)[1] if ":" in text[def_start:] else text[def_start:].split("\n", 1)[1]
            # Find next section
            if "instruction" in def_text.lower() or "jury" in def_text.lower():
                def_text = def_text[:def_text.lower().find("instruction" if "instruction" in def_text.lower() else "jury")]
            case_data["defense_argument"] = def_text.strip()[:200]
        
        # Determine case type
        crime_keywords = {
            "murder": ["murder", "homicide", "killing", "death"],
            "theft": ["theft", "stealing", "robbery", "burglary", "larceny"],
            "assault": ["assault", "battery", "attack", "violence"],
            "fraud": ["fraud", "embezzlement", "forgery", "deception"],
            "drug": ["drug", "narcotic", "possession", "trafficking"]
        }
        
        for crime_type, keywords in crime_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                case_data["case_type"] = crime_type
                break
        
        # Validate we have minimum required data
        if not case_data["key_evidence"]:
            print("\nNo evidence found. Please add at least 3 pieces of evidence:")
            for i in range(3):
                evidence = input(f"Evidence {i+1}: ")
                if evidence:
                    case_data["key_evidence"].append(evidence)
        
        if not case_data["prosecution_argument"]:
            case_data["prosecution_argument"] = input("\nProsecution's main argument: ")
        
        if not case_data["defense_argument"]:
            case_data["defense_argument"] = input("\nDefense's main argument: ")
        
        print("\n" + "="*60)
        print("PARSED CASE:")
        print(f"Title: {case_data['case_title']}")
        print(f"Type: {case_data['case_type']}")
        print(f"Summary: {case_data['summary'][:100]}...")
        print(f"Evidence items: {len(case_data['key_evidence'])}")
        print("="*60)
        
        confirm = input("\nUse this case? (y/n): ")
        if confirm.lower() == 'y':
            return DeliberationCase(**case_data)
        else:
            return create_case_step_by_step()
            
    except Exception as e:
        print(f"Error parsing case: {e}")
        return create_case_step_by_step()

def create_case_step_by_step() -> Optional[DeliberationCase]:
    """Create a case by prompting for each field"""
    print("\nEnter case details:")
    
    # Case type
    print("\nCase type options: murder, theft, assault, fraud, drug, other")
    case_type = input("Case type: ").lower()
    if case_type not in ["murder", "theft", "assault", "fraud", "drug", "other"]:
        case_type = "other"
    
    # Case title
    case_title = input("\nCase title (e.g., 'State v. Smith'): ")
    if not case_title:
        case_title = "Custom Case"
    
    # Summary
    print("\nCase summary (brief description):")
    summary = input()
    if not summary:
        summary = "A criminal case requiring jury deliberation."
    
    # Evidence
    print("\nEnter key evidence (one per line, empty line to finish):")
    key_evidence = []
    while True:
        evidence = input(f"Evidence {len(key_evidence)+1}: ")
        if not evidence:
            break
        key_evidence.append(evidence)
    
    if not key_evidence:
        print("Must have at least one piece of evidence!")
        return None
    
    # Arguments
    prosecution_argument = input("\nProsecution's main argument: ")
    if not prosecution_argument:
        prosecution_argument = "The evidence proves guilt beyond a reasonable doubt."
    
    defense_argument = input("\nDefense's main argument: ")
    if not defense_argument:
        defense_argument = "The evidence is insufficient to prove guilt."
    
    # Jury instructions
    jury_instructions = input("\nJury instructions (or press Enter for default): ")
    if not jury_instructions:
        jury_instructions = "You must determine guilt beyond a reasonable doubt. Consider all evidence presented."
    
    return DeliberationCase(
        case_type=case_type,
        case_title=case_title,
        summary=summary,
        key_evidence=key_evidence,
        prosecution_argument=prosecution_argument,
        defense_argument=defense_argument,
        jury_instructions=jury_instructions,
        requires_unanimous=True
    )

async def main():
    """Main entry point for CLI"""
    cli = DeliberationCLI()

    # Print welcome banner
    welcome_banner = f"""
{Fore.CYAN}{Style.BRIGHT}
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║        ██╗██╗   ██╗██████╗ ██╗   ██╗    ███████╗██╗███╗   ███╗          ║
║        ██║██║   ██║██╔══██╗╚██╗ ██╔╝    ██╔════╝██║████╗ ████║          ║
║        ██║██║   ██║██████╔╝ ╚████╔╝     ███████╗██║██╔████╔██║          ║
║   ██   ██║██║   ██║██╔══██╗  ╚██╔╝      ╚════██║██║██║╚██╔╝██║          ║
║   ╚█████╔╝╚██████╔╝██║  ██║   ██║       ███████║██║██║ ╚═╝ ██║          ║
║    ╚════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚══════╝╚═╝╚═╝     ╚═╝          ║
║                                                                           ║
║               >>> AI-Powered Jury Deliberation System <<<                ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
    print(welcome_banner)
    
    # Select location
    print("\nSelect location:")
    print("1. San Francisco, CA (Liberal)")
    print("2. Maricopa, AZ (Purple/Swing)")
    print("3. Oklahoma, OK (Conservative)")
    print("4. Cook County, IL (Liberal - Chicago)")
    print("5. Harris County, TX (Purple - Houston)")
    print("6. Miami-Dade, FL (Purple - Miami)")
    print("7. King County, WA (Liberal - Seattle)")
    print("8. Orange County, CA (Purple - Southern CA)")
    print("9. Fulton County, GA (Liberal - Atlanta)")
    print("10. Dallas County, TX (Purple - Dallas)")
    
    location_choice = input("\nChoice (1-10): ")
    locations = {
        "1": ("San Francisco", "CA"),
        "2": ("Maricopa", "AZ"),
        "3": ("Oklahoma", "OK"),
        "4": ("Cook", "IL"),
        "5": ("Harris", "TX"),
        "6": ("Miami-Dade", "FL"),
        "7": ("King", "WA"),
        "8": ("Orange", "CA"),
        "9": ("Fulton", "GA"),
        "10": ("Dallas", "TX")
    }
    county, state = locations.get(location_choice, ("San Francisco", "CA"))
    
    # Select case
    print("\nSelect case type:")
    print("1. Theft")
    print("2. Assault")
    print("3. Murder")
    print("4. O.J. Simpson Murder Trial")
    print("5. George Zimmerman Trial")
    print("6. Custom Case (Enter your own)")
    
    case_choice = input("\nChoice (1-6): ")
    
    if case_choice == "6":
        case = create_custom_case()
        if not case:
            print("Failed to create custom case")
            return
    elif case_choice == "4":
        # Load complete OJ Simpson case with all transcript data
        case = load_oj_simpson_complete()
    elif case_choice == "5":
        # Load George Zimmerman case
        case = load_zimmerman_case()
    else:
        case_types = {
            "1": "theft", 
            "2": "assault", 
            "3": "murder"
        }
        case_type = case_types.get(case_choice, "theft")
        case = SAMPLE_CASES[case_type]
    
    # Run deliberation
    await cli.run_deliberation(county, state, case)


if __name__ == "__main__":
    asyncio.run(main())