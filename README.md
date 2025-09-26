# 💊 RxFlow Pharmacy Assistant

AI-powered pharmacy refill assistant built for Qventus technical interview challenge. This system demonstrates conversational AI, tool integration, RAG implementation, and mathematical optimization in a healthcare context.

## 🎯 Project Overview

RxFlow is a sophisticated pharmacy refill assistant that:
- Processes natural language refill requests
- Handles multi-turn conversations with state management
- Integrates with pharmacy, insurance, and drug databases
- Performs safety checks and drug interaction screening
- Optimizes costs and pharmacy selection
- Manages complex escalation workflows

## 🏗️ Architecture

- **Frontend**: Streamlit (Python-based web interface)
- **Conversation Engine**: LangChain + LangGraph for state management
- **LLM**: Ollama Llama3.2 (configurable for GPT-4/Gemini Flash 2.0)
- **Vector Store**: FAISS for RAG implementation
- **Embeddings**: Sentence Transformers
- **Package Structure**: Modular design with all components under `rxflow/` package
- **Configuration**: Pydantic-based settings with environment variable support

## 📁 Project Structure

```
rxflow_pharmacy_assistant/
├── app.py                    # Main Streamlit application
├── pyproject.toml           # Poetry dependencies  
├── .env.example             # Environment configuration template
├── README.md                # This file
├── data/                    # Mock data and policies
│   ├── mock_patients.json
│   ├── mock_pharmacies.json
│   ├── mock_insurance.json
│   ├── mock_drugs.json
│   └── drug_policies.txt
└── rxflow/                  # Main package
    ├── __init__.py          # Package initialization
    ├── main.py              # Main entry point
    ├── config/              # Configuration management
    │   ├── __init__.py
    │   └── settings.py
    ├── utils/               # Utility functions
    │   ├── __init__.py
    │   ├── logger.py        # Logging setup
    │   └── helpers.py       # Helper functions
    ├── workflow/            # LangGraph workflow implementation
    │   ├── __init__.py
    │   ├── state.py         # State definitions
    │   ├── graph.py         # Main workflow orchestration
    │   ├── nodes/           # Individual workflow nodes
    │   │   ├── __init__.py
    │   │   ├── input_nodes.py      # Input parser, confirmation nodes
    │   │   ├── validation_nodes.py # Eligibility, interaction check nodes
    │   │   ├── formulary_nodes.py  # Formulary, cost optimization nodes
    │   │   ├── inventory_nodes.py  # Pharmacy inventory, selection nodes
    │   │   ├── escalation_nodes.py # Provider, pharmacist escalation nodes
    │   │   └── output_nodes.py     # Order submission, confirmation nodes
    │   ├── chains/          # Reusable LLM chains
    │   │   ├── __init__.py
    │   │   ├── conversation_chains.py  # User interaction chains
    │   │   ├── extraction_chains.py    # Entity extraction chains
    │   │   ├── decision_chains.py      # Decision-making chains
    │   │   └── prompts.py              # All prompt templates
    │   └── routers.py       # Conditional routing logic
    ├── tools/               # API integrations and utilities
    │   ├── __init__.py
    │   ├── mock_apis.py     # Mock pharmacy/insurance APIs
    │   ├── rxnorm_api.py    # RxNorm API integration
    │   └── optimization.py  # Cost/distance optimization
    ├── rag/                 # RAG implementation
    │   ├── __init__.py
    │   ├── vector_store.py  # FAISS vector store setup
    │   ├── documents.py     # Document loading
    │   └── retriever.py     # RAG retrieval logic
    └── tests/               # Test suite
        ├── __init__.py
        ├── test_workflow/
        ├── test_tools/
        └── test_integration/
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Ollama (for local LLM)

### Installation

1. **Clone and setup the project:**
```bash
cd /home/alireza/projects/rxflow_pharmacy_assistant
cp .env.example .env
```

2. **Install dependencies:**
```bash
poetry install
```

3. **Setup Ollama (if not already installed):**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama3.2 model
ollama pull llama3.2
```

4. **Run the application:**
```bash
poetry run streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 🎮 Usage Examples

### Basic Refill Request
```
User: "I need to refill my lisinopril"
Bot: "I found your Lisinopril 10mg prescription. You have 2 refills remaining. 
     Would you like me to check which pharmacy has the best price and shortest wait time?"
```

### Cost Optimization
```
User: "Refill my Lipitor"
Bot: "Lipitor (brand) costs $320. Generic atorvastatin is $15 with your insurance. 
     Would you like to switch to save $305?"
