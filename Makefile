# RxFlow Pharmacy Assistant - Makefile
# Easy commands for development, testing, and deployment

.PHONY: help install lint format test run clean check setup dev

# Default target
help: ## Show this help message
	@echo "🚀 RxFlow Pharmacy Assistant - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📝 Examples:"
	@echo "  make run          # Start the Streamlit app"
	@echo "  make test         # Run all tests"
	@echo "  make lint         # Run linting checks"
	@echo "  make format       # Format code automatically"
	@echo "  make check        # Run linting + tests"

# Environment setup
setup: ## Set up the development environment
	@echo "🔧 Setting up development environment..."
	poetry install
	@echo "✅ Environment setup complete!"

install: setup ## Alias for setup

# Development server
run: ## Start the Streamlit application
	@echo "🚀 Starting RxFlow Streamlit app..."
	poetry run streamlit run app.py

dev: run ## Alias for run

# Code quality
lint: ## Run linting checks (flake8, black --check, isort --check)
	@echo "🔍 Running linting checks..."
	@echo "📋 Running flake8..."
	poetry run flake8 rxflow/ app.py --max-line-length=88 --extend-ignore=E203,W503 || true
	@echo ""
	@echo "🎨 Checking code formatting with black..."
	poetry run black --check --diff rxflow/ app.py *.py || true
	@echo ""
	@echo "📦 Checking import sorting with isort..."
	poetry run isort --check-only --diff rxflow/ app.py *.py || true
	@echo ""
	@echo "🔍 Running mypy type checking..."
	poetry run mypy rxflow/ --ignore-missing-imports || true

format: ## Format code automatically (black, isort)
	@echo "🎨 Formatting code..."
	poetry run black rxflow/ app.py *.py
	poetry run isort rxflow/ app.py *.py
	@echo "✅ Code formatting complete!"

# Testing
test: ## Run all tests
	@echo "🧪 Running tests..."
	@echo "📋 Testing project setup..."
	poetry run python test_setup.py
	@echo ""
	@echo "💬 Testing conversation chains..."
	poetry run python test_conversation_chains.py
	@echo ""
	@echo "🔗 Testing Streamlit integration..."
	poetry run python test_streamlit_integration.py
	@echo ""
	@echo "🧠 Testing intelligent conversation..."
	poetry run python test_intelligent_conversation.py
	@echo ""
	@echo "✅ All tests completed!"

test-chains: ## Run only conversation chain tests
	@echo "💬 Testing conversation chains..."
	poetry run python test_conversation_chains.py

test-setup: ## Run only setup tests
	@echo "📋 Testing project setup..."
	poetry run python test_setup.py

test-integration: ## Run only integration tests
	@echo "🔗 Testing Streamlit integration..."
	poetry run python test_streamlit_integration.py

test-intelligent: ## Run intelligent conversation tests
	@echo "🧠 Testing intelligent conversation..."
	poetry run python test_intelligent_conversation.py

test-simple: ## Run simple conversation tests
	@echo "💬 Testing simple conversation..."
	poetry run python test_simple_conversation.py

# Quality assurance
check: lint test ## Run linting and tests (CI pipeline)
	@echo ""
	@echo "✅ All quality checks passed!"

# Utility commands
clean: ## Clean up temporary files and caches
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Environment management
env-info: ## Show environment information
	@echo "🔍 Environment Information:"
	@echo "Python version: $$(poetry run python --version)"
	@echo "Poetry version: $$(poetry --version)"
	@echo "Virtual environment: $$(poetry env info --path)"
	@echo "Dependencies:"
	@poetry show --tree

deps-update: ## Update dependencies
	@echo "📦 Updating dependencies..."
	poetry update
	@echo "✅ Dependencies updated!"

deps-add: ## Add a new dependency (usage: make deps-add PACKAGE=package_name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "❌ Error: Please specify PACKAGE=package_name"; \
		echo "Example: make deps-add PACKAGE=requests"; \
		exit 1; \
	fi
	poetry add $(PACKAGE)

# Development tools
jupyter: ## Start Jupyter notebook server
	@echo "📓 Starting Jupyter notebook server..."
	poetry run jupyter notebook

shell: ## Open Poetry shell
	@echo "🐚 Opening Poetry shell..."
	poetry shell

# Docker commands (if using Docker in the future)
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t rxflow-pharmacy-assistant .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -p 8501:8501 rxflow-pharmacy-assistant

# Git helpers
git-status: ## Show git status with helpful info
	@echo "📊 Git Status:"
	git status --short --branch
	@echo ""
	@echo "📝 Recent commits:"
	git log --oneline -5

commit: ## Interactive git commit (usage: make commit MSG="commit message")
	@if [ -z "$(MSG)" ]; then \
		echo "📝 Staging all changes and opening interactive commit..."; \
		git add -A; \
		git commit; \
	else \
		echo "📝 Committing with message: $(MSG)"; \
		git add -A; \
		git commit -m "$(MSG)"; \
	fi

# Production helpers
requirements: ## Generate requirements.txt from Poetry
	@echo "📋 Generating requirements.txt..."
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	@echo "✅ requirements.txt generated!"

security: ## Run security checks
	@echo "🔒 Running security checks..."
	poetry run safety check
	poetry run bandit -r rxflow/ -f json || true

# Performance and profiling
profile: ## Profile the application performance
	@echo "⚡ Profiling application..."
	poetry run python -m cProfile -s cumulative test_conversation_chains.py

# Documentation
docs: ## Generate documentation (placeholder)
	@echo "📚 Documentation generation not yet implemented"
	@echo "💡 Future: Sphinx documentation generation"

# Advanced development
debug: ## Run app in debug mode with verbose logging
	@echo "🐛 Starting app in debug mode..."
	RXFLOW_LOG_LEVEL=DEBUG poetry run streamlit run app.py

watch: ## Watch for changes and restart (requires entr)
	@echo "👀 Watching for changes (requires 'entr' to be installed)..."
	find . -name "*.py" | entr -r make run

# Version management
version: ## Show current version info
	@echo "📋 Version Information:"
	@echo "Project: $$(poetry version)"
	@echo "Python: $$(poetry run python --version)"
	@echo "Streamlit: $$(poetry run streamlit version)"

bump-patch: ## Bump patch version
	poetry version patch
	@echo "✅ Version bumped to: $$(poetry version --short)"

bump-minor: ## Bump minor version
	poetry version minor
	@echo "✅ Version bumped to: $$(poetry version --short)"

bump-major: ## Bump major version
	poetry version major
	@echo "✅ Version bumped to: $$(poetry version --short)"

# Quick development workflow
quick-check: format lint test-chains ## Quick development check (format + lint + test chains)
	@echo ""
	@echo "✅ Quick check completed successfully!"

full-check: format lint test ## Full development check (format + lint + all tests)
	@echo ""
	@echo "🎉 Full check completed successfully!"

# Installation of development tools
install-dev-tools: ## Install additional development tools
	@echo "🔧 Installing development tools..."
	pip install flake8 black isort mypy safety bandit
	@echo "✅ Development tools installed!"