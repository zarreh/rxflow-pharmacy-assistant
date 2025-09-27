# 🛠️ Development with Makefile

## Quick Commands

```bash
# Get help and see all available commands
make help

# 🚀 Run the application
make run                # Start Streamlit app
make dev                # Alias for run

# 🧪 Testing
make test               # Run all tests
make test-chains        # Test conversation chains only
make test-integration   # Test Streamlit integration
make quick-check        # Format + lint + test chains
make full-check         # Format + lint + all tests

# 🎨 Code Quality
make format             # Auto-format with black & isort
make lint               # Run linting (flake8, black, isort, mypy)
make check              # Run linting + all tests (CI pipeline)

# 🔧 Environment
make setup              # Set up development environment
make clean              # Clean temporary files
make env-info          # Show environment details
```

## Most Used Commands

### Development Workflow
```bash
# Start development
make setup              # First time setup
make run                # Start the app

# Before committing
make format             # Format code
make quick-check        # Quick validation
```

### Testing
```bash
make test-chains        # Fast: test core functionality
make test               # Full: all tests
```

### Quality Assurance
```bash
make lint               # Check code quality
make format             # Fix formatting issues
make check              # Full CI pipeline check
```

## Advanced Commands

### Git Integration
```bash
make git-status         # Enhanced git status
make commit MSG="fix: update chains"  # Quick commit
```

### Version Management
```bash
make version            # Show current versions
make bump-patch         # Increment patch version
```

### Dependencies
```bash
make deps-update        # Update all dependencies  
make deps-add PACKAGE=requests  # Add new package
```

### Development Tools
```bash
make debug              # Run with debug logging
make profile            # Performance profiling
make security           # Security checks
```

## Command Details

### `make run`
- Starts Streamlit app at `http://localhost:8501`
- Uses Poetry virtual environment
- Includes all conversation chains

### `make test`
- Runs setup validation
- Tests conversation chains
- Tests Streamlit integration
- Shows detailed output

### `make lint`
- **flake8**: Style and error checking
- **black --check**: Code formatting verification
- **isort --check**: Import sorting verification  
- **mypy**: Type checking (with warnings)

### `make format`
- **black**: Auto-formats Python code
- **isort**: Sorts and organizes imports
- Safe to run anytime

### `make check`
- Complete CI pipeline simulation
- Runs linting + all tests
- Use before pushing code

## Tips

1. **Daily Development**: `make run` to start, `make test-chains` to validate
2. **Before Commit**: `make format` then `make quick-check`
3. **CI/CD Ready**: `make check` simulates full pipeline
4. **Debugging**: `make debug` for verbose logging
5. **Clean Slate**: `make clean` removes cached files

The Makefile provides a consistent, easy-to-use interface for all development tasks!