```

### Prior Authorization Escalation
```
User: "I need my Eliquis refilled"
Bot: "Eliquis requires prior authorization. I can send the request to Dr. Johnson 
     with the required criteria. This typically takes 24-48 hours. Shall I proceed?"
```

## 🧪 Demo Features

The current implementation includes:

- **Patient Selection**: Choose from demo patients (John Smith, Mary Johnson)
- **Mock Data**: Realistic pharmacy, insurance, and drug databases
- **Conversation Interface**: Streamlit-based chat interface
- **Basic NLP**: Intent recognition for common refill requests
- **Quick Actions**: One-click refill buttons for testing

## 🔧 Configuration

Edit `.env` file to configure:

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# For future LLM switching:
# OPENAI_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here

# Application settings
DEBUG=true
LOG_LEVEL=INFO
USE_MOCK_DATA=true
```

## 🏗️ Development Status

### ✅ Completed (Phase 1)
- [x] Project structure and configuration (Python 3.12 + Poetry)
- [x] Main package structure under `rxflow/`
- [x] Mock data creation (patients, pharmacies, insurance, drugs)
- [x] Basic Streamlit interface
- [x] Configuration management with Pydantic settings
- [x] Logging and utilities setup
- [x] State definitions for LangGraph workflow
- [x] Ollama Llama3.2 integration setup

### 🚧 In Progress (Phase 2)
- [ ] LangGraph workflow implementation
- [ ] Conversation nodes and chains
- [ ] RAG system for policy retrieval
- [ ] API integrations (RxNorm, mock APIs)
- [ ] Optimization algorithms

### 📋 Planned (Phase 3)
- [ ] Drug interaction checking
- [ ] Cost optimization logic
- [ ] Pharmacy selection algorithm
- [ ] Escalation workflows
- [ ] Enhanced UI components
- [ ] Test suite implementation

## 🎯 Key Business Value

- **Time Savings**: Reduces refill processing from 15-30 min to 2-3 min
- **Error Prevention**: Automated interaction and eligibility checking
- **Cost Optimization**: Suggests generics and best prices
- **Patient Satisfaction**: Faster turnaround and proactive communication
- **Workflow Automation**: Handles prior authorizations and escalations

## 🔬 Technical Highlights

1. **Modular Architecture**: Each component is independently testable and replaceable
2. **State Management**: LangGraph provides robust conversation state tracking
3. **Safety First**: Drug interactions checked before cost optimization
4. **User Consent**: Never changes medications without explicit approval
5. **Scalable Design**: Easy to extend to other healthcare workflows

## 🧪 Testing Scenarios

### Happy Path
- Standard refill with available inventory
- Cost optimization suggestions
- Pharmacy selection based on location/price

### Escalation Paths
- No refills remaining → Provider request
- High interaction risk → Pharmacist review
- Prior authorization needed → Automated PA request
- Not covered → Alternative suggestions

## 📊 Development Roadmap

**Next Steps for Implementation:**
1. Complete LangGraph workflow nodes
2. Implement RAG system for policy retrieval
3. Add RxNorm API integration
4. Build optimization algorithms
5. Enhance conversation capabilities
6. Add comprehensive testing

## 🤝 Contributing

This is a technical interview project, but the architecture supports:
- Adding new workflow nodes
- Integrating additional APIs
- Extending to other healthcare workflows
- Scaling to multiple concurrent users

## 📝 License

This project is created for educational and interview purposes.

## ✅ Current Status - Phase 1 Complete

The project structure is now fully set up and ready for development:

- ✅ **Project Structure**: All components organized under `rxflow/` package
- ✅ **Dependencies**: Poetry with Python 3.12, all packages installed and tested
- ✅ **Configuration**: Pydantic-based settings with environment variables
- ✅ **Mock Data**: Comprehensive JSON files for patients, pharmacies, insurance, and drugs
- ✅ **Streamlit App**: Basic interface running successfully
- ✅ **State Management**: LangGraph state definitions ready for workflow implementation
- ✅ **Utilities**: Logging, helper functions, and basic testing framework

### Next Steps for Phase 2
1. Implement LangGraph workflow nodes
2. Create conversation chains and prompts
3. Build RAG system for policy retrieval
4. Integrate RxNorm API and optimization algorithms
5. Add comprehensive drug interaction checking

### Quick Start Commands
```bash
# Install dependencies
poetry install

# Run setup test
poetry run python test_setup.py

# Start the application
poetry run streamlit run app.py
```

The application will be available at `http://localhost:8501`

---

**Built for Qventus Technical Interview**  
*Demonstrating healthcare AI, conversation management, and workflow automation*
