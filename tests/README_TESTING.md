# Testing Guide

This document provides information about the test suite for the timeline-reporter project.

## Overview

The test suite follows Python best practices and includes:

- **Unit tests** for individual client components
- **Integration tests** showing how clients work together
- **Comprehensive mocking** of external dependencies
- **Code coverage reporting**
- **Parameterized tests** for various input scenarios
- **Error handling tests** for robust code

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_integration.py      # Integration tests
└── clients/
    ├── __init__.py
    ├── test_mongodb.py      # MongoDB client tests
    ├── test_openai.py       # OpenAI client tests
    ├── test_perplexity.py   # Perplexity client tests
    └── test_pinecone.py     # Pinecone client tests
```

## Running Tests

### Prerequisites

Install testing dependencies:

```bash
pip install -r requirements.txt
```

### Basic Usage

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=clients --cov-report=term-missing
```

### Using the Test Runner

The project includes a convenience script:

```bash
# Run all tests
python run_tests.py

# Run only client tests
python run_tests.py --type clients

# Run integration tests
python run_tests.py --type integration

# Run without coverage
python run_tests.py --no-coverage

# Verbose output
python run_tests.py --verbose
```

### Specific Test Categories

Run only unit tests:

```bash
pytest -m unit
```

Run only integration tests:

```bash
pytest -m integration
```

Run specific test files:

```bash
pytest tests/clients/test_mongodb.py
pytest tests/clients/test_openai.py -v
```

## Test Features

### Comprehensive Mocking

All external dependencies are mocked:

- HTTP requests (httpx, requests)
- Database connections (MongoDB, Pinecone)
- API clients (OpenAI, Perplexity)
- Environment variables

### Test Fixtures

Shared fixtures in `conftest.py`:

- `mock_environment_variables`: Auto-mocked environment variables
- `sample_vector`: Sample embedding vector for tests
- `sample_article_data`: Sample article data structure
- `sample_research_prompt`: Sample research query

### Error Handling

Tests cover various error scenarios:

- Missing API keys
- Network failures
- Invalid responses
- Malformed data
- Authentication errors

### Coverage Goals

- **Target**: 85% minimum coverage
- **Current focus**: Client modules
- **Reports**: Terminal output + HTML (htmlcov/)

## Test Best Practices Followed

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive test names**: Clear purpose description
3. **Independent tests**: No test dependencies
4. **Parameterized tests**: Multiple input scenarios
5. **Proper mocking**: External dependencies isolated
6. **Error testing**: Both success and failure paths
7. **Documentation**: Docstrings for all test classes/methods

## Configuration

Test configuration in `pytest.ini`:

- Test discovery patterns
- Coverage settings
- Warning filters
- Custom markers

## Continuous Integration

The test suite is designed for CI/CD:

- No external dependencies required
- Fast execution through mocking
- Clear pass/fail criteria
- Coverage reporting integration

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're in the project root
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Environment variables**: Tests use mocked values automatically

### Debug Mode

Run tests with more verbose output:

```bash
pytest -vvv --tb=long
```

Show print statements:

```bash
pytest -s
```

### Coverage Issues

Generate detailed HTML coverage report:

```bash
pytest --cov=clients --cov-report=html
# Open htmlcov/index.html in browser
```
