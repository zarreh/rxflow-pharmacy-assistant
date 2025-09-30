# 🔄 Comprehensive Workflow Diagrams

This page contains detailed workflow diagrams that illustrate how RxFlow processes prescription refill requests through various scenarios.

## 🌳 Interactive Decision Tree

The system uses an intelligent decision tree to route requests through the optimal workflow path:

```mermaid
graph TD
    Start([👤 User Input<br/>Medication Request]) --> Parse{🔍 Parse Request}
    
    Parse -->|Clear medication name| GetHistory[📋 Get Patient History]
    Parse -->|Unclear request| Clarify[❓ Ask for Clarification]
    
    GetHistory --> CheckMed{💊 Medication Found?}
    CheckMed -->|✅ Found| SafetyCheck{🛡️ Safety Analysis}
    CheckMed -->|❌ Not Found| UnknownMed[🔍 Unknown Medication]
    
    SafetyCheck -->|🟢 Safe| CheckRefills{💊 Refills Available?}
    SafetyCheck -->|🔴 Controlled Substance| DoctorEsc[👨‍⚕️ Doctor Escalation]
    SafetyCheck -->|⚠️ Safety Concerns| DoctorEsc
    
    CheckRefills -->|✅ Has Refills| Insurance{💳 Insurance Check}
    CheckRefills -->|❌ No Refills| ExpiredRx[📅 Expired Prescription]
    
    Insurance -->|✅ Covered| FindPharmacy[🏥 Find Pharmacy]
    Insurance -->|❌ Not Covered| PriorAuth[📋 Prior Authorization]
    Insurance -->|💰 High Cost| GenericOpt[💊 Generic Option]
    
    FindPharmacy --> CheckStock{📦 In Stock?}
    CheckStock -->|✅ Available| PriceComp[💰 Price Comparison]
    CheckStock -->|❌ Out of Stock| Fallback[🔄 Pharmacy Fallback]
    
    Fallback --> TryNext[🏪 Try Next Pharmacy]
    TryNext --> CheckStock2{📦 Alternative Stock?}
    CheckStock2 -->|✅ Found| PriceComp
    CheckStock2 -->|❌ All Out| PharmacistEsc[👩‍⚕️ Pharmacist Consult]
    
    PriceComp --> OrderReady[✅ Order Ready]
    OrderReady --> Confirm{✋ User Confirmation}
    Confirm -->|✅ Approved| SubmitOrder[📝 Submit Order]
    Confirm -->|❌ Declined| ModifyOrder[🔄 Modify Selection]
    
    SubmitOrder --> Success[🎉 Order Completed]
    
    %% Escalation Endpoints
    DoctorEsc --> ContactDoctor[📞 Contact Doctor]
    ExpiredRx --> ContactDoctor
    PriorAuth --> ContactInsurance[📞 Contact Insurance]
    UnknownMed --> PharmacistEsc
    PharmacistEsc --> ContactPharmacist[📞 Contact Pharmacist]
    
    %% Modification Loops
    ModifyOrder --> FindPharmacy
    Clarify --> Parse
    GenericOpt --> FindPharmacy
    
    %% Final States
    ContactDoctor --> EndEscalation[🏁 Escalation Complete]
    ContactInsurance --> EndEscalation
    ContactPharmacist --> EndEscalation
    Success --> EndSuccess[🎉 Refill Complete]
```

## 🔧 State Machine Transitions

The RxFlow state machine manages complex workflow transitions with intelligent decision-making:

```mermaid
stateDiagram-v2
    [*] --> START
    START --> IDENTIFY_MEDICATION : medication_request
    START --> ERROR : invalid_input
    
    IDENTIFY_MEDICATION --> CLARIFY_MEDICATION : ambiguous_medication
    IDENTIFY_MEDICATION --> CONFIRM_DOSAGE : medication_identified
    IDENTIFY_MEDICATION --> ESCALATE_UNKNOWN : unknown_medication
    
    CLARIFY_MEDICATION --> CONFIRM_DOSAGE : medication_clarified
    CLARIFY_MEDICATION --> ERROR : clarification_failed
    
    CONFIRM_DOSAGE --> CHECK_AUTHORIZATION : dosage_confirmed
    CONFIRM_DOSAGE --> ESCALATE_SAFETY : safety_concern
    
    CHECK_AUTHORIZATION --> SELECT_PHARMACY : authorized
    CHECK_AUTHORIZATION --> ESCALATE_PA : prior_auth_required
    CHECK_AUTHORIZATION --> ESCALATE_REFILLS : no_refills
    
    SELECT_PHARMACY --> CONFIRM_ORDER : pharmacy_selected
    SELECT_PHARMACY --> ESCALATE_INVENTORY : no_pharmacy_available
    
    CONFIRM_ORDER --> COMPLETE : order_confirmed
    CONFIRM_ORDER --> SELECT_PHARMACY : change_pharmacy
    CONFIRM_ORDER --> ERROR : order_failed
    
    ESCALATE_PA --> SELECT_PHARMACY : pa_approved
    ESCALATE_PA --> ERROR : pa_denied
    
    ESCALATE_UNKNOWN --> [*] : pharmacist_contacted
    ESCALATE_SAFETY --> [*] : doctor_contacted
    ESCALATE_REFILLS --> [*] : doctor_contacted
    ESCALATE_INVENTORY --> SELECT_PHARMACY : fallback_found
    
    ERROR --> START : restart_conversation
    ERROR --> IDENTIFY_MEDICATION : retry_medication
    
    COMPLETE --> [*] : workflow_complete
```

## 🚀 Advanced Workflow Patterns

