# Integration Tests

This directory contains integration tests for the jury deliberation system.

## Test Files

### Core Functionality Tests
- `test_deliberation.py` - Main deliberation engine test
- `test_simple_agent.py` - Basic AI agent functionality
- `test_foreperson_fix.py` - Foreperson selection and moderation
- `test_reduced_repetition.py` - Discussion tracker and repetition reduction

### Model Tests
- `test_deepseek_api.py` - DeepSeek API integration
- `test_reasoning_model.py` - Juror reasoning model
- `test_model_availability.py` - Model availability checks

### Dialogue Quality Tests
- `test_natural_dialogue.py` - Natural speech patterns
- `test_no_gestures.py` - Gesture removal verification
- `test_juror_length.py` - Response length testing

### Performance Tests
- `test_quick_deliberation.py` - Quick deliberation runs
- `test_deliberation_auto.py` - Automated deliberation testing

### Feature Tests
- `test_improved_deliberation.py` - Enhanced deliberation features
- `test_dynamics_demo.py` - Jury dynamics demonstration
- `test_tracker_demo.py` - Discussion tracker demonstration

## Running Tests

Run individual tests:
```bash
python tests/integration/test_simple_agent.py
```

Run all integration tests:
```bash
python -m pytest tests/integration/
```