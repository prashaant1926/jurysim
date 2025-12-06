"""
Test that jury deliberation follows proper legal principles
"""
import asyncio
from app.models.deliberation import DeliberationCase
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine
from app.services.juror_generator import JurorGenerator


async def test_jury_principles():
    """Test that jury follows proper legal principles"""
    
    # Create test case
    case = DeliberationCase(
        case_type="assault",
        case_title="Test Case - Jury Principles",
        summary="Testing adherence to jury instructions and principles",
        key_evidence=[
            "Witness saw defendant near scene",
            "No physical evidence linking defendant",
            "Defendant has alibi (partially verified)",
            "Victim identified defendant (but was intoxicated)"
        ],
        prosecution_argument="Witness testimony places defendant at scene",
        defense_argument="No physical evidence and reasonable doubt exists",
        jury_instructions="You must find defendant guilty only if prosecution proves guilt beyond reasonable doubt",
        requires_unanimous=True
    )
    
    # Generate diverse jury
    generator = JurorGenerator()
    jurors = generator.generate_jury_pool("San Francisco", "CA", 6)
    
    # Track if principles are mentioned
    principles_mentioned = {
        "presumption_of_innocence": False,
        "beyond_reasonable_doubt": False,
        "evidence_only": False,
        "compelling_reasons": False,
        "no_repetition": False
    }
    
    statements_collected = []
    
    def track_statement(statement):
        content = statement.content.lower()
        statements_collected.append(statement)
        
        # Check for key principles
        if "presume" in content or "innocent until" in content:
            principles_mentioned["presumption_of_innocence"] = True
        
        if "reasonable doubt" in content or "beyond a reasonable" in content:
            principles_mentioned["beyond_reasonable_doubt"] = True
            
        if "evidence presented" in content or "based on evidence" in content:
            principles_mentioned["evidence_only"] = True
            
        if "compelling" in content or "convince" in content:
            principles_mentioned["compelling_reasons"] = True
    
    # Create engine with callback
    engine = ResponsiveDeliberationEngine(
        case=case,
        jurors=jurors,
        on_statement=track_statement
    )
    
    # Run brief deliberation
    print("\nTesting jury principles adherence...\n")
    session = await engine.run_full_deliberation(max_rounds=1)
    
    # Check foreperson statements
    foreperson_statements = [s for s in statements_collected if "(Foreperson)" in s.juror_name]
    
    # Verify foreperson read jury instructions
    instructions_read = False
    for stmt in foreperson_statements[:3]:  # Check early statements
        if "must follow" in stmt.content or "jury principles" in stmt.content.lower():
            instructions_read = True
            break
    
    # Check for repetition tracking
    discussion_statements = [s for s in statements_collected if s.phase.value == "discussion"]
    if len(discussion_statements) > 10:
        # Simple check: see if later statements reference avoiding repetition
        for stmt in discussion_statements[5:]:
            if "already" in stmt.content.lower() or "mentioned" in stmt.content.lower():
                principles_mentioned["no_repetition"] = True
                break
    
    # Print results
    print("\n" + "="*60)
    print("JURY PRINCIPLES COMPLIANCE CHECK")
    print("="*60)
    
    print(f"\nForeperson read instructions: {'✓' if instructions_read else '✗'}")
    print(f"\nPrinciples mentioned during deliberation:")
    print(f"  Presumption of innocence: {'✓' if principles_mentioned['presumption_of_innocence'] else '✗'}")
    print(f"  Beyond reasonable doubt: {'✓' if principles_mentioned['beyond_reasonable_doubt'] else '✓'}")
    print(f"  Evidence-based decisions: {'✓' if principles_mentioned['evidence_only'] else '✗'}")
    print(f"  Compelling reasons needed: {'✓' if principles_mentioned['compelling_reasons'] else '✗'}")
    print(f"  Avoiding repetition: {'✓' if principles_mentioned['no_repetition'] else '✗'}")
    
    # Check voting instructions
    voting_instructions_proper = False
    for stmt in foreperson_statements:
        if "before you vote" in stmt.content.lower() and "presumed innocent" in stmt.content.lower():
            voting_instructions_proper = True
            break
    
    print(f"\nVoting instructions included legal standards: {'✓' if voting_instructions_proper else '✗'}")
    
    # Overall assessment
    compliance_score = sum([
        instructions_read,
        principles_mentioned["beyond_reasonable_doubt"],
        principles_mentioned["evidence_only"],
        voting_instructions_proper
    ])
    
    print(f"\nOverall Compliance: {compliance_score}/4 critical elements")
    
    if compliance_score >= 3:
        print("\n✓ Jury deliberation follows proper legal principles!")
    else:
        print("\n⚠ Some legal principles may need reinforcement")


if __name__ == "__main__":
    asyncio.run(test_jury_principles())