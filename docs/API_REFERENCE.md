# 🔗 RxFlow Pharmacy Assistant - API Reference

**Version 1.0** | **Last Updated:** September 27, 2025

This document provides comprehensive API documentation for all components, classes, methods, and tools in the RxFlow Pharmacy Assistant system.

---

## 📋 Table of Contents

1. [Core Components API](#-core-components-api)
2. [Workflow Management API](#-workflow-management-api)  
3. [Tools API Reference](#-tools-api-reference)
4. [Configuration API](#-configuration-api)
5. [Utilities API](#-utilities-api)
6. [Data Models](#-data-models)
7. [Exception Classes](#-exception-classes)
8. [Type Definitions](#-type-definitions)

---

## 🏗️ Core Components API

### ConversationManager

**Module**: `rxflow.workflow.conversation_manager`

The central orchestrator for all pharmacy conversation workflows.

```python
class AdvancedConversationManager:
    """
    Main conversation management system for pharmacy interactions.
    
    Handles state management, tool execution, and response generation
    using LangChain agents and custom state machines.
    """
```

#### Constructor

```python
def __init__(self) -> None:
    """
    Initialize conversation manager with LLM, state machine, and tools.
    
    Automatically configures:
    - LLM instance from settings
    - State machine for workflow management
    - All 15 specialized pharmacy tools
    - LangChain agent executor
    """
```

#### Core Methods

```python
async def handle_message(
    self,
    user_input: str,
    session_id: str
) -> ConversationResponse:
    """
    Process user message and generate appropriate response.
    
    Args:
        user_input (str): Raw user message input
        session_id (str): Unique session identifier
        
    Returns:
        ConversationResponse: Structured response with state information
        
    Raises:
        ValidationError: If input validation fails
        ProcessingError: If conversation processing fails
        
    Example:
        >>> manager = AdvancedConversationManager()
        >>> response = await manager.handle_message(
        ...     "I need to refill my lisinopril",
        ...     "session_123"
        ... )
        >>> print(response.message)
        "I can help you refill your lisinopril prescription..."
    """
```

```python
def get_conversation_context(self, session_id: str) -> ConversationContext:
    """
    Retrieve current conversation context for session.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        ConversationContext: Current conversation state and data
        
    Raises:
        SessionNotFoundError: If session doesn't exist
    """
```

#### State-Specific Handlers

```python
def _handle_identify_medication(
    self,
    user_input: str,
    context: ConversationContext,
    history: List[BaseMessage]
) -> ConversationResponse:
    """
    Handle medication identification state.
    
    Processes user input to extract medication names using:
    - Keyword pattern matching
    - Dosage detection with regex patterns
    - RxNorm tool integration for validation
    
    Args:
        user_input: Raw user message
        context: Current conversation context
        history: Message history for context
        
    Returns:
        ConversationResponse: Response with medication identification results
    """
```

```python
def _handle_confirm_dosage(
    self,
    user_input: str,
    context: ConversationContext,
    history: List[BaseMessage]
) -> ConversationResponse:
    """
    Handle dosage confirmation and safety validation.
    
    Validates dosage information and checks for:
    - Proper dosage format and ranges
    - Drug interactions and contraindications  
    - Patient allergy and medical history
    
    Args:
        user_input: Raw user message
        context: Current conversation context
        history: Message history for context
        
    Returns:
        ConversationResponse: Response with dosage validation results
    """
```

```python
def _handle_select_pharmacy(
    self,
    user_input: str,
    context: ConversationContext,
    history: List[BaseMessage]
) -> ConversationResponse:
    """
    Handle pharmacy selection and comparison.
    
    Processes pharmacy preferences and provides:
    - Location-based pharmacy search
    - Inventory availability checking
    - Price comparisons across locations
    - Wait time estimates
    
    Args:
        user_input: Raw user message
        context: Current conversation context
        history: Message history for context
        
    Returns:
        ConversationResponse: Response with pharmacy options and details
    """
```

---

## 🔄 Workflow Management API

### RefillStateMachine

**Module**: `rxflow.workflow.state_machine`

Manages conversation state transitions and workflow logic.

```python
class RefillStateMachine:
    """
    State machine for pharmacy refill conversation workflows.
    
    Manages state transitions, session persistence, and conditional logic
    for guiding users through medication refill processes.
    """
```

#### Constructor

```python
def __init__(self) -> None:
    """
    Initialize state machine with predefined transitions and empty sessions.
    
    Sets up:
    - All valid state transitions with conditions
    - Empty session storage dictionary
    - Transition logging configuration
    """
```

#### Core Methods

```python
def transition(
    self,
    session_id: str,
    trigger: str,
    **context_updates
) -> Tuple[bool, ConversationContext]:
    """
    Execute state transition with validation and context updates.
    
    Args:
        session_id (str): Unique session identifier
        trigger (str): Transition trigger name
        **context_updates: Key-value pairs for context updates
        
    Returns:
        Tuple[bool, ConversationContext]: Success status and updated context
        
    Raises:
        InvalidTransitionError: If transition is not valid
        SessionNotFoundError: If session doesn't exist
        
    Example:
        >>> state_machine = RefillStateMachine()
        >>> success, context = state_machine.transition(
        ...     "session_123",
        ...     "medication_identified",
        ...     medication="lisinopril"
        ... )
        >>> assert success
        >>> assert context.medication == "lisinopril"
    """
```

```python
def get_session(self, session_id: str) -> ConversationContext:
    """
    Retrieve conversation context for session.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        ConversationContext: Current session context
        
    Raises:
        SessionNotFoundError: If session doesn't exist
    """
```

```python
def create_session(self, session_id: str, patient_id: str) -> ConversationContext:
    """
    Create new conversation session with initial context.
    
    Args:
        session_id (str): Unique session identifier  
        patient_id (str): Patient identifier
        
    Returns:
        ConversationContext: Newly created session context
        
    Raises:
        SessionExistsError: If session already exists
    """
```

```python
def get_valid_triggers(self, session_id: str) -> List[str]:
    """
    Get list of valid transition triggers for current state.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        List[str]: Available trigger names
    """
```

### State Definitions

**Module**: `rxflow.workflow.workflow_types`

```python
class RefillState(Enum):
    """Enumeration of all possible conversation states."""
    
    START = "start"
    IDENTIFY_MEDICATION = "identify_medication"
    CLARIFY_MEDICATION = "clarify_medication"
    CONFIRM_DOSAGE = "confirm_dosage"
    CHECK_AUTHORIZATION = "check_authorization"
    SELECT_PHARMACY = "select_pharmacy"
    CONFIRM_ORDER = "confirm_order"
    ESCALATE_PA = "escalate_pa"
    COMPLETE = "complete"
    ERROR = "error"
```

```python
@dataclass
class StateTransition:
    """Definition of a state machine transition."""
    
    from_state: RefillState
    to_state: RefillState
    trigger: str
    condition: Callable[[ConversationContext], bool]
    description: str
```

---

## 🛠️ Tools API Reference

### Patient History Tools

#### PatientHistoryTool

**Module**: `rxflow.tools.patient_history_tool`

```python
def get_patient_medication_history(query: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive patient medication history.
    
    Args:
        query (str): Patient identifier or name
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Patient history information
          - patient_id (str): Unique patient identifier
          - current_medications (List[Dict]): Active prescriptions
          - prescription_history (List[Dict]): Historical prescriptions
          - last_refill_dates (Dict): Date of last refills by medication
        - source (str): Data source identifier
        
    Example:
        >>> result = get_patient_medication_history("john_doe")
        >>> if result["success"]:
        ...     medications = result["data"]["current_medications"]
        ...     print(f"Patient has {len(medications)} active medications")
    """
```

#### AdherenceAnalysisTool

```python
def analyze_patient_adherence(query: str) -> Dict[str, Any]:
    """
    Analyze patient medication adherence patterns.
    
    Args:
        query (str): Patient identifier
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Adherence analysis
          - overall_adherence_rate (float): 0-100 percentage
          - medication_adherence (Dict): Per-medication rates
          - missed_doses (int): Recent missed doses
          - adherence_trend (str): "improving"|"stable"|"declining"
          - recommendations (List[str]): Improvement suggestions
        - source (str): "adherence_analysis"
    """
```

#### AllergyCheckTool

```python
def check_patient_allergies(query: str) -> Dict[str, Any]:
    """
    Check patient allergies and contraindications.
    
    Args:
        query (str): Patient identifier or medication name
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Allergy information
          - known_allergies (List[str]): Known medication allergies
          - contraindications (List[str]): Medical contraindications
          - allergy_severity (Dict): Severity levels by allergen
          - safe_alternatives (List[str]): Alternative medications
        - source (str): "allergy_check"
    """
```

### RxNorm Integration Tools

#### RxNormLookupTool

**Module**: `rxflow.tools.rxnorm_tool`

```python
def lookup_medication_rxnorm(query: str) -> Dict[str, Any]:
    """
    Look up medication information using RxNorm database.
    
    Args:
        query (str): Medication name or partial name
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): RxNorm medication data
          - rxcui (str): RxNorm concept identifier
          - name (str): Standardized medication name
          - generic_name (str): Generic equivalent name
          - brand_names (List[str]): Available brand names
          - active_ingredients (List[str]): Active ingredient list
          - drug_class (str): Therapeutic class
          - dosage_forms (List[str]): Available forms
        - source (str): "rxnorm_lookup"
        
    Example:
        >>> result = lookup_medication_rxnorm("lisinopril")
        >>> if result["success"]:
        ...     rxcui = result["data"]["rxcui"]
        ...     print(f"RxCUI: {rxcui}")
    """
```

#### DosageValidationTool

```python
def validate_medication_dosage(query: str) -> Dict[str, Any]:
    """
    Validate medication dosage against standard ranges.
    
    Args:
        query (str): Medication name and dosage (e.g., "lisinopril 10mg")
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Dosage validation results
          - medication (str): Medication name
          - dosage (str): Specified dosage
          - is_valid (bool): Whether dosage is valid
          - standard_range (str): Normal dosage range
          - frequency_valid (bool): Frequency validation
          - safety_warnings (List[str]): Safety concerns
          - recommendations (List[str]): Dosage suggestions
        - source (str): "dosage_validation"
    """
```

#### DrugInteractionTool

```python
def check_drug_interactions(query: str) -> Dict[str, Any]:
    """
    Check for drug-drug interactions.
    
    Args:
        query (str): Medication names separated by commas
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Interaction analysis
          - interactions_found (bool): Whether interactions exist
          - interaction_pairs (List[Dict]): Specific interactions
          - severity_levels (Dict): Severity by interaction
          - clinical_significance (str): Overall significance
          - management_recommendations (List[str]): How to manage
        - source (str): "drug_interactions"
    """
```

### Pharmacy Service Tools

#### PharmacyLocatorTool

**Module**: `rxflow.tools.pharmacy_tools`

```python
def find_nearby_pharmacies(query: str) -> Dict[str, Any]:
    """
    Find pharmacies near specified location.
    
    Args:
        query (str): Location (address, zip code, or "near me")
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Pharmacy location data
          - pharmacies (List[Dict]): Nearby pharmacy list
            - pharmacy_id (str): Unique identifier
            - name (str): Pharmacy name
            - address (str): Full address
            - distance (float): Distance in miles
            - phone (str): Contact number
            - hours (Dict): Operating hours
            - services (List[str]): Available services
          - search_location (str): Searched location
        - source (str): "pharmacy_locator"
    """
```

#### InventoryCheckTool

```python
def check_pharmacy_inventory(query: str) -> Dict[str, Any]:
    """
    Check medication inventory at specific pharmacy.
    
    Args:
        query (str): "medication_name at pharmacy_name" format
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Inventory information
          - medication (str): Medication name
          - pharmacy (str): Pharmacy name
          - in_stock (bool): Availability status
          - quantity_available (int): Available quantity
          - estimated_wait (str): Wait time if not in stock
          - alternative_locations (List[str]): Other locations with stock
        - source (str): "inventory_check"
    """
```

#### WaitTimeEstimatorTool

```python
def estimate_wait_time(query: str) -> Dict[str, Any]:
    """
    Estimate prescription wait time at pharmacy.
    
    Args:
        query (str): Pharmacy name or identifier
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Wait time estimation
          - pharmacy (str): Pharmacy name
          - current_wait (str): Current estimated wait
          - typical_wait (str): Typical wait time
          - busy_periods (List[str]): High-traffic times
          - recommendations (List[str]): Best times to visit
        - source (str): "wait_time_estimate"
    """
```

#### PharmacyInfoTool

```python
def get_pharmacy_details(query: str) -> Dict[str, Any]:
    """
    Get detailed information about specific pharmacy.
    
    Args:
        query (str): Pharmacy name or identifier
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Pharmacy details
          - name (str): Pharmacy name
          - address (str): Full address
          - phone (str): Contact number
          - hours (Dict): Operating hours by day
          - services (List[str]): Available services
          - specialties (List[str]): Special programs
          - insurance_accepted (List[str]): Accepted insurance
          - pharmacy_type (str): Chain/independent classification
        - source (str): "pharmacy_details"
    """
```

### Cost Optimization Tools

#### GoodRxPricingTool

**Module**: `rxflow.tools.cost_tools`

```python
def lookup_goodrx_pricing(query: str) -> Dict[str, Any]:
    """
    Look up GoodRx pricing for medication.
    
    Args:
        query (str): Medication name and dosage
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Pricing information
          - medication (str): Medication name
          - prices_by_pharmacy (Dict): Prices at different pharmacies
          - lowest_price (float): Best available price
          - savings_potential (float): Potential savings amount
          - goodrx_coupon (str): Coupon code if available
          - price_comparison (List[Dict]): Detailed price comparison
        - source (str): "goodrx_pricing"
    """
```

#### InsuranceFormularyTool

```python
def check_insurance_formulary(query: str) -> Dict[str, Any]:
    """
    Check insurance formulary coverage for medication.
    
    Args:
        query (str): "medication_name for insurance_plan" format
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Formulary information
          - medication (str): Medication name
          - insurance_plan (str): Insurance plan name
          - covered (bool): Coverage status
          - tier_level (int): Formulary tier (1-5)
          - copay (float): Patient copay amount
          - prior_auth_required (bool): Prior authorization needed
          - quantity_limits (str): Quantity restrictions
          - alternatives_covered (List[str]): Covered alternatives
        - source (str): "insurance_formulary"
    """
```

#### BrandGenericComparisonTool

```python
def compare_brand_generic(query: str) -> Dict[str, Any]:
    """
    Compare brand name and generic medication options.
    
    Args:
        query (str): Medication name (brand or generic)
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Brand vs generic comparison
          - brand_name (str): Brand name medication
          - generic_name (str): Generic equivalent
          - price_difference (float): Cost difference
          - bioequivalence (str): FDA bioequivalence status
          - brand_price (float): Brand medication price
          - generic_price (float): Generic medication price
          - savings_amount (float): Potential savings
          - recommendation (str): Cost-effectiveness recommendation
        - source (str): "brand_generic_comparison"
    """
```

#### PriorAuthorizationTool

```python
def lookup_prior_authorization(query: str) -> Dict[str, Any]:
    """
    Look up prior authorization requirements and process.
    
    Args:
        query (str): "medication_name for insurance_plan" format
        
    Returns:
        Dict containing:
        - success (bool): Operation success status
        - data (Dict): Prior authorization information
          - medication (str): Medication name
          - insurance_plan (str): Insurance plan
          - pa_required (bool): Whether PA is required
          - pa_criteria (List[str]): Approval criteria
          - required_documentation (List[str]): Needed documents
          - typical_timeline (str): Processing time estimate
          - appeal_process (str): Appeal procedure if denied
          - alternatives (List[str]): Non-PA alternatives
        - source (str): "prior_authorization"
    """
```

### Order Management Tools

#### RefillOrderTool

**Module**: `rxflow.tools.order_tools`

```python
def submit_refill_order(query: str) -> Dict[str, Any]:
    """
    Submit medication refill order to pharmacy.
    
    Args:
        query (str): Structured order information
        
    Returns:
        Dict containing:
        - success (bool): Order submission success
        - data (Dict): Order confirmation
          - order_id (str): Unique order identifier
          - prescription_number (str): Prescription reference
          - medication (str): Medication name and dosage
          - pharmacy (str): Fulfilling pharmacy
          - estimated_ready_time (str): When order will be ready
          - total_cost (float): Order total cost
          - payment_method (str): Payment information
          - pickup_instructions (str): How to collect order
        - source (str): "refill_order_submission"
        
    Example:
        >>> order_data = {
        ...     "medication": "lisinopril 10mg",
        ...     "pharmacy": "CVS Main Street",
        ...     "patient_id": "12345"
        ... }
        >>> result = submit_refill_order(str(order_data))
    """
```

#### OrderTrackingTool

```python
def track_order_status(query: str) -> Dict[str, Any]:
    """
    Track status of existing prescription order.
    
    Args:
        query (str): Order ID or prescription number
        
    Returns:
        Dict containing:
        - success (bool): Tracking success status
        - data (Dict): Order status information
          - order_id (str): Order identifier
          - current_status (str): Current processing status
          - status_history (List[Dict]): Status change timeline
          - estimated_ready (str): Estimated ready time
          - pharmacy_location (str): Fulfillment pharmacy
          - special_instructions (str): Any special notes
          - contact_info (str): Pharmacy contact for questions
        - source (str): "order_tracking"
    """
```

#### OrderCancellationTool

```python
def cancel_prescription_order(query: str) -> Dict[str, Any]:
    """
    Cancel existing prescription order.
    
    Args:
        query (str): Order ID or prescription number to cancel
        
    Returns:
        Dict containing:
        - success (bool): Cancellation success status
        - data (Dict): Cancellation confirmation
          - order_id (str): Cancelled order identifier
          - cancellation_time (str): When cancellation processed
          - refund_amount (float): Refunded amount if applicable
          - refund_method (str): How refund will be processed
          - cancellation_reason (str): Reason for cancellation
        - source (str): "order_cancellation"
        
    Note:
        Orders can typically only be cancelled before pharmacy begins processing.
        Some orders may incur cancellation fees depending on timing.
    """
```

---

## ⚙️ Configuration API

### Settings Management

**Module**: `rxflow.config.settings`

```python
class RxFlowSettings(BaseSettings):
    """
    Application configuration using Pydantic settings.
    
    Automatically loads from environment variables with RXFLOW_ prefix.
    """
    
    # LLM Configuration
    llm_provider: str = Field(default="ollama", description="LLM provider name")
    llm_model: str = Field(default="llama3.2", description="LLM model name")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    # API Configuration
    rxnorm_api_key: Optional[str] = Field(default=None, description="RxNorm API key")
    goodrx_api_key: Optional[str] = Field(default=None, description="GoodRx API key")
    
    # Application Settings
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    
    class Config:
        env_file = ".env"
        env_prefix = "RXFLOW_"
        case_sensitive = False
```

```python
def get_settings() -> RxFlowSettings:
    """
    Get application settings instance.
    
    Returns:
        RxFlowSettings: Configured settings instance
        
    Example:
        >>> settings = get_settings()
        >>> print(settings.llm_provider)
        "ollama"
    """
```

### LLM Configuration

**Module**: `rxflow.llm`

```python
def get_conversational_llm() -> BaseLLM:
    """
    Get configured conversational LLM instance.
    
    Returns:
        BaseLLM: Configured LLM based on settings
        
    Raises:
        ConfigurationError: If LLM configuration is invalid
        ConnectionError: If LLM connection fails
        
    Supported Providers:
        - "ollama": Local Ollama instance
        - "openai": OpenAI GPT models
        - "anthropic": Anthropic Claude models
    """
```

```python
def get_llm_with_tools(tools: List[Tool]) -> AgentExecutor:
    """
    Create LLM agent executor with specified tools.
    
    Args:
        tools (List[Tool]): Tools to make available to agent
        
    Returns:
        AgentExecutor: Configured agent with tools
        
    Example:
        >>> from rxflow.tools import AVAILABLE_TOOLS
        >>> agent = get_llm_with_tools(AVAILABLE_TOOLS)
        >>> response = agent.invoke("Help me refill my medication")
    """
```

---

## 🔧 Utilities API

### Logging

**Module**: `rxflow.utils.logger`

```python
def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger instance.
    
    Args:
        name (str): Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
```

```python
def configure_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    enable_structured: bool = False
) -> None:
    """
    Configure application logging.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string (Optional[str]): Custom format string
        enable_structured (bool): Enable structured JSON logging
    """
```

### Helper Functions

**Module**: `rxflow.utils.helpers`

```python
def parse_medication_dosage(text: str) -> Dict[str, Any]:
    """
    Parse medication and dosage information from text.
    
    Args:
        text (str): Text containing medication and dosage
        
    Returns:
        Dict containing:
        - medication (str): Extracted medication name
        - dosage (Optional[str]): Extracted dosage
        - frequency (Optional[str]): Extracted frequency
        - form (Optional[str]): Medication form (tablet, capsule, etc.)
        
    Example:
        >>> result = parse_medication_dosage("lisinopril 10mg once daily")
        >>> print(result)
        {
            "medication": "lisinopril",
            "dosage": "10mg", 
            "frequency": "once daily",
            "form": None
        }
    """
```

```python
def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format and security.
    
    Args:
        session_id (str): Session identifier to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
```

```python
def sanitize_user_input(user_input: str) -> str:
    """
    Sanitize user input for safety and consistency.
    
    Args:
        user_input (str): Raw user input
        
    Returns:
        str: Sanitized input safe for processing
    """
```

```python
def format_currency(amount: float) -> str:
    """
    Format currency amount for display.
    
    Args:
        amount (float): Currency amount
        
    Returns:
        str: Formatted currency string (e.g., "$12.34")
    """
```

---

## 📊 Data Models

### Core Data Classes

**Module**: `rxflow.workflow.workflow_types`

```python
@dataclass
class ConversationContext:
    """
    Context information for ongoing conversation session.
    
    Attributes:
        session_id (str): Unique session identifier
        patient_id (str): Patient identifier
        current_state (RefillState): Current workflow state
        medication (Optional[str]): Identified medication name
        dosage (Optional[str]): Confirmed medication dosage
        pharmacy (Optional[str]): Selected pharmacy
        order_details (Optional[Dict]): Order information
        created_at (datetime): Session creation timestamp
        last_updated (datetime): Last update timestamp
    """
    session_id: str
    patient_id: str
    current_state: RefillState
    medication: Optional[str] = None
    dosage: Optional[str] = None
    pharmacy: Optional[str] = None
    order_details: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def update(self, **kwargs) -> None:
        """Update context with new values and timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_updated = datetime.utcnow()
```

```python
@dataclass
class ConversationResponse:
    """
    Standardized response from conversation processing.
    
    Attributes:
        message (str): AI-generated response message
        session_id (str): Session identifier
        current_state (RefillState): Current workflow state
        tool_results (List[Dict]): Results from tool executions
        next_steps (Optional[str]): Guidance for user
        error (Optional[str]): Error message if processing failed
        metadata (Dict): Additional response metadata
    """
    message: str
    session_id: str
    current_state: RefillState
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    next_steps: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Mock Data Models

**Module**: `rxflow.services.mock_data`

```python
@dataclass
class PatientRecord:
    """Patient information and medication history."""
    patient_id: str
    name: str
    date_of_birth: str
    phone: str
    email: str
    address: Dict[str, str]
    insurance: Dict[str, Any]
    current_medications: List[Dict[str, Any]]
    medical_history: List[str]
    allergies: List[str]
    emergency_contact: Dict[str, str]
```

```python
@dataclass
class PharmacyRecord:
    """Pharmacy location and service information."""
    pharmacy_id: str
    name: str
    chain: str
    address: Dict[str, str]
    phone: str
    hours: Dict[str, str]
    services: List[str]
    specialties: List[str]
    insurance_accepted: List[str]
    coordinates: Dict[str, float]
```

```python
@dataclass
class MedicationRecord:
    """Medication database information."""
    rxcui: str
    name: str
    generic_name: str
    brand_names: List[str]
    active_ingredients: List[str]
    drug_class: str
    dosage_forms: List[str]
    typical_dosages: List[str]
    contraindications: List[str]
    interactions: List[str]
```

---

## ⚠️ Exception Classes

**Module**: `rxflow.utils.exceptions`

```python
class RxFlowException(Exception):
    """Base exception for RxFlow system."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
```

```python
class ValidationError(RxFlowException):
    """Raised when input validation fails."""
    pass
```

```python
class ProcessingError(RxFlowException):
    """Raised when conversation processing fails."""
    pass
```

```python
class SessionNotFoundError(RxFlowException):
    """Raised when session cannot be found."""
    pass
```

```python
class InvalidTransitionError(RxFlowException):
    """Raised when state transition is not valid."""
    pass
```

```python
class ToolExecutionError(RxFlowException):
    """Raised when tool execution fails."""
    pass
```

```python
class ConfigurationError(RxFlowException):
    """Raised when configuration is invalid."""
    pass
```

---

## 🏷️ Type Definitions

**Module**: `rxflow.workflow.workflow_types`

```python
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from datetime import datetime
from enum import Enum

# Core Types
SessionId = str
PatientId = str  
MedicationName = str
PharmacyName = str

# Tool Response Type
ToolResponse = Dict[str, Any]

# Context Update Type
ContextUpdate = Dict[str, Any]

# State Condition Type
StateCondition = Callable[[ConversationContext], bool]

# LLM Message Types
MessageHistory = List[Dict[str, str]]

# API Response Types
APIResponse = Dict[str, Any]
```

### Tool Interface Types

```python
from langchain.tools import Tool
from typing import Protocol

class ToolFunction(Protocol):
    """Protocol for tool functions."""
    
    def __call__(self, query: str) -> Dict[str, Any]:
        """
        Execute tool function.
        
        Args:
            query: Input query string
            
        Returns:
            Standardized tool response dictionary
        """
        ...

class SafeToolWrapper(Protocol):
    """Protocol for safe tool wrapper functions."""
    
    def __call__(self, query: Union[str, Dict, None]) -> Dict[str, Any]:
        """
        Safe wrapper for tool execution with parameter validation.
        
        Args:
            query: Tool input (string, dict, or None)
            
        Returns:
            Standardized response with error handling
        """
        ...
```

---

## 📈 Usage Examples

### Basic Conversation Flow

```python
from rxflow.workflow.conversation_manager import AdvancedConversationManager
from rxflow.workflow.workflow_types import RefillState

async def example_conversation():
    """Example of basic conversation flow."""
    manager = AdvancedConversationManager()
    session_id = "example_session"
    
    # Start conversation
    response1 = await manager.handle_message(
        "I need to refill my lisinopril",
        session_id
    )
    print(f"State: {response1.current_state}")
    print(f"Response: {response1.message}")
    
    # Confirm dosage
    response2 = await manager.handle_message(
        "Yes, it's 10mg once daily",
        session_id
    )
    print(f"State: {response2.current_state}")
    print(f"Response: {response2.message}")
    
    # Continue conversation...
```

### Direct Tool Usage

```python
from rxflow.tools.patient_history_tool import get_patient_medication_history
from rxflow.tools.rxnorm_tool import lookup_medication_rxnorm

def example_tool_usage():
    """Example of direct tool usage."""
    # Look up patient history
    history_result = get_patient_medication_history("john_doe")
    if history_result["success"]:
        medications = history_result["data"]["current_medications"]
        print(f"Patient has {len(medications)} medications")
    
    # Look up medication in RxNorm
    rxnorm_result = lookup_medication_rxnorm("lisinopril")
    if rxnorm_result["success"]:
        rxcui = rxnorm_result["data"]["rxcui"]
        print(f"RxCUI: {rxcui}")
```

### State Machine Operations

```python
from rxflow.workflow.state_machine import RefillStateMachine
from rxflow.workflow.workflow_types import RefillState

def example_state_machine():
    """Example of state machine operations."""
    state_machine = RefillStateMachine()
    session_id = "test_session"
    
    # Create new session
    context = state_machine.create_session(session_id, "patient_123")
    print(f"Initial state: {context.current_state}")
    
    # Execute transition
    success, updated_context = state_machine.transition(
        session_id,
        "medication_identified",
        medication="lisinopril"
    )
    
    if success:
        print(f"New state: {updated_context.current_state}")
        print(f"Medication: {updated_context.medication}")
```

---

## 🔍 Error Handling Patterns

### Tool Error Handling

```python
from rxflow.tools.rxnorm_tool import lookup_medication_rxnorm
from rxflow.utils.exceptions import ToolExecutionError

def safe_tool_usage():
    """Example of safe tool usage with error handling."""
    try:
        result = lookup_medication_rxnorm("invalid_medication")
        
        if not result["success"]:
            print(f"Tool failed: {result['error']}")
            return None
            
        return result["data"]
        
    except ToolExecutionError as e:
        print(f"Tool execution error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Conversation Error Handling

```python
from rxflow.workflow.conversation_manager import AdvancedConversationManager
from rxflow.utils.exceptions import ProcessingError, ValidationError

async def safe_conversation_handling():
    """Example of safe conversation handling."""
    manager = AdvancedConversationManager()
    
    try:
        response = await manager.handle_message(
            "I need help with my medication",
            "session_123"
        )
        return response
        
    except ValidationError as e:
        print(f"Input validation failed: {e}")
        return create_error_response("Please provide valid input")
        
    except ProcessingError as e:
        print(f"Processing failed: {e}")
        return create_error_response("Unable to process request")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return create_error_response("System error occurred")
```

---

## 📚 Integration Examples

### Streamlit Integration

```python
import streamlit as st
from rxflow.workflow.conversation_manager import AdvancedConversationManager

@st.cache_resource
def get_conversation_manager():
    """Get cached conversation manager instance."""
    return AdvancedConversationManager()

async def streamlit_chat_handler(user_input: str, session_id: str):
    """Handle chat in Streamlit app."""
    manager = get_conversation_manager()
    
    try:
        response = await manager.handle_message(user_input, session_id)
        
        # Display response
        st.write(response.message)
        
        # Display current state
        st.sidebar.write(f"State: {response.current_state.value}")
        
        # Display tool results if any
        if response.tool_results:
            with st.expander("Tool Results"):
                for result in response.tool_results:
                    st.json(result)
                    
        return response
        
    except Exception as e:
        st.error(f"Error: {e}")
        return None
```

### Custom Tool Development

```python
from langchain.tools import Tool
from typing import Dict, Any

class CustomPharmacyTool:
    """Example custom tool implementation."""
    
    def __init__(self):
        self.name = "custom_pharmacy_tool"
        self.description = "Custom pharmacy functionality"
    
    def execute_function(self, query: str) -> Dict[str, Any]:
        """Execute custom tool logic."""
        try:
            # Custom implementation
            result = self._process_custom_query(query)
            
            return {
                "success": True,
                "data": result,
                "source": "custom_pharmacy_tool"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "custom_pharmacy_tool"
            }
    
    def _process_custom_query(self, query: str) -> Dict[str, Any]:
        """Custom processing logic."""
        # Implementation here
        return {"processed": query}

# Create LangChain tool
custom_tool = Tool(
    name="custom_pharmacy_tool",
    description="Custom pharmacy functionality for specialized use cases",
    func=CustomPharmacyTool().execute_function
)
```

---

This API reference provides comprehensive documentation for all public interfaces in the RxFlow Pharmacy Assistant system. For implementation examples and usage patterns, refer to the [Developer Guide](DEVELOPER_GUIDE.md) and [User Guide](USER_GUIDE.md).

**Last Updated:** September 27, 2025 | **Version:** 1.0