
# Makefile for common tasks

.PHONY: lint test clean install pre-commit install-hooks

# Install dependencies
install:
	@pip install -r requirements.txt

# Lint all Python files in the repository
lint:
	@pylint pipeline --rcfile=.pylintrc

# Run all tests (unit and integration)
test:
	@pytest --maxfail=1 --disable-warnings -q

# Clean up Python cache files
clean:
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete

# Run pre-commit hooks
pre-commit:
	@pre-commit run --all-files

# Install pre-commit hooks into the git repo
install-hooks:
	@pre-commit install

