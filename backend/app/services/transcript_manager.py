"""
Centralized Transcript Manager for Jury Deliberations
"""
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.deliberation import (
    DeliberationSession, JurorStatement, Vote, 
    DeliberationPhase, DeliberationCase, JurorPersona
)
import json


class TranscriptManager:
    """Manages a single comprehensive transcript for the entire deliberation"""
    
    def __init__(self, session_id: str, case: DeliberationCase, jurors: List[JurorPersona], 
                 county: str, state: str):
        self.session_id = session_id
        self.case = case
        self.jurors = jurors
        self.county = county
        self.state = state
        self.start_time = datetime.utcnow()
        
        # Create transcript directory
        self.transcript_dir = Path("/Users/prashaantranganathan/FreudLaw/backend/transcripts")
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename based on case and location
        case_name = self._sanitize_filename(case.case_title)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        self.transcript_file = self.transcript_dir / f"{case_name}_{county}_{state}_{timestamp}.txt"
        
        # Initialize the transcript
        self._init_transcript()
        
        # Track voting rounds
        self.current_voting_round = 0
        
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename by removing special characters"""
        # Keep only alphanumeric and spaces, then replace spaces with underscores
        sanitized = ''.join(c for c in name if c.isalnum() or c in (' ', '-'))
        sanitized = sanitized.replace(' ', '_').replace('-', '_')
        # Limit length and remove multiple underscores
        sanitized = '_'.join(filter(None, sanitized.split('_')))[:50]
        return sanitized
    
    def _init_transcript(self):
        """Initialize the transcript with header information"""
        header = f"""JURY DELIBERATION TRANSCRIPT
{'='*80}

CASE INFORMATION:
Title: {self.case.case_title}
Type: {self.case.case_type.replace('_', ' ').title()}
Location: {self.county}, {self.state}
Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
Session ID: {self.session_id}

CASE SUMMARY:
{self.case.summary}

KEY EVIDENCE:
{chr(10).join(f'{i+1}. {evidence}' for i, evidence in enumerate(self.case.key_evidence))}

PROSECUTION'S ARGUMENT:
{self.case.prosecution_argument}

DEFENSE'S ARGUMENT:
{self.case.defense_argument}

JURY INSTRUCTIONS:
{self.case.jury_instructions}

{'='*80}

