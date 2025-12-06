# Evidence Flow in Jury Deliberation System

## 1. Case Definition
Cases are defined in `DeliberationCase` objects with:
- `case_type`: Type of crime (murder, theft, assault, etc.)
- `case_title`: Full case name
- `summary`: Brief description
- `key_evidence`: List of evidence items as strings
- `prosecution_argument`: Prosecution's interpretation
- `defense_argument`: Defense's interpretation
- `jury_instructions`: Legal instructions

## 2. Evidence Presentation to Jurors

### In System Prompt (ai_juror_agent.py)
Evidence is numbered and presented in the system prompt:
```
KEY EVIDENCE PRESENTED:
1. Security camera footage showing defendant in store
2. Receipt showing no purchase of items found
3. Defendant's explanation that items were a gift
4. No witness saw defendant take items
```

### Opening Statements
Jurors are prompted to reference specific evidence:
- "Looking at ALL the evidence presented (witness testimony, video footage, physical evidence), what's your initial reaction? Reference specific evidence items. Keep response under 20 words."

### Evidence Review Phase
- "Which specific piece of evidence troubles you most? Be specific and concise (under 20 words)."

## 3. Evidence Reference Format
Jurors should reference evidence by number:
- "Evidence #1 shows..."
- "The video footage (#3)..."
- "Looking at evidence #2, the receipt doesn't prove..."

## 4. Implementation Status
- ✅ Evidence properly structured in DeliberationCase
- ✅ Evidence numbered in system prompt
- ✅ Prompts require specific evidence references
- ✅ Converted from Anthropic to DeepSeek API
- ✅ Token limits set for concise responses (40-50 tokens)