### 1. **Happy Path Workflow Sequence**

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant CM as Conversation Manager
    participant SM as State Machine
    participant Tools as Healthcare Tools
    participant API as Mock APIs
    
    User->>UI: "I need to refill my omeprazole"
    UI->>CM: Process message with session context
    CM->>SM: Check current state (START)
    SM->>Tools: Execute Patient History Tool
    Tools->>API: Lookup patient medication history
    API-->>Tools: Return patient data + medications
    Tools-->>SM: Medication found (omeprazole 20mg)
    SM->>SM: Transition to CONFIRM_DOSAGE
    SM->>Tools: Execute Safety Verification
    Tools->>Tools: Check dosage, interactions, allergies
    Tools-->>SM: Safety checks passed
    SM->>SM: Transition to SELECT_PHARMACY
    SM->>Tools: Execute Pharmacy Location Tool
    Tools->>API: Find nearby pharmacies with inventory
    API-->>Tools: Return pharmacy options
    Tools-->>SM: Pharmacy selection ready
    SM-->>CM: Workflow state updated
    CM-->>UI: "Found your omeprazole 20mg. CVS Main St has it for $12.99, ready in 15 minutes."
    UI-->>User: Display response with pharmacy options
```

### 2. **Escalation Workflow Sequence**

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant CM as Conversation Manager
    participant SM as State Machine
    participant ET as Escalation Tools
    participant ES as Escalation System
    
    User->>UI: "I need to refill my lorazepam"
    UI->>CM: Process message with session context
    CM->>SM: Check current state (START)
    SM->>Tools: Execute Patient History Tool
    Tools->>API: Lookup patient medication history
    API-->>Tools: Return lorazepam (controlled substance)
    Tools-->>SM: Controlled substance detected
    SM->>ET: Execute Escalation Check Tool
    ET->>ET: Analyze medication requirements
    Note over ET: Lorazepam = Schedule IV<br/>Requires doctor consultation
    ET-->>SM: ESCALATION REQUIRED (Doctor)
    SM->>SM: Transition to ESCALATE_SAFETY
    SM->>ES: Route to Doctor Escalation
    ES-->>CM: Generate escalation response
    CM-->>UI: "Lorazepam requires doctor consultation. Please contact your physician for refill authorization."
    UI-->>User: Display escalation message with next steps
```

### 3. **Pharmacy Fallback Sequence**

```mermaid
sequenceDiagram
    participant User
    participant System as RxFlow System
    participant CVS as CVS Pharmacy
    participant Walmart as Walmart Pharmacy
    participant Walgreens as Walgreens Pharmacy
    participant Costco as Costco Pharmacy
    
    User->>System: Request omeprazole refill
    System->>CVS: Check inventory for omeprazole 20mg
    CVS-->>System: ❌ Out of stock
    
    Note over System: Intelligent Fallback Activated
    System->>Walmart: Check inventory for omeprazole 20mg
    Walmart-->>System: ❌ Out of stock
    
    System->>Walgreens: Check inventory for omeprazole 20mg
    Walgreens-->>System: ✅ In stock - $15.99
    
    System-->>User: "CVS is out of stock. Found omeprazole at Walgreens (1.2 miles) for $15.99, ready in 20 minutes."
    
    alt User Accepts Alternative
        User->>System: Accept Walgreens option
        System->>Walgreens: Submit refill order
        Walgreens-->>System: Order confirmed
        System-->>User: "Order submitted to Walgreens. Pickup ready at 3:20 PM."
    else User Requests Different Option
        User->>System: "Try other pharmacies"
        System->>Costco: Check inventory
        Costco-->>System: ✅ In stock - $12.99
        System-->>User: "Also available at Costco (2.1 miles) for $12.99, ready in 30 minutes."
    end
```

## 📊 Tool Integration Flow

```mermaid
graph LR
    subgraph "Patient Tools"
        PH[Patient History]
        MA[Medication Adherence]
        AL[Allergy Check]
    end
    
    subgraph "Medication Tools"
        RX[RxNorm Lookup]
        DV[Dosage Validation]
        DI[Drug Interactions]
    end
    
    subgraph "Pharmacy Tools"
        PS[Pharmacy Search]
        IS[Inventory Status]
        PC[Price Comparison]
    end
    
    subgraph "Safety Tools"
        SC[Safety Check]
        ES[Escalation System]
        CS[Controlled Substance]
    end
    
    subgraph "Order Tools"
        OS[Order Submission]
        OT[Order Tracking]
        OC[Order Cancellation]
    end
    
    CM[Conversation Manager] --> PH
    CM --> RX
    CM --> PS
    CM --> SC
    CM --> OS
    
    PH --> MA
    PH --> AL
    RX --> DV
    RX --> DI
    PS --> IS
    PS --> PC
    SC --> ES
    SC --> CS
    
    ES --> Doctor[👨‍⚕️ Doctor Escalation]
    ES --> Pharmacist[👩‍⚕️ Pharmacist Escalation]
```

## 🎯 Error Handling & Recovery

```mermaid
graph TD
    Error[❌ Error Detected] --> Type{Error Type?}
    
    Type -->|Validation Error| Retry[🔄 Retry with Correction]
    Type -->|API Timeout| Fallback[🔄 Try Alternative API]
    Type -->|Unknown Medication| Clarify[❓ Request Clarification]
    Type -->|System Error| Escalate[🚨 System Escalation]
    
    Retry --> Success{✅ Success?}
    Fallback --> Success
    Clarify --> Success
    
    Success -->|Yes| Continue[➡️ Continue Workflow]
    Success -->|No| MaxRetries{Max Retries?}
    
    MaxRetries -->|No| Retry
    MaxRetries -->|Yes| Escalate
    
    Escalate --> Admin[👨‍💻 Admin Notification]
    Admin --> Manual[🤲 Manual Intervention]
    
    Continue --> Complete[✅ Workflow Complete]
```