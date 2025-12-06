#!/usr/bin/env python3
"""
Debug script to test for duplicate statement callbacks
"""
import asyncio
from app.models.deliberation import DeliberationCase, JurorStatement, DeliberationPhase
from app.services.juror_generator import JurorGenerator
from app.services.responsive_deliberation_engine import ResponsiveDeliberationEngine

# Track callbacks
callback_count = 0
statements_seen = set()

def on_statement_callback(statement: JurorStatement):
    global callback_count
    callback_count += 1
    
    # Create a unique key for this statement
    key = f"{statement.timestamp}_{statement.juror_name}_{statement.content[:50]}"
    
    if key in statements_seen:
        print(f"\n!!! DUPLICATE DETECTED !!!")
        print(f"Statement: {statement.juror_name} at {statement.timestamp}")
        print(f"Content: {statement.content[:50]}...")
        print(f"This is callback #{callback_count}")
    else:
        statements_seen.add(key)
        print(f"✓ New statement #{callback_count}: {statement.juror_name}")

async def test_duplicates():
    # Create a simple test case
    case = DeliberationCase(
        case_type="theft",
        case_title="Test Case",
        summary="Test for duplicate callbacks",
        key_evidence=["Evidence 1", "Evidence 2"],
        prosecution_argument="Test prosecution",
        defense_argument="Test defense",
        jury_instructions="Test instructions",
        requires_unanimous=True
    )
    
    # Generate jurors
    generator = JurorGenerator()
    jurors = generator.generate_jury_pool("San Francisco", "CA", 3)  # Just 3 jurors for quick test
    
    print(f"Generated {len(jurors)} jurors")
    
    # Create engine
    engine = ResponsiveDeliberationEngine(
        case=case,
        jurors=jurors,
        county="San Francisco",
        state="CA",
        on_statement=on_statement_callback
    )
    
    # Run just the opening statements
    print("\nRunning opening statements...")
    await engine._run_opening_statements()
    
    print(f"\nTotal callbacks received: {callback_count}")
    print(f"Unique statements seen: {len(statements_seen)}")
    
    if callback_count > len(statements_seen):
        print("\n⚠️  DUPLICATES CONFIRMED!")
        print(f"Received {callback_count - len(statements_seen)} duplicate callbacks")
    else:
        print("\n✅ No duplicates detected")

if __name__ == "__main__":
    asyncio.run(test_duplicates())