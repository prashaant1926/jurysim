#!/usr/bin/env python3
"""
Basic test to verify TranscriptManager works correctly
"""
from app.models.deliberation import (
    DeliberationCase, JurorPersona, JurorStatement, Vote, 
    DeliberationPhase, VerdictChoice
)
from app.services.transcript_manager import TranscriptManager
from pathlib import Path
import json
from datetime import datetime

def test_transcript_manager():
    """Test basic TranscriptManager functionality"""
    
    # Create test case
    case = DeliberationCase(
        case_type="theft",
        case_title="Test Case: State v. Smith",
        summary="Test case for transcript system",
        key_evidence=["Evidence 1", "Evidence 2", "Evidence 3"],
        prosecution_argument="Test prosecution argument",
        defense_argument="Test defense argument",
        jury_instructions="Test instructions",
        requires_unanimous=True
    )
    
    # Create test jurors
    jurors = [
        JurorPersona(
            juror_id=1,
            name="John Doe",
            demographics={"age": 35, "gender": "Male", "race": "White", "education_level": "College", "income": 75000},
            personality={"openness": 3.5, "conscientiousness": 4.0, "extraversion": 3.0, "agreeableness": 3.5, "neuroticism": 2.5},
            attitudes={"political_view": 4}
        ),
        JurorPersona(
            juror_id=2,
            name="Jane Smith",
            demographics={"age": 42, "gender": "Female", "race": "Black", "education_level": "High School", "income": 45000},
            personality={"openness": 4.0, "conscientiousness": 3.5, "extraversion": 4.0, "agreeableness": 4.5, "neuroticism": 3.0},
            attitudes={"political_view": 3}
        )
    ]
    
    # Create transcript manager
    tm = TranscriptManager(
        session_id="test-session-123",
        case=case,
        jurors=jurors,
        county="San Francisco",
        state="CA"
    )
    
    print(f"✓ TranscriptManager created")
    print(f"  Transcript file: {tm.transcript_file.name}")
    
    # Test phase marker
    tm.add_phase_marker(DeliberationPhase.OPENING)
    print(f"✓ Added phase marker")
    
    # Test adding statements
    statement1 = JurorStatement(
        juror_id=1,
        juror_name="John Doe",
        phase=DeliberationPhase.OPENING,
        content="I think we need to carefully consider all the evidence.",
        sentiment="neutral"
    )
    tm.add_statement(statement1)
    print(f"✓ Added statement from John Doe")
    
    statement2 = JurorStatement(
        juror_id=2,
        juror_name="Jane Smith",
        phase=DeliberationPhase.OPENING,
        content="I agree. The prosecution has to prove guilt beyond reasonable doubt.",
        sentiment="agreeable"
    )
    tm.add_statement(statement2)
    print(f"✓ Added statement from Jane Smith")
    
    # Test voting round
    votes = [
        Vote(
            juror_id=1,
            juror_name="John Doe",
            verdict=VerdictChoice.NOT_GUILTY,
            confidence=0.8,
            reasoning="The evidence doesn't prove guilt beyond reasonable doubt",
            round_number=1
        ),
        Vote(
            juror_id=2,
            juror_name="Jane Smith",
            verdict=VerdictChoice.UNDECIDED,
            confidence=0.5,
            reasoning="I need more discussion before deciding",
            round_number=1
        )
    ]
    tm.add_voting_round(votes)
    print(f"✓ Added voting round")
    
    # Test verdict
    tm.add_verdict("not_guilty", votes)
    print(f"✓ Added verdict")
    
    # Save JSON summary
    tm.save_json_summary()
    print(f"✓ Saved JSON summary")
    
    # Check files exist
    if tm.transcript_file.exists():
        print(f"\n✓ Transcript file exists: {tm.transcript_file}")
        print(f"  Size: {tm.transcript_file.stat().st_size} bytes")
        
        # Show content
        print("\nTranscript content preview:")
        print("-" * 60)
        with open(tm.transcript_file, 'r') as f:
            content = f.read()
            print(content[:1000] + "..." if len(content) > 1000 else content)
        print("-" * 60)
    else:
        print(f"\n✗ Transcript file not found")
    
    json_file = tm.transcript_file.with_suffix('.json')
    if json_file.exists():
        print(f"\n✓ JSON summary exists: {json_file}")
        with open(json_file, 'r') as f:
            summary = json.load(f)
        print(f"  Contents: {json.dumps(summary, indent=2)}")
    else:
        print(f"\n✗ JSON summary not found")

if __name__ == "__main__":
    test_transcript_manager()