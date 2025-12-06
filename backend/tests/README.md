# FreudLaw Backend Tests

This directory contains all test files for the FreudLaw backend.

## Test Files

- `test_data_collection.py` - Tests for data collection endpoints
- `test_juror_generation.py` - Basic juror generation tests
- `test_juror_visual.py` - Visual output test for juror generation
- `test_complete_data_integration.py` - Integration tests for all data sources

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_juror_generation.py

# Run visual test
python tests/test_juror_visual.py
```