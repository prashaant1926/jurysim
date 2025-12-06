"""Demonstrate the improved jury dynamics without running full simulation"""
from app.services.juror_generator import JurorGenerator
from app.services.deliberation_engine_v2 import ImprovedDeliberationEngine
from app.cli.deliberation_interface import SAMPLE_CASES
from app.models.deliberation import JurorPersona
import json

# Generate jury
generator = JurorGenerator()
jurors = generator.generate_jury_pool("San Francisco", "CA", 12)

# Create engine
engine = ImprovedDeliberationEngine(
    case=SAMPLE_CASES["theft"],
    jurors=jurors
)

print("IMPROVED JURY DYNAMICS DEMONSTRATION")
print("=" * 50)

# Show how personas are enriched
print("\n1. ENRICHED JUROR PERSONAS:")
print("-" * 30)
for persona in engine.juror_personas[:3]:
    print(f"\n{persona.name} (Juror #{persona.juror_id}):")
    print(f"  Background: {persona.background_story}")
    print(f"  Speaking style: {persona.speaking_style}")
    print(f"  Decision approach: {persona.decision_making_approach}")
    print(f"  Deliberation traits: {', '.join(persona.deliberation_traits[:2])}")
    print(f"  Initial bias: {persona.case_biases.get('initial_lean', 'neutral')} - {persona.case_biases.get('reason', 'no specific reason')}")

# Show leader identification
print("\n\n2. NATURAL LEADERS IDENTIFIED:")
print("-" * 30)
leaders = engine._identify_leaders()
for leader_id in leaders:
    leader = next(p for p in engine.juror_personas if p.juror_id == leader_id)
    print(f"  {leader.name}: {leader.deliberation_traits[0]}")

# Show how diverse speakers are selected
print("\n\n3. DIVERSE SPEAKER SELECTION:")
print("-" * 30)
speakers = engine._select_diverse_speakers()
print("Selected speakers represent different viewpoints:")
for speaker_id in speakers:
    speaker = next(p for p in engine.juror_personas if p.juror_id == speaker_id)
    print(f"  {speaker.name}: {speaker.case_biases.get('initial_lean', 'neutral')} leaning")

# Show voting bloc logic
print("\n\n4. VOTING BLOC DYNAMICS:")
print("-" * 30)
print("After votes, jurors would be grouped into:")
print("  - Guilty bloc: Will argue strongly for conviction")
print("  - Not guilty bloc: Will challenge prosecution's case") 
print("  - Undecided: Will ask probing questions")
print("\nThis creates realistic faction debates instead of random discussion")

# Show improved prompting
print("\n\n5. IMPROVED AI PROMPTING:")
print("-" * 30)
print("Old approach: Generic 'share your thoughts'")
print("New approach: Direct engagement between jurors")
print("\nExample prompts used:")
print('  - "Make a strong argument for why the defendant is guilty. Address the doubters directly."')
print('  - "You\'re undecided. Ask pointed questions about the evidence that concern you."')
print('  - "Respond directly to what [Juror Name] just said. Build on or challenge their points."')

print("\n\n6. KEY IMPROVEMENTS SUMMARY:")
print("-" * 30)
print("✓ Jurors have realistic backgrounds and speaking styles")
print("✓ Natural leaders emerge and guide discussion")
print("✓ Voting blocs form and debate as factions")
print("✓ Direct juror-to-juror interactions by name")
print("✓ Progressive voting with confidence changes")
print("✓ Final push arguments before hung jury")

print("\n\nThis creates a much more realistic and engaging jury deliberation simulation!")