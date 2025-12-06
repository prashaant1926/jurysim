"""
Demo of how the discussion tracker guides jurors to avoid repetition
"""
from app.services.discussion_tracker import DiscussionTracker

def demo_discussion_tracker():
    """Show how the tracker guides discussion"""
    tracker = DiscussionTracker()
    
    print("DISCUSSION TRACKER DEMO")
    print("="*60)
    
    # Simulate some juror statements
    statements = [
        ("John", "The DNA evidence #1 is compelling - 1 in 170 million is hard to ignore. Also, the blood trail #2 seems damning."),
        ("Mary", "I agree about the DNA #1, but what about the glove #3 not fitting? That's a huge problem for the prosecution."),
        ("Bob", "Yeah, the 1 in 170 million DNA match is strong. But the timeline #9 is tight - only 25 minutes to do all that?"),
        ("Sarah", "Everyone keeps saying 1 in 170 million, but evidence #5 shows Martin was unarmed. That matters to me."),
    ]
    
    print("\nSimulating juror statements...\n")
    
    for name, statement in statements:
        print(f"{name}: {statement}")
        tracker.update_from_statement(name, statement)
        
        # Show what guidance the next speaker would get
        guidance = tracker.get_guidance_for_next_speaker("Next Speaker")
        print(f"  → Guidance for next: {guidance}")
        print()
    
    # Show final analysis
    print("="*60)
    print("TRACKER ANALYSIS:")
    print("="*60)
    
    print(f"\nEvidence mentioned: {sorted(tracker.evidence_mentioned)}")
    print(f"\nEvidence mention counts:")
    for num, count in sorted(tracker.evidence_mention_count.items()):
        print(f"  Evidence #{num}: {count} times")
    
    print(f"\nCommon phrases detected: {len(tracker.common_phrases_used)}")
    
    # Show what guidance a new speaker would get
    print("\nGuidance for next speaker:")
    guidance = tracker.get_guidance_for_next_speaker("New Juror")
    print(f"  {guidance}")
    
    # Test if evidence should be mentioned again
    print("\nShould mention evidence #1 again?", tracker.should_mention_evidence(1))
    print("Should mention evidence #10?", tracker.should_mention_evidence(10))

if __name__ == "__main__":
    demo_discussion_tracker()