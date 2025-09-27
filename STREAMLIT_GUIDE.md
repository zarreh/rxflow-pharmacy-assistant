# 🚀 Using the RxFlow Streamlit App with Intelligent Conversations

## Quick Start

1. **Start the app:**
   ```bash
   make run
   # or: poetry run streamlit run app.py
   ```

2. **Access the app:**
   - Open your browser to: `http://localhost:8501`

## � How to Have Natural Conversations

### Natural Conversation Flow
The intelligent conversation system adapts to your needs:

1. **Just Talk Naturally** - Start however feels natural:
   - "I need to refill my lisinopril 10mg"
   - "Can you help me with my prescription?"
   - "What pharmacies do you recommend?"
   - "How much will my medication cost?"

2. **System Remembers Context** - No need to repeat information:
   - Remembers your medication name and dosage
   - Tracks pharmacy preferences
   - Knows conversation history

3. **Intelligent Guidance** - AI guides you naturally:
   - Asks clarifying questions when needed
   - Suggests next steps contextually  
   - Provides relevant information at the right time

4. **Flexible Conversation** - Handle any order of topics:
   - Cost questions before pharmacy selection
   - Insurance questions at any time
   - Multiple medications in one conversation

### � Conversation Intelligence
The app intelligently tracks your conversation:
- **🏁 Getting started** - Understanding your initial request
- **❓ Understanding request** - Clarifying what you need
- **📝 Gathering details** - Collecting medication information
- **💊 Medication confirmed** - Confirmed medication and dosage
- **🏪 Selecting pharmacy** - Finding the right pharmacy
- **💰 Reviewing costs** - Discussing pricing and insurance
- **⚠️ Consulting pharmacist** - Escalating complex issues
- **✅ Process complete** - Successfully processed refill

### ⚠️ Special Cases (Escalation)
Handle complex scenarios:
- **No refills remaining:** "I have no refills left"
- **Prior authorization:** "My insurance needs authorization"
- **Prescription questions:** "Is this medication right for me?"

### 🎛️ App Features

#### Sidebar Controls
- **Patient Selection:** Choose demo patient profiles
- **Settings Display:** Current LLM and configuration
- **Clear Conversation:** Reset to start fresh

#### Quick Actions Panel
- **🔄 New Conversation:** Reset conversation state
- **💊 Example Refills:** Try common medications
- **⚠️ Test Escalations:** Try special scenarios

## 🧪 Example Conversations

Try these natural conversation starters:

```
"I need to refill my lisinopril 10mg"
→ AI confirms medication, discusses pharmacy options and pricing

"What pharmacies do you recommend?"  
→ AI provides pharmacy options with locations and pricing

"How much will this cost with my insurance?"
→ AI discusses insurance coverage and cost optimization

"Can you help me with my prescription refill?"
→ AI asks clarifying questions to understand your needs

"I think I'm out of refills"
→ AI helps you contact prescriber for new prescription

"What's the difference between generic and brand name?"
→ AI explains options and potential savings
```

## 🔧 Technical Details

### Intelligent Conversation System
- **LLM-Powered:** Uses Ollama/Llama 3.2 for natural language understanding
- **Context Memory:** Maintains conversation history and extracted entities
- **Smart Routing:** Automatically determines conversation status and next steps
- **Async Processing:** Non-blocking conversation processing for smooth UX
- **Error Recovery:** Robust fallbacks and graceful error handling

### Mock Data Integration
- **Patient Profiles:** Realistic demo patients with insurance
- **Pharmacy Network:** Multiple locations with pricing
- **Medication Database:** Common prescriptions with interactions
- **Insurance Plans:** Various coverage scenarios

### Real-time Features
- **Live Chain Responses:** Direct LLM integration via Ollama
- **Dynamic Routing:** Intelligent conversation flow management
- **Context Preservation:** Maintains conversation history and state
- **Interactive UI:** Real-time updates and status tracking

## 🎯 Next Steps

This integrated frontend demonstrates the core conversation chains in action. The next phase will include:

1. **LangGraph Workflow Integration:** Full workflow nodes with conditional routing
2. **Advanced RAG:** Vector search for medication interactions and guidelines
3. **Multi-turn Conversations:** Complex conversation management
4. **Production Features:** Authentication, real pharmacy APIs, EHR integration

The conversation chains provide the foundation for building a complete AI-powered pharmacy refill assistant!