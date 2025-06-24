# Eagle Development Makefile

.PHONY: test test-unit test-integration test-coverage install install-dev clean lint format

# Test commands
test:
	python run_tests.py

test-unit:
	python -m pytest tests/test_config.py tests/test_cli.py tests/test_interpreter.py tests/test_tools.py -v

test-integration: 
	python -m pytest tests/test_integration.py -v

test-coverage:
	python -m pytest --cov=eagle_lang --cov-report=html --cov-report=term tests/

# Installation commands
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-test:
	pip install -e ".[test]"

# Code quality
lint:
	flake8 src/eagle_lang --max-line-length=100
	mypy src/eagle_lang --ignore-missing-imports

format:
	black src/eagle_lang tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build and distribution
build:
	python -m build

publish-test:
	python -m twine upload --repository testpypi dist/*

publish:
	python -m twine upload dist/*

# Help
help:
	@echo "Eagle Development Commands:"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"  
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo ""
	@echo "Installation:"
	@echo "  install        - Install Eagle in development mode"
	@echo "  install-dev    - Install with development dependencies"
	@echo "  install-test   - Install with test dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run linting (flake8, mypy)"
	@echo "  format         - Format code with black"
	@echo ""
	@echo "Build:"
	@echo "  build          - Build distribution packages"
	@echo "  clean          - Clean build artifacts"
	@echo ""
	@echo "Publishing:"
	@echo "  publish-test   - Publish to TestPyPI"
	@echo "  publish        - Publish to PyPI"