# Installation Guide

Get RxFlow Pharmacy Assistant up and running in your environment with this comprehensive installation guide.

## 📋 **Prerequisites**

Before installing RxFlow, ensure you have the following prerequisites:

### System Requirements

=== "Python Environment"
    - **Python 3.8+** (Python 3.9+ recommended)
    - **pip** package manager
    - **Git** for version control

=== "Operating Systems"
    - **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+
    - **macOS**: 10.14+ (Mojave or newer)
    - **Windows**: 10+ with WSL2 (recommended) or native

=== "Hardware"
    - **RAM**: 4GB minimum, 8GB recommended
    - **Storage**: 2GB available space
    - **Network**: Internet connection for API services

### API Keys Required

!!! warning "API Configuration"
    RxFlow requires the following API keys for full functionality:
    
    - **OpenAI API Key** - For LLM processing (GPT-4)
    - **RxNorm API** - For medication verification (free NIH service)
    - Optional: **GoodRx API** - For prescription pricing

## 🚀 **Quick Installation**

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/zarreh/rxflow-pharmacy-assistant.git
cd rxflow-pharmacy-assistant
```

### 2. Set Up Python Environment

=== "Using Poetry (Recommended)"
    ```bash
    # Install Poetry if not already installed
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Install dependencies
    poetry install
    
    # Activate the virtual environment
    poetry shell
    ```

=== "Using pip + venv"
    ```bash
    # Create virtual environment
    python3 -m venv rxflow-env
    
    # Activate virtual environment
    # On Linux/macOS:
    source rxflow-env/bin/activate
    # On Windows:
    # rxflow-env\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    ```

=== "Using conda"
    ```bash
    # Create conda environment
    conda create -n rxflow python=3.9
    conda activate rxflow
    
    # Install dependencies
    pip install -r requirements.txt
    ```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit the configuration file
nano .env  # or use your preferred editor
```

**Required Configuration:**
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
APP_NAME=RxFlow Pharmacy Assistant
LOG_LEVEL=INFO

# Optional: Database Configuration
# DATABASE_URL=postgresql://user:pass@localhost/rxflow

# Optional: External APIs
# GOODRX_API_KEY=your_goodrx_key_here
```

### 4. Verify Installation

```bash
# Run basic tests
python -m pytest tests/ -v

# Start the application
streamlit run app.py
```

Navigate to `http://localhost:8501` to verify the installation.

## 🔧 **Advanced Installation Options**

### Docker Installation

For containerized deployment:

```bash
# Build the Docker image
docker build -t rxflow-pharmacy-assistant .

# Run the container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key_here \
  rxflow-pharmacy-assistant
```

### Development Installation

For contributors and developers:

```bash
# Install with development dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install

# Run development server with auto-reload
streamlit run app.py --server.runOnSave=true
```

## 🛠️ **Dependencies Overview**

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ^1.28.0 | Web interface framework |
| `langchain` | ^0.0.350 | AI agent orchestration |
| `openai` | ^1.0.0 | LLM integration |
| `pydantic` | ^2.0.0 | Data validation |
| `requests` | ^2.31.0 | HTTP client for APIs |

### Optional Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | ^2.1.0 | Data analysis and reporting |
| `plotly` | ^5.17.0 | Interactive visualizations |
| `python-dotenv` | ^1.0.0 | Environment management |

## 📊 **Installation Verification**

After installation, verify everything is working:

### 1. Check System Health

```bash
# Run the system check script
python scripts/health_check.py
```

Expected output:
```
✅ Python version: 3.9.x
✅ Dependencies installed
✅ API keys configured
✅ Mock data loaded
✅ All systems operational
```

### 2. Test Core Functionality

```bash
# Test conversation manager
python -c "
from rxflow.workflow.conversation_manager import ConversationManager
cm = ConversationManager()
print('✅ Conversation manager initialized')
"

# Test patient tools
python -c "
from rxflow.tools.patient_history_tool import PatientHistoryTool
tool = PatientHistoryTool()
result = tool.get_medication_history('omeprazole')
print('✅ Patient tools working:', result.get('success', False))
"
```

### 3. Access the Web Interface

1. Start the application: `streamlit run app.py`
2. Open browser to `http://localhost:8501`
3. Try the quick action: "I need to refill my medication"
4. Verify you receive an AI response

## 🚨 **Troubleshooting**

### Common Issues

=== "Import Errors"
    ```bash
    # Issue: ModuleNotFoundError
    # Solution: Ensure virtual environment is activated
    which python  # Should point to your venv
    pip list | grep streamlit  # Verify installation
    ```

=== "API Key Errors"
    ```bash
    # Issue: Invalid API key
    # Check environment variables
    echo $OPENAI_API_KEY
    
    # Verify .env file is loaded
    python -c "from rxflow.config.settings import get_settings; print(get_settings().openai_api_key[:10])"
    ```

=== "Port Already in Use"
    ```bash
    # Issue: Streamlit port 8501 busy
    # Use different port
    streamlit run app.py --server.port 8502
    
    # Or kill existing process
    pkill -f streamlit
    ```

### Getting Help

If you encounter issues:

1. **Check Logs**: Look in `logs/` directory for error details
2. **GitHub Issues**: [Report bugs](https://github.com/zarreh/rxflow-pharmacy-assistant/issues)
3. **Documentation**: Review [troubleshooting guide](../user-guide/interface.md#troubleshooting)

## ⚡ **Performance Optimization**

### For Production Deployment

```bash
# Install production dependencies
pip install gunicorn uvicorn

# Optimize Python
export PYTHONOPTIMIZE=1

# Configure logging
export LOG_LEVEL=WARNING
```

### For Development

```bash
# Enable debug mode
export LOG_LEVEL=DEBUG

# Use development server
streamlit run app.py --server.runOnSave=true --server.address=0.0.0.0
```

## 🎉 **Next Steps**

Once installation is complete:

1. **[Quick Start Guide](quickstart.md)** - Learn basic usage patterns
2. **[Configuration Guide](configuration.md)** - Customize your setup
3. **[User Guide](../user-guide/interface.md)** - Master the interface
4. **[API Reference](../api/conversation-manager.md)** - Explore the APIs

---

!!! success "Installation Complete!"
    You're ready to start using RxFlow! Head to the [Quick Start Guide](quickstart.md) to begin your first prescription refill workflow.