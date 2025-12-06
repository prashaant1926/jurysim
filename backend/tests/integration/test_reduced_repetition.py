"""
Test if the discussion tracker reduces repetition in deliberations
"""
import asyncio
from app.cli.deliberation_interface import SAMPLE_CASES
from app.services.juror_generator import JurorGenerator
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine
from app.models.deliberation import JurorStatement
from collections import Counter
import re

async def test_repetition_reduction():
    """Test if jurors avoid repeating the same points"""
    generator = JurorGenerator()
    
    # Use OJ case for testing
    case = SAMPLE_CASES["oj_simpson"]
    
    # Generate small jury for quick test
    print("Generating jury...")
    jurors = generator.generate_jury_pool("Los Angeles", "CA", 6)
    
    # Track mentions of key phrases
    phrase_counter = Counter()
    evidence_counter = Counter()
    
    def track_statement(statement: JurorStatement):
        if statement.juror_id == 0:  # Skip foreperson
            return
            
        # Track evidence mentions
        evidence_nums = re.findall(r'#(\d+)|Evidence #(\d+)', statement.content)
        for match in evidence_nums:
            num = match[0] or match[1]
            evidence_counter[f"Evidence #{num}"] += 1
        
        # Track common phrases
        if "1 in 170 million" in statement.content:
            phrase_counter["1 in 170 million"] += 1
        if "glove" in statement.content.lower() and "fit" in statement.content.lower():
            phrase_counter["glove doesn't fit"] += 1
        if "25 minutes" in statement.content:
            phrase_counter["25 minutes timeline"] += 1
        if "domestic violence" in statement.content.lower():
            phrase_counter["domestic violence"] += 1
            
        # Print statement preview
        print(f"[{statement.juror_name}]: {statement.content[:100]}...")
    
    # Create engine
    engine = ResponsiveDeliberationEngine(
        case=case,
        jurors=jurors,
        on_statement=track_statement,
        on_vote=lambda v: None
    )
    
    print(f"\nForeperson: {engine.foreperson_name}")
    print("\nRunning opening statements...\n")
    
    try:
        # Just run opening statements to check repetition
        await engine._run_opening_statements()
        
        print("\n" + "="*60)
        print("REPETITION ANALYSIS:")
        print("="*60)
        
        print("\nEvidence Mentions:")
        for evidence, count in evidence_counter.most_common(10):
            print(f"  {evidence}: mentioned {count} times")
        
        print("\nKey Phrase Repetitions:")
        for phrase, count in phrase_counter.items():
            print(f"  '{phrase}': repeated {count} times")
        
        # Check guidance from tracker
        print("\nDiscussion Tracker Guidance:")
        guidance = engine.discussion_tracker.get_discussion_context()
        print(f"  {guidance}")
        
        # Success criteria
        max_mentions = max(evidence_counter.values()) if evidence_counter else 0
        max_phrase_rep = max(phrase_counter.values()) if phrase_counter else 0
        
        print(f"\nResults:")
        print(f"  Most mentioned evidence: {max_mentions} times")
        print(f"  Most repeated phrase: {max_phrase_rep} times")
        
        if max_mentions <= 3 and max_phrase_rep <= 2:
            print("  ✓ Good variety - minimal repetition!")
        else:
            print("  ✗ Too much repetition detected")
            
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_repetition_reduction())