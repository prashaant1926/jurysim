# Fixed the "My Gut" Repetition Problem

## The Issue
All jurors were saying variations of "my gut" constantly:
- "My gut's telling me..."
- "My gut reaction is..." 
- "So my gut? When I see..."

This made them sound like robots using the same script.

## What I Fixed

### 1. **Updated Base System Prompts**
- Removed examples that used "gut" language
- Added emphasis on VARIED language
- Explicitly told AI not to repeat phrases

### 2. **Created Unique Speech Patterns for Each Juror**
Added `_get_speech_patterns()` method that creates different speech based on:
- **Age**: Older people say "back in my day", younger say "like, honestly"
- **Education**: College grads avoid slang, high school dropouts use "ain't"
- **Personality**: Blunt people say "that's wrong", quiet people wait their turn

### 3. **Individual Speech Reminders**
Each juror now gets a custom prompt based on their persona:
- 65-year-old: "Start with phrases like 'Back when I...' or 'Now listen here...'"
- 25-year-old: "Use modern casual speech: 'Honestly...', 'I'm not gonna lie...'"
- Working class: "Use working-class speech: 'Look here...', 'That ain't right...'"

### 4. **Banned Repetitive Phrases**
Explicitly told the AI: "DO NOT use 'gut' phrases - vary your language!"

## Expected Results

**Before:**
```
Juror 1: "My gut's telling me he's guilty..."
Juror 2: "My gut reaction is doubt..."
Juror 3: "So my gut? When I see this..."
```

**After:**
```
65-year-old: "Back in my day, if you took something without paying..."
25-year-old: "Honestly, this whole thing seems sketchy..."
Working class: "Look, I work construction and this don't add up..."
```

## Files Updated
- `app/models/deliberation.py` - Base speech guidelines
- `app/services/ai_juror_agent_reasoning.py` - Individual speech patterns
- `app/services/deliberation_engine_v2.py` - Speech pattern generation

## Key Principle
Each juror should sound like a **different real person** with their own:
- Vocabulary level
- Regional phrases  
- Age-appropriate language
- Education level
- Personal speech habits

NOT everyone using the same "gut reaction" template!