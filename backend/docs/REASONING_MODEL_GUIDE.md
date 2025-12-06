# DeepSeek Reasoning Model Integration Guide

## Overview
The `deepseek-reasoner` model provides Chain of Thought (CoT) reasoning before delivering final answers, making it ideal for complex jury deliberation simulations.

## Key Differences from Regular Chat Model

### 1. **Model Name**
```python
# Old
model="deepseek-chat"

# New
model="deepseek-reasoner"
```

### 2. **No Temperature/Top_p Parameters**
The reasoning model doesn't support:
- `temperature`
- `top_p`
- `presence_penalty`
- `frequency_penalty`

### 3. **Reasoning Content Output**
```python
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[...],
    max_tokens=4000  # Supports up to 64K
)

# Access reasoning process
reasoning_content = response.choices[0].message.reasoning_content
final_answer = response.choices[0].message.content
```

### 4. **Multi-round Conversations**
- Only the `content` (final answer) should be added to conversation history
- The `reasoning_content` should NOT be included in subsequent messages
- This keeps the context focused on decisions, not the reasoning process

## Benefits for Jury Deliberation

1. **Better Vote Confidence**: The reasoning model can better calculate confidence levels based on its internal reasoning
2. **More Nuanced Arguments**: Jurors can develop more sophisticated legal arguments
3. **Consistent Character**: Better maintains juror personality throughout deliberation
4. **Reduced JSON Errors**: More reliable at producing valid JSON for voting

## Implementation Status

✅ Created `ai_juror_agent_reasoning.py` with reasoning model support
✅ Updated `deliberation_engine_v2.py` to use reasoning agents
✅ Removed unsupported parameters (temperature, etc.)
✅ Added reasoning content logging for debugging

## Usage Example

```python
from app.services.ai_juror_agent_reasoning import AIJurorAgentReasoning

# Create juror with reasoning capabilities
agent = AIJurorAgentReasoning(persona, case)

# Generate statement with chain of thought
statement = await agent.generate_statement(
    phase=DeliberationPhase.DISCUSSION,
    previous_statements=recent_statements
)

# Cast vote with reasoning
vote = await agent.cast_vote(round_number=1)
```

## Expected Improvements

1. **Voting Accuracy**: Should reduce the "50% undecided" errors
2. **Deliberation Quality**: More thoughtful, legally-grounded arguments
3. **Character Consistency**: Better roleplay based on juror backgrounds
4. **Confidence Levels**: More meaningful confidence percentages based on actual reasoning

## Notes

- Max tokens increased to 4000 for statements (reasoning model supports up to 64K)
- Reasoning content is logged for debugging but not shown to users
- Fallback mechanisms still in place for error handling