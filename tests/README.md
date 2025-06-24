# Eagle Test Suite

This directory contains the comprehensive test suite for Eagle, the natural language platform for orchestrating custom, evolving AI agents.

## Test Structure

```
tests/
├── README.md              # This file
├── __init__.py            # Test package initialization
├── test_config.py         # Configuration system tests
├── test_cli.py            # Command-line interface tests
├── test_interpreter.py    # Core interpreter functionality tests
├── test_tools.py          # Tool system and registry tests
└── test_integration.py    # End-to-end integration tests
```

## Test Categories

### Unit Tests

**test_config.py**
- Configuration loading and validation
- Default configuration verification
- Config file precedence (project vs user home)
- Error handling for invalid configurations

**test_cli.py** 
- Command-line argument parsing
- Subcommand routing (run, init, capabilities, etc.)
- Flag handling (--verbose, --context, --provider, etc.)
- Help message content verification

**test_interpreter.py**
- Interpreter initialization with different providers
- Content enhancement with additional context
- Tool permission system
- Rule loading and system prompt building
- Error handling for missing API keys

**test_tools.py**
- Tool registry functionality
- Tool base class behavior
- Built-in tool validation
- OpenAI and Anthropic function format generation
- Tool loading from directories

### Integration Tests

**test_integration.py**
- Complete .caw file execution workflows
- Tool execution with permission handling
- Context injection end-to-end
- Verbose mode output verification
- Error handling scenarios

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Or using pytest
pytest

# Or using make
make test
```

### Specific Test Categories

```bash
# Unit tests only
make test-unit

# Integration tests only
make test-integration

# With coverage report
make test-coverage
```

### Individual Test Files

```bash
# Run specific test file
python run_tests.py test_config
pytest tests/test_config.py

# Run specific test class
pytest tests/test_cli.py::TestCLI

# Run specific test method
pytest tests/test_cli.py::TestCLI::test_run_caw_file_basic
```

## Test Dependencies

The test suite requires the following packages:

```bash
# Install test dependencies
pip install -e ".[test]"

# Or install development dependencies (includes testing)
pip install -e ".[dev]"
```

**Core test dependencies:**
- `pytest>=7.0.0` - Test framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `pytest-mock>=3.10.0` - Enhanced mocking capabilities

## Writing Tests

### Test Guidelines

1. **Follow naming conventions**: Test files should start with `test_`, test classes with `Test`, and test methods with `test_`

2. **Use descriptive test names**: Test method names should clearly describe what is being tested
   ```python
   def test_cli_accepts_verbose_flag(self):  # Good
   def test_verbose(self):                   # Too vague
   ```

3. **Structure tests with AAA pattern**:
   - **Arrange**: Set up test data and mocks
   - **Act**: Execute the code being tested  
   - **Assert**: Verify the expected behavior

4. **Mock external dependencies**: Use `unittest.mock` to isolate units under test
   ```python
   @patch('eagle_lang.interpreter.OpenAI')
   def test_interpreter_initialization(self, mock_openai):
       # Test implementation
   ```

5. **Test both success and failure cases**: Include positive tests and error handling tests

### Example Test Structure

```python
import unittest
from unittest.mock import patch, MagicMock
from eagle_lang.module import ClassUnderTest

class TestClassUnderTest(unittest.TestCase):
    """Test cases for ClassUnderTest."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = {"key": "value"}
    
    def tearDown(self):
        """Clean up after tests."""
        # Reset any global state
        pass
    
    @patch('eagle_lang.module.external_dependency')
    def test_method_with_external_dependency(self, mock_dependency):
        """Test method behavior with mocked dependency."""
        # Arrange
        mock_dependency.return_value = "expected_result"
        instance = ClassUnderTest()
        
        # Act
        result = instance.method_under_test()
        
        # Assert
        self.assertEqual(result, "expected_result")
        mock_dependency.assert_called_once()
```

## Mocking Strategies

### Common Mock Patterns

**File operations:**
```python
@patch('builtins.open', new_callable=mock_open, read_data="file content")
def test_file_reading(self, mock_file):
    # Test file reading logic
```

**Environment variables:**
```python
@patch('os.getenv')
def test_environment_config(self, mock_getenv):
    mock_getenv.return_value = "test_value"
    # Test logic that uses environment variables
```

**API clients:**
```python
@patch('eagle_lang.interpreter.OpenAI')
def test_ai_provider_interaction(self, mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    # Test AI provider interactions
```

## Coverage Goals

- **Unit tests**: Aim for >90% line coverage on core modules
- **Integration tests**: Cover major user workflows and error scenarios
- **Tool tests**: Each built-in tool should have comprehensive tests

## Continuous Integration

Tests are designed to run in CI environments with:
- No external network dependencies (all API calls mocked)
- No file system side effects (temporary directories used)
- Deterministic behavior (no random elements)

## Debugging Tests

```bash
# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb

# Run specific test with debug output
pytest tests/test_config.py::TestConfig::test_load_config_default_fallback -v -s
```

## Performance Testing

While not included in the current suite, consider adding performance tests for:
- Large .caw file processing
- Tool registry with many tools
- Configuration loading with complex rule sets

## Contributing Test Cases

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure new code maintains coverage levels
3. Add both positive and negative test cases
4. Update this documentation if adding new test categories
5. Run the full test suite before submitting changes

```bash
# Before submitting changes
make test
make lint
```