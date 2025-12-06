# Fixed: Physical Gestures Still Appearing in Responses

## The Problem
Despite previous attempts, jurors were still including physical actions:
```
*Leans back in chair, rubbing chin thoughtfully*
*Taps finger on table*
*Turns to others*
```

## Root Cause
The reasoning model agent (`ai_juror_agent_reasoning.py`) was missing explicit instructions to avoid physical gestures. While we fixed the "gut" repetition issue, we didn't add the no-gesture rule.

## What I Fixed

### 1. **Updated Base System Prompt** (`app/models/deliberation.py`):
Added explicit instruction:
```
NO PHYSICAL ACTIONS: Do not include gestures in asterisks like *leans forward*, 
*taps finger*, *adjusts glasses*. Just speak naturally.
```

### 2. **Updated Reasoning Agent** (`app/services/ai_juror_agent_reasoning.py`):
- Added gesture removal to main prompt
- Added to speech reminder: "NO physical gestures (*leans*, *taps*, etc.)"

### 3. **Already Fixed in DeepSeek Agent** (`app/services/ai_juror_agent_deepseek.py`):
This already had the instruction but wasn't being used by the v2 engine.

## Why This Happened
- The v2 engine uses the reasoning agent
- The reasoning agent had different prompts than the regular agent
- When we fixed gestures before, we only updated one agent

## Expected Results

**Before:**
```
*Leans forward thoughtfully*
Look, what's bugging me is...
*Taps finger on table*
```

**After:**
```
Look, what's bugging me is the gap between what the prosecution 
claims and what we actually saw.
```

## Files Updated
- `app/models/deliberation.py` - Base persona system prompt
- `app/services/ai_juror_agent_reasoning.py` - Reasoning model prompts

The deliberations should now be gesture-free and focus on natural dialogue!