JURY COMPOSITION ({len(self.jurors)} Jurors):
"""
        
        # Add juror information
        for juror in self.jurors:
            demo = juror.demographics
            header += f"\nJuror #{juror.juror_id} - {juror.name}:"
            header += f"\n  Age: {demo.get('age')}, Gender: {demo.get('gender')}, Race: {demo.get('race')}"
            header += f"\n  Education: {demo.get('education_level')}, Income: ${demo.get('income', 0):,}"
            header += f"\n  Political Views: {juror.attitudes.get('political_view', 'Unknown')}/7"
            header += "\n"
        
        header += f"\n{'='*80}\nDELIBERATION BEGINS:\n{'='*80}\n"
        
        with open(self.transcript_file, 'w') as f:
            f.write(header)
    
    def add_phase_marker(self, phase: DeliberationPhase):
        """Add a phase transition marker to the transcript"""
        phase_header = f"\n\n{'='*40}\n{phase.value.upper().replace('_', ' ')}\n{'='*40}\n\n"
        with open(self.transcript_file, 'a') as f:
            f.write(phase_header)
    
    def add_statement(self, statement: JurorStatement):
        """Add a juror statement to the transcript"""
        timestamp = datetime.utcnow().strftime('%H:%M:%S')
        
        # Format the statement
        entry = f"[{timestamp}] {statement.juror_name}"
        if hasattr(statement, 'sentiment') and statement.sentiment:
            entry += f" ({statement.sentiment})"
        entry += f"\n           {statement.content}\n\n"
        
        with open(self.transcript_file, 'a') as f:
            f.write(entry)
    
    def add_voting_round(self, votes: List[Vote]):
        """Add a voting round to the transcript"""
        if not votes:
            return
            
        self.current_voting_round = votes[0].round_number
        
        # Create voting header
        vote_header = f"\n{'='*40}\nVOTING ROUND {self.current_voting_round}\n{'='*40}\n\n"
        
        # Group votes by verdict
        guilty = []
        not_guilty = []
        undecided = []
        
        for vote in votes:
            vote_info = {
                'name': vote.juror_name,
                'confidence': vote.confidence,
                'reasoning': vote.reasoning
            }
            
            if vote.verdict.value == 'guilty':
                guilty.append(vote_info)
            elif vote.verdict.value == 'not_guilty':
                not_guilty.append(vote_info)
            else:
                undecided.append(vote_info)
        
        # Format voting results
        vote_summary = f"Guilty: {len(guilty)} | Not Guilty: {len(not_guilty)} | Undecided: {len(undecided)}\n"
        vote_summary += "-" * 80 + "\n\n"
        
        # Add each category
        if guilty:
            vote_summary += "GUILTY:\n"
            for v in guilty:
                vote_summary += f"  {v['name']:<16} [{'█' * int(v['confidence'] * 10):<10}] {int(v['confidence'] * 100)}%\n"
                vote_summary += f"                   {self._wrap_text(v['reasoning'], 65, 19)}\n\n"
        
        if not_guilty:
            vote_summary += "NOT GUILTY:\n"
            for v in not_guilty:
                vote_summary += f"  {v['name']:<16} [{'█' * int(v['confidence'] * 10):<10}] {int(v['confidence'] * 100)}%\n"
                vote_summary += f"                   {self._wrap_text(v['reasoning'], 65, 19)}\n\n"
        
        if undecided:
            vote_summary += "UNDECIDED:\n"
            for v in undecided:
                vote_summary += f"  {v['name']:<16} [{'█' * int(v['confidence'] * 10):<10}] {int(v['confidence'] * 100)}%\n"
                vote_summary += f"                   {self._wrap_text(v['reasoning'], 65, 19)}\n\n"
        
        with open(self.transcript_file, 'a') as f:
            f.write(vote_header + vote_summary)
    
    def _wrap_text(self, text: str, width: int, indent: int) -> str:
        """Wrap text to specified width with indentation"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > width:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Add indentation to all lines after the first
        return lines[0] if len(lines) == 1 else lines[0] + '\n' + '\n'.join(' ' * indent + line for line in lines[1:])
    
    def add_verdict(self, verdict: Optional[str], final_votes: List[Vote]):
        """Add the final verdict to the transcript"""
        end_time = datetime.utcnow()
        duration_minutes = (end_time - self.start_time).total_seconds() / 60
        
        verdict_section = f"\n\n{'='*80}\n"
        verdict_section += " " * 30 + "VERDICT\n"
        verdict_section += "="*80 + "\n\n"
        
        if verdict:
            verdict_text = "GUILTY" if verdict == "guilty" else "NOT GUILTY"
            verdict_section += f" {verdict_text.center(78)} \n\n"
        else:
            verdict_section += " HUNG JURY - No unanimous verdict reached \n\n"
        
        # Add statistics
        verdict_section += f"Deliberation Statistics:\n"
        verdict_section += f"  Duration: {duration_minutes:.1f} minutes\n"
        verdict_section += f"  Total Statements: {self._count_statements()}\n"
        verdict_section += f"  Voting Rounds: {self.current_voting_round}\n"
        
        if final_votes:
            guilty_count = sum(1 for v in final_votes if v.verdict.value == 'guilty')
            not_guilty_count = sum(1 for v in final_votes if v.verdict.value == 'not_guilty')
            verdict_section += f"  Final Vote: {guilty_count} Guilty, {not_guilty_count} Not Guilty\n"
        
        with open(self.transcript_file, 'a') as f:
            f.write(verdict_section)
    
    def _count_statements(self) -> int:
        """Count the number of statements in the transcript"""
        # This is a simple implementation - could be enhanced
        with open(self.transcript_file, 'r') as f:
            content = f.read()
        # Count timestamp patterns
        import re
        return len(re.findall(r'\[\d{2}:\d{2}:\d{2}\]', content))
    
    def get_transcript_path(self) -> str:
        """Get the path to the transcript file"""
        return str(self.transcript_file)
    
    def save_json_summary(self):
        """Save a JSON summary alongside the transcript"""
        summary = {
            "session_id": self.session_id,
            "case_title": self.case.case_title,
            "location": f"{self.county}, {self.state}",
            "date": self.start_time.isoformat(),
            "duration_minutes": (datetime.utcnow() - self.start_time).total_seconds() / 60,
            "juror_count": len(self.jurors),
            "voting_rounds": self.current_voting_round,
            "transcript_file": self.transcript_file.name
        }
        
        json_file = self.transcript_file.with_suffix('.json')
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)