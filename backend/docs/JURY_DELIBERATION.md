# AI Jury Deliberation System

## Overview

The AI Jury Deliberation System simulates realistic jury discussions using Claude AI agents. Each juror is generated based on real demographic data and has unique personalities, attitudes, and deliberation styles.

## Features

- **Realistic Jurors**: Generated from Census, GSS, and election data
- **AI-Powered Discussions**: Each juror uses Claude to generate contextual responses
- **Multiple Phases**: Opening statements, evidence review, discussion, and voting
- **Interactive CLI**: Color-coded jurors with real-time deliberation display
- **Case Types**: Theft, assault, and murder cases with different evidence

## Running a Deliberation

### Quick Start

```bash
python run_deliberation.py
```

### Interactive Options

1. **Choose Location**:
   - San Francisco, CA (Liberal)
   - Maricopa, AZ (Purple/Swing)
   - Oklahoma, OK (Conservative)

2. **Select Case Type**:
   - Theft
   - Assault
   - Murder

3. **Watch Deliberation**:
   - Jurors introduce themselves
   - Review evidence
   - Discuss the case
   - Vote on verdict

## System Architecture

### Components

1. **Juror Generation** (`juror_generator.py`):
   - Creates 12 diverse jurors based on county demographics
   - Integrates Census API, GSS attitudes, and personality traits

2. **AI Juror Agent** (`ai_juror_agent.py`):
   - Converts juror profile to AI persona
   - Generates contextual statements
   - Casts votes with reasoning

3. **Deliberation Engine** (`deliberation_engine.py`):
   - Orchestrates turn-taking
   - Manages deliberation phases
   - Tracks votes and determines verdict

4. **CLI Interface** (`deliberation_interface.py`):
   - Color-coded display
   - Real-time statement rendering
   - Vote tracking and visualization

### Deliberation Flow

1. **Opening Statements**: Each juror shares initial impressions
2. **Evidence Review**: Discuss key evidence pieces
3. **Discussion Rounds**: Natural back-and-forth debate
4. **Voting**: Secret ballot with confidence levels
5. **Verdict**: Unanimous or hung jury

## Juror Personalities

Each juror has:
- **Demographics**: Age, gender, race, education, income
- **Attitudes**: Political views, death penalty stance, etc.
- **Personality**: Big Five traits affecting behavior
- **Deliberation Style**: Leader, consensus-seeker, skeptic, etc.

## Example Output

```
[14:23:45] Sarah Johnson (assertive)
          As a 45-year-old teacher, I've seen how young people can make 
          mistakes. The evidence doesn't convince me beyond reasonable doubt.

[14:23:52] Michael Rodriguez (challenging)  
          I disagree. The security footage clearly shows the defendant
          taking the items. That's theft, plain and simple.

[14:24:01] Linda Chen (uncertain)
          I'm not sure... Could someone else have placed those items?
          The footage isn't perfectly clear.
```

## Customization

### Adding New Cases

Edit `SAMPLE_CASES` in `deliberation_interface.py`:

```python
"new_case": DeliberationCase(
    case_type="fraud",
    case_title="State v. Smith - Wire Fraud",
    summary="...",
    key_evidence=["..."],
    prosecution_argument="...",
    defense_argument="...",
    jury_instructions="...",
    requires_unanimous=True
)
```

### Adjusting Deliberation Length

In `run_deliberation()`, change `max_rounds`:
```python
session = await engine.run_deliberation(max_rounds=5)  # More rounds
```

## API Usage

The system uses the Anthropic API with Claude 3 Sonnet. Ensure your API key is set in `.env`:

```
ANTHROPIC_API_KEY=your-key-here
```

## Performance Notes

- Each juror statement takes ~1-2 seconds to generate
- A full deliberation with 12 jurors takes ~10-15 minutes
- API costs: ~$0.10-0.20 per full deliberation

## Troubleshooting

### "API Key Invalid"
- Check `.env` file has correct `ANTHROPIC_API_KEY`

### "Rate Limited"
- The system includes delays between API calls
- Reduce juror count or add longer delays if needed

### "Import Error"
- Ensure you're in the `backend/` directory
- Install requirements: `pip install -r requirements.txt`