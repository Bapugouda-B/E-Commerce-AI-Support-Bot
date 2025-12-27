# E-Commerce AI Support Bot - Complete System Design Documentation

## Table of Contents

1. System Architecture Overview
2. Component Details & Interactions
3. Data Flow Diagrams
4. Technology Stack Analysis
5. Integration Points
6. Deployment Architecture
7. Scalability & Performance Considerations

---

## 🏗️ Section 1: System Architecture Overview

### Three-Layer Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                 FRONTEND LAYER                          │
│              (User Interaction)                         │
│   HTML5 Chat Widget + Real-time JavaScript             │
└─────────────┬───────────────────────────────────────────┘
              │ HTTP/AJAX (JSON)
              ▼
┌─────────────────────────────────────────────────────────┐
│                BACKEND LAYER                            │
│             (Application Logic)                         │
│   Flask REST API + Request Handling                     │
└─────────────┬───────────────────────────────────────────┘
              │ Function Calls + Context
              ▼
┌─────────────────────────────────────────────────────────┐
│              AI & DATA LAYER                            │
│         (Intelligence & Knowledge)                      │
│  LLM + RAG + Agent Router + Mock Tools                 │
└─────────────────────────────────────────────────────────┘
```

### Design Philosophy

- **Separation of Concerns**: Each layer has distinct responsibility
- **Modularity**: Components are independent and replaceable
- **Scalability**: Easy to enhance without architectural changes
- **Maintainability**: Clear code structure, well-documented

---

## 🔧 Section 2: Component Details & Interactions

### 2.1 Frontend Layer (Presentation)

**File:** `templates/index.html`, `static/style.css`, `static/script.js`

**Responsibilities:**

- Display chat interface
- Send user queries via AJAX to backend
- Display bot responses in real-time
- Show quick-action buttons
- Manage conversation history display
- Handle user feedback submission

**Key Components:**

```
Chat Widget
├── Header (Title + Info)
├── Message Area (scrollable conversation)
│   ├── User Message Bubbles
│   └── Bot Message Bubbles
├── Quick Action Buttons
│   ├── "Track Order"
│   ├── "Return Item"
│   ├── "Payment Issue"
│   └── "Help"
├── Input Section
│   ├── Text Input Field
│   └── Send Button
└── Feedback Section (Helpful/Unhelpful)
```

**Technology Details:**

- **HTML5**: Semantic markup, forms, accessibility
- **CSS3**: Flexbox layout, responsive design, animations
- **Vanilla JavaScript (ES6+)**: Fetch API for AJAX, event handling
- **No External Dependencies**: Pure frontend, no jQuery/Bootstrap

**AJAX Flow:**

```javascript
User Types "Track my order"
    ↓
Press Send Button
    ↓
JavaScript captures query
    ↓
fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: userInput })
})
    ↓
Receive JSON response { response: "..." }
    ↓
Append bot message to conversation
    ↓
Display in chat widget with animation
```

---

### 2.2 Backend Layer (Application)

**File:** `backend/app.py`

**Responsibilities:**

- Initialize Flask application with CORS
- Setup LLM, vector store, and agent on startup
- Handle HTTP requests and responses
- Validate user input
- Manage session context
- Return JSON responses

**Key Endpoints:**

#### `/` (GET)

```
Purpose: Serve the chat UI
Response: index.html template
CORS: Enabled
Cache: No (always fresh)
```

#### `/chat` (POST)

```
Purpose: Main chatbot endpoint - process user queries
Request Body: { "query": "Where is my order ORD123?" }
Processing:
  1. Validate JSON and query content
  2. Call agent_router.chat_agent(query)
  3. Capture response from LLM/tools
  4. Clean response (remove artifacts, format)
  5. Log interaction for audit
Response: { "response": "Your order ORD123 is on the way..." }
Status Codes:
  200: Success
  400: Invalid input
  500: Internal error
```

#### `/api/order-status` (GET)

```
Purpose: Direct order lookup API
Query Parameters: ?order_id=ORD123
Processing:
  1. Extract order_id from params
  2. Call mock_tools.get_order_status(order_id)
  3. Return structured JSON
Response:
{
  "order_id": "ORD123",
  "status": "Shipped",
  "ordered_date": "2025-12-20",
  "expected_delivery": "2025-12-27"
}
```

#### `/api/create-return` (POST)

```
Purpose: Create return request
Request Body:
{
  "order_id": "ORD789",
  "reason": "Damaged item",
  "comments": "Item arrived with broken corner"
}
Processing:
  1. Validate order_id exists
  2. Check return eligibility (delivered within N days)
  3. Call mock_tools.create_return_request(...)
  4. Generate return ID
Response:
{
  "success": true,
  "return_id": "RET001234",
  "status": "Created",
  "next_steps": "Print label and ship..."
}
```

**Error Handling:**

```python
try:
    response = agent.chat(query)
except ValueError as e:
    # Validation error
    return {"error": "Invalid input", "details": str(e)}, 400
except Exception as e:
    # Unexpected error
    logging.error(f"Chatbot error: {e}")
    return {"error": "System error, please try again"}, 500
```

---

### 2.3 AI & Data Layer (Intelligence)

#### 2.3.1 Agent Router (`agents/agent_router.py`)

**Responsibilities:**

- Analyze user query intent
- Route to appropriate handler
- Manage conversation context
- Generate final response

**Intent Detection Logic:**

```
User Query: "Where is my order ORD123?"
    ↓
Step 1: Classify Intent
  - Keywords: "where", "order", "track"
  - Pattern Match: order_id_pattern
  - Intent: INTENT_ORDER_TRACKING
    ↓
Step 2: Extract Entities
  - Extract Order ID: "ORD123"
    ↓
Step 3: Select Handler
  if intent == ORDER_TRACKING:
      return get_order_status(order_id)
    ↓
Step 4: Format Response
  Raw tool output: structured dict
  Clean: remove JSON artifacts, personalize
  Add context: "Hi! I found your order..."
    ↓
Return final response to user
```

**Intent Categories:**

| Intent         | Keywords                    | Handler                 | Output                    |
| -------------- | --------------------------- | ----------------------- | ------------------------- |
| GREETING       | hi, hello, hey              | greeting_response()     | "Hello! How can I help?"  |
| ORDER_TRACKING | track, order, where, status | get_order_status()      | Order details + status    |
| RETURN_REQUEST | return, exchange, damaged   | create_return_request() | Return ID + next steps    |
| REFUND_POLICY  | refund, policy, timeline    | get_refund_policy()     | Policy details from RAG   |
| PAYMENT_ISSUE  | payment, failed, charged    | payment_help()          | Guidance + escalation     |
| FAQ/KNOWLEDGE  | other queries               | RAG QA Chain            | Knowledge-grounded answer |
| OUT_OF_SCOPE   | non e-commerce              | escalation()            | "I can only help with..." |

**Conversation Memory:**

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    max_token_limit=2000  # Prevent unbounded growth
)

# On each turn:
memory.save_context(
    {"input": user_query},
    {"output": bot_response}
)

# When calling LLM, include:
chat_history = memory.load_memory_variables({})["chat_history"]
# This allows LLM to understand context
```

---

#### 2.3.2 LLM Module (`llm/llm_loader.py`)

**Model:** FLAN-T5-Base (Google HuggingFace)

**Why FLAN-T5?**

- ✅ Free (open-source)
- ✅ Instruction-tuned for diverse tasks
- ✅ Fast inference on CPU
- ✅ Good quality (13B parameter base)
- ✅ No API keys required

**Loading Process:**

```python
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

def load_llm():
    model_name = "google/flan-t5-base"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        device_map="cpu"  # or "cuda" if GPU available
    )

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=512,
        temperature=0.7  # Balanced: creative but stable
    )

    return HuggingFacePipeline(model_kwargs={"temperature": 0.7}, pipeline=pipe)
```

**Response Generation:**

```
System Prompt + Context + Query
    ↓
FLAN-T5 Tokenizer (text → token IDs)
    ↓
Model Inference (forward pass)
    ↓
Generate token sequence
    ↓
Decode tokens → text
    ↓
Post-process (clean, format)
    ↓
Return response
```

---

#### 2.3.3 RAG Pipeline (`rag/` directory)

##### Embeddings (`rag/embeddings.py`)

**Model:** all-MiniLM-L6-v2 (Sentence-Transformers)

**Purpose:** Convert text to fixed-size vectors (384-dim) for semantic search

**Process:**

```
Input Text: "What is your return policy?"
    ↓
Tokenize: [101, 2054, 2003, ...]
    ↓
Sentence-BERT Encoder (6 layers)
    ↓
Output Vector: [0.15, -0.23, 0.88, ..., -0.12] (384 dimensions)
    ↓
Store in FAISS vector database
```

**Why MiniLM?**

- Small (33M parameters, 22MB)
- Fast inference (milliseconds)
- Good quality for semantic similarity
- Proven on STS benchmark

##### Vector Store (`rag/vectorstore.py`)

**Technology:** FAISS (Facebook AI Similarity Search)

**Architecture:**

```
Knowledge Base Documents (50+ documents)
    ↓
Split into chunks (max 512 tokens)
    ↓
Generate embeddings for each chunk
    ↓
Build FAISS index (in-memory)
    ↓
Store mapping: chunk_id → original document
    ↓
Query-time: Fast similarity search in milliseconds
```

**Search Process:**

```
User Query: "How long does shipping take?"
    ↓
Embed query: embed("How long...") → [0.12, -0.34, ...]
    ↓
FAISS search: Find k=5 nearest neighbors
    ↓
Retrieved documents:
  1. "Standard shipping: 5-7 business days"
  2. "Express shipping: 2-3 days"
  3. "Free shipping on orders over $50"
  4. "Shipping policy document"
  5. "FAQ about delivery"
    ↓
Pass to LLM with system prompt
    ↓
LLM generates: "Standard shipping takes 5-7..."
```

**FAISS Index Details:**

```python
from faiss import IndexFlatL2

# Create L2 distance index (Euclidean distance)
index = faiss.IndexFlatL2(embedding_dim=384)

# Add all embedded documents
index.add(np.array(document_embeddings))

# Search (returns distances and indices)
distances, indices = index.search(query_embedding, k=5)

# Retrieve actual documents
results = [documents[idx] for idx in indices]
```

---

##### Knowledge Base (`data/knowledge_base.py`)

**Structure:**

```python
KNOWLEDGE_BASE_DOCS = [
    {
        "id": "doc_001",
        "category": "shipping",
        "content": "Standard shipping takes 5-7 business days..."
    },
    {
        "id": "doc_002",
        "category": "returns",
        "content": "Items can be returned within 30 days..."
    },
    # ... 50+ more documents
]
```

**Categories Covered:**

- 📦 Order & Delivery (tracking, shipping methods, timelines)
- Returns & Exchanges (eligibility, process, timelines)
- Refunds (policy, timelines, status)
- 💳 Payments (methods, issues, security)
- Discounts & Coupons (how to use, restrictions)
- 📱 Products (categories, search, availability)
- 👤 Account (management, security, password reset)
- 🆘 Support & Escalation (contact info, priority issues)

---

#### 2.3.4 Mock Tools (`backend/mock_tools.py`)

**Purpose:** Simulate backend operations without real databases

**Mock Data Structure:**

```python
MOCK_ORDERS = {
    "ORD123": {
        "order_id": "ORD123",
        "customer_name": "John Doe",
        "order_date": "2025-12-15",
        "status": "Shipped",
        "expected_delivery": "2025-12-27",
        "items": ["Laptop", "Mouse"],
        "total": 45000
    },
    "ORD456": { ... },
    "ORD789": { ... }
}

MOCK_PRODUCTS = {
    "PROD001": {
        "name": "Wireless Headphones",
        "price": 2999,
        "in_stock": True,
        "rating": 4.5
    },
    # ... more products
}
```

**Tool Functions:**

```python
def get_order_status(order_id: str) -> dict:
    """Lookup order status"""
    if order_id in MOCK_ORDERS:
        order = MOCK_ORDERS[order_id]
        return {
            "order_id": order_id,
            "status": order["status"],
            "expected_delivery": order["expected_delivery"],
            "message": f"Your order is {order['status'].lower()}"
        }
    else:
        return {"error": f"Order {order_id} not found"}

def create_return_request(order_id: str, reason: str) -> dict:
    """Create a return request"""
    if order_id not in MOCK_ORDERS:
        return {"error": "Order not found"}

    order = MOCK_ORDERS[order_id]
    # Check eligibility (delivered within 30 days)
    from datetime import datetime, timedelta
    order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
    if (datetime.now() - order_date) > timedelta(days=30):
        return {"error": "Return window expired"}

    # Create return ID
    return_id = f"RET{random.randint(100000, 999999)}"

    return {
        "success": True,
        "return_id": return_id,
        "order_id": order_id,
        "message": f"Return request {return_id} created successfully"
    }

def payment_failed_help() -> str:
    """Provide guidance for payment failures"""
    return """
    Payment Failed - Don't Worry! Here's what typically happens:

    ✓ If amount was deducted, it will be refunded within 3-5 business days
    ✓ Check your bank account - sometimes it takes a while to process
    ✓ Try again with a different payment method

    If issue persists, contact us at support@ecommerce.com
    """

def get_refund_policy() -> str:
    """Return refund policy document"""
    return """
    REFUND POLICY

    Refund Timeline:
    - Initiated: 5 business days
    - Processed: 7-10 business days
    - Bank posting: 3-5 additional days

    Conditions:
    - Return must be within 30 days of delivery
    - Item must be in original condition
    - Original receipt/proof required
    """
```

---

### 2.4 Complete Request-Response Flow

```
1. USER INTERACTION
   ├─ User types: "Where is order ORD123?"
   └─ Clicks Send Button

2. FRONTEND PROCESSING
   ├─ JavaScript captures input
   ├─ Validates (not empty, length check)
   ├─ Creates AJAX request
   └─ Sends to /chat endpoint

3. BACKEND (Flask)
   ├─ Receives JSON: {"query": "Where is order ORD123?"}
   ├─ Validates input (length, format)
   ├─ Calls agent_router.chat_agent(query)
   └─ Waits for response

4. AI LAYER (Agent Router)
   ├─ Analyze intent → ORDER_TRACKING
   ├─ Extract entity → order_id = "ORD123"
   ├─ Select handler → get_order_status()
   ├─ Call mock_tools.get_order_status("ORD123")
   │  └─ Returns: {"status": "Shipped", "expected_delivery": "2025-12-27"}
   ├─ Build prompt: "User asked about order status. Tool returned: {...}"
   ├─ Call FLAN-T5 with system prompt + context
   │  └─ Generates: "Your order ORD123 is currently shipped..."
   ├─ Clean response (remove tokens, format)
   ├─ Store in memory: {"input": "...", "output": "..."}
   └─ Return response to Flask

5. BACKEND RESPONSE
   ├─ Receive response from agent
   ├─ Format as JSON: {"response": "Your order ORD123 is..."}
   ├─ Log interaction (optional)
   └─ Return to frontend

6. FRONTEND DISPLAY
   ├─ Receive JSON response
   ├─ Create message bubble (bot)
   ├─ Append to conversation
   ├─ Scroll to bottom
   └─ Animate in with fade-in

7. USER SEES
   └─ "Your order ORD123 is currently shipped and expected on 2025-12-27"
```

---

## 📊 Section 3: Data Flow Diagrams

### 3.1 Query Processing Flow

```
┌─────────────────────────────────────────────────────────┐
│  USER INPUT: "I want to return my order ORD789"        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────┐
        │  INTENT DETECTION       │
        │  Keywords: return, item │
        │  → INTENT_RETURN        │
        └──────────┬──────────────┘
                   │
                   ▼
        ┌─────────────────────────┐
        │  ENTITY EXTRACTION      │
        │  Order ID: "ORD789"     │
        │  Reason: damaged?       │
        └──────────┬──────────────┘
                   │
                   ▼
        ┌─────────────────────────┐
        │  HANDLER SELECTION      │
        │  Route to tool:         │
        │  create_return_request()│
        └──────────┬──────────────┘
                   │
                   ▼
        ┌─────────────────────────┐
        │  TOOL EXECUTION         │
        │  - Lookup order ORD789  │
        │  - Check eligibility    │
        │  - Create return ID     │
        └──────────┬──────────────┘
                   │
                   ▼
        ┌─────────────────────────┐
        │  TOOL OUTPUT            │
        │  {                      │
        │    return_id: RET00123, │
        │    status: Created      │
        │  }                      │
        └──────────┬──────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  RESPONSE GENERATION (FLAN-T5)      │
        │  System Prompt: You're helpful...   │
        │  Context: Tool returned...          │
        │  Conversation History: [...]        │
        │  User Query: Return order ORD789    │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │  LLM OUTPUT                  │
        │  "Great! I've created a...   │
        │   return request RET00123... │
        │   Please print the label..." │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │  POST-PROCESSING             │
        │  - Clean artifacts           │
        │  - Format text               │
        │  - Add personality           │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │  FINAL RESPONSE              │
        │  "Great! I've created return │
        │   request RET00123 for your  │
        │   order ORD789. Print label  │
        │   and ship to our warehouse" │
        └──────────┬───────────────────┘
                   │
                   ▼
      ┌───────────────────────────────────────┐
      │ DISPLAY TO USER                       │
      │ ────────────────────────────────────  │
      │ Bot: Great! I've created return       │
      │      request RET00123 for your order  │
      │      ORD789...                        │
      └───────────────────────────────────────┘
```

### 3.2 RAG Query Flow

```
┌──────────────────────────────────────────────┐
│  USER INPUT: "How long does shipping take?" │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────────┐
        │  INTENT DETECTION               │
        │  Keywords: how, long, shipping  │
        │  → Not matching tool intent     │
        │  → RAG_QA (knowledge-based)     │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │  EMBEDDING GENERATION           │
        │  Query: "How long does..."      │
        │  Model: Sentence-Transformers   │
        │  Output: [0.12, -0.34, ...]    │
        │  Dimension: 384                 │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │  FAISS SIMILARITY SEARCH        │
        │  Index: 50+ documents embedded  │
        │  Search: Find k=5 nearest       │
        │  Distance metric: L2            │
        │  Time: ~5-10ms                  │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────────┐
        │  RETRIEVED DOCUMENTS                    │
        │  1. "Standard shipping 5-7 days"        │
        │  2. "Express shipping 2-3 days"         │
        │  3. "Free shipping on orders >50"       │
        │  4. "Shipping methods comparison"       │
        │  5. "Delivery tracking FAQ"             │
        └────────────┬────────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────────────────┐
        │  CONTEXT BUILDING                            │
        │  System Prompt: "You're helpful e-commerce"  │
        │  Retrieved Context: [doc1, doc2, ...]        │
        │  Chat History: [previous messages]           │
        │  User Query: "How long does shipping take?"  │
        └────────────┬─────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │  FLAN-T5 GENERATION                │
        │  Input tokens: ~200                │
        │  Decoding: Beam search (temp=0.7)  │
        │  Output tokens: ~50                │
        │  Time: ~1-2 seconds (CPU)          │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │  LLM OUTPUT                        │
        │  "Shipping timelines: Standard     │
        │   shipping takes 5-7 business days │
        │   Express takes 2-3 days..."       │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  POST-PROCESSING                 │
        │  - Extract useful parts          │
        │  - Format for display            │
        │  - Validate against original doc │
        │  - Add source attribution        │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────────┐
        │  FINAL RESPONSE                      │
        │  "Shipping timelines are:            │
        │   • Standard: 5-7 business days      │
        │   • Express: 2-3 business days       │
        │   Free shipping on orders over $50"  │
        └────────────┬─────────────────────────┘
                     │
                     ▼
      ┌────────────────────────────────────────┐
      │ DISPLAY TO USER                        │
      │ ────────────────────────────────────   │
      │ Bot: Shipping timelines are:...        │
      └────────────────────────────────────────┘
```

---

## 💻 Section 4: Technology Stack Analysis

### 4.1 Why Each Technology Was Chosen

#### **Python 3.9+**

- Industry standard for NLP/ML
- Rich ecosystem (transformers, langchain, faiss)
- Cross-platform deployment
- Good performance for CPU-bound tasks

#### **Flask 3.1.2**

- Lightweight and simple (not overkill like Django)
- Perfect for API-first architecture
- Excellent ecosystem (Flask-CORS, extensions)
- Easy to understand and maintain

#### **FLAN-T5-Base**

- Free and open-source
- Instruction-tuned (good at following prompts)
- Fast inference on CPU
- Good quality (13B parameter model)
- Perfect for chat applications

#### **LangChain 1.2.0**

- Abstracts LLM complexities
- Provides Memory, Chain, Agent abstractions
- Easy prompt management
- Large community and documentation

#### **Sentence-Transformers 2.5.1**

- Best-in-class semantic embeddings
- Small model size (MiniLM-L6)
- Fast inference
- Pre-trained on diverse data

#### **FAISS 1.7.4**

- Optimized vector similarity search
- In-memory (fast)
- Scales to millions of vectors
- Industry standard (used by Meta, Google)

#### **HTML5 / CSS3 / Vanilla JS**

- No build tools needed
- Single file deployment
- Fast and responsive
- Works everywhere (browsers)

---

### 4.2 Performance Characteristics

| Component     | Metric         | Value       | Note                        |
| ------------- | -------------- | ----------- | --------------------------- |
| FLAN-T5       | Model Size     | 248 MB      | Loaded into RAM once        |
| FLAN-T5       | Inference Time | 1-2 sec     | Per query on CPU            |
| Sentence-BERT | Model Size     | 22 MB       | Very compact                |
| Sentence-BERT | Embedding Time | <5ms        | Per query                   |
| FAISS         | Search Time    | 5-10ms      | k=5 nearest neighbors       |
| Flask         | API Latency    | 50-100ms    | Network + processing        |
| **Total**     | **End-to-End** | **2-3 sec** | From user input to response |

---

## 🔗 Section 5: Integration Points

### 5.1 External Integrations (Future)

```
Current (Mock):
┌──────────────────────────────────────┐
│  E-Commerce AI Chatbot               │
│  ├─ Mock Orders (hardcoded)          │
│  ├─ Mock Tools (simulated)           │
│  └─ Local Knowledge Base (embedded)  │
└──────────────────────────────────────┘

Future (Real Integration):
┌──────────────────────────────────────────────────────┐
│  E-Commerce AI Chatbot                               │
├─ Order Management System (OMS) API                   │
│  ├─ Get order status, history, details              │
│  ├─ Create/modify orders                            │
│  └─ Real-time tracking data                         │
├─ Payment Gateway API (Stripe/Razorpay)              │
│  ├─ Check payment status                            │
│  ├─ Refund processing                               │
│  └─ Double-charge verification                      │
├─ Logistics API (Shiprocket/Delhivery)               │
│  ├─ Track shipments                                 │
│  ├─ Get tracking updates                            │
│  └─ Address validation                              │
├─ CRM System (HubSpot/Salesforce)                    │
│  ├─ Customer history                                │
│  ├─ Support ticket creation                         │
│  └─ Escalation routing                              │
├─ Vector DB (Pinecone/Weaviate)                      │
│  ├─ Persistent document storage                     │
│  ├─ Advanced retrieval                              │
│  └─ Dynamic knowledge updates                       │
└─ LLM API (OpenAI GPT-4 / Claude 3)                  │
   ├─ Better reasoning capability                     │
   ├─ Lower latency (API-based)                       │
   └─ Multi-modal support                             │
```

---

### 5.2 Database Schema (Future)

```sql
-- Users Table
CREATE TABLE users (
  id INT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(20),
  created_at TIMESTAMP
);

-- Orders Table
CREATE TABLE orders (
  order_id VARCHAR(20) PRIMARY KEY,
  user_id INT,
  order_date TIMESTAMP,
  status VARCHAR(50),
  total DECIMAL(10, 2),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Conversations Table (for logging)
CREATE TABLE conversations (
  id INT PRIMARY KEY,
  user_id INT,
  query TEXT,
  response TEXT,
  intent VARCHAR(50),
  tool_used VARCHAR(50),
  timestamp TIMESTAMP,
  helpful BOOLEAN,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Returns Table
CREATE TABLE returns (
  return_id VARCHAR(20) PRIMARY KEY,
  order_id VARCHAR(20),
  reason TEXT,
  status VARCHAR(50),
  created_at TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

---

## 🚀 Section 6: Deployment Architecture

### 6.1 Local Development

```
Developer Machine
├─ Conda environment
├─ Python 3.9
├─ requirements.txt (all dependencies)
├─ Flask development server (http://127.0.0.1:5000)
└─ Browser (chat UI)
```

### 6.2 Production Deployment (Future)

```
┌─────────────────────────────────────────────────────────┐
│                    INTERNET / DNS                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │  CDN (Akamai) │ ← Serve static files (CSS, JS)
         └───────────────┘
                 │
                 ▼
         ┌──────────────────────┐
         │  Load Balancer (AWS) │ ← Distribute traffic
         └──────┬───────────────┘
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
    ┌────────┬────────┬────────┐
    │ Pod 1  │ Pod 2  │ Pod 3  │ ← Kubernetes Pods
    │ Flask  │ Flask  │ Flask  │
    │ + LLM  │ + LLM  │ + LLM  │
    └────────┴────────┴────────┘
        │       │        │
        └───────┼────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │  Redis Cache                │ ← Session + responses
    │  (conversation memory)      │
    └─────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │  Vector DB (Pinecone)       │ ← Persistent embeddings
    │  (knowledge base)           │
    └─────────────────────────────┘
                │
                ▼
    ┌──────────────────────────────────┐
    │  External APIs                   │
    │  ├─ OMS, Payment, Logistics      │
    │  ├─ CRM, Email Service           │
    │  └─ LLM API (OpenAI / Anthropic) │
    └──────────────────────────────────┘
```

### 6.3 Containerization (Docker)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY . .

# Expose port
EXPOSE 5000

# Run Flask
CMD ["python", "-m", "backend.app"]
```

**Docker Compose (Local + Services):**

```yaml
version: "3.8"
services:
  chatbot:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=secret
```

---

## 📈 Section 7: Scalability & Performance

### 7.1 Bottlenecks & Solutions

| Bottleneck                  | Current         | Solution                        |
| --------------------------- | --------------- | ------------------------------- |
| **LLM Inference (1-2 sec)** | FLAN-T5 on CPU  | Use faster LLM API or GPU       |
| **Model Loading**           | 248 MB VRAM     | Load once, reuse (already done) |
| **Vector Search**           | FAISS in-memory | Use Pinecone for scale          |
| **Session Memory**          | In-process      | Use Redis for distributed       |
| **Database Queries**        | Mock (instant)  | Add connection pooling          |

### 7.2 Optimization Strategies

#### **LLM Inference**

```python
# Caching responses for common queries
response_cache = {}

def chat_agent(query: str):
    if query in response_cache:
        return response_cache[query]  # 0ms

    # Otherwise, process normally
    response = llm.generate(prompt)
    response_cache[query] = response
    return response
```

#### **Embedding Caching**

```python
# Cache document embeddings (done at startup)
embedding_cache = {}

for doc in knowledge_base:
    embedding_cache[doc.id] = embed(doc.content)  # Compute once

# Query-time lookup is instant
```

#### **Batch Processing**

```python
# Process multiple queries in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(agent.chat, query)
        for query in queries
    ]
    responses = [f.result() for f in futures]
```

### 7.3 Metrics & Monitoring

```python
import time
from functools import wraps

def track_performance(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@track_performance
def chat_agent(query):
    # ... implementation
    pass
```

**Key Metrics to Track:**

- Query latency (p50, p95, p99)
- Error rate
- Intent classification accuracy
- Tool execution time
- LLM token usage
- API response time
- User satisfaction (helpful/unhelpful)

---

## 🎯 Conclusion

This system design demonstrates:

1. **Modularity**: Each component has single responsibility
2. **Scalability**: Can easily upgrade to production components
3. **Maintainability**: Clear code structure and separation
4. **Extensibility**: New features/APIs without architectural changes
5. **Performance**: 2-3 second end-to-end latency on CPU

The chatbot is **production-ready in structure** and **demo-ready in implementation**, with clear upgrade paths to handle 1000+ concurrent users and millions of queries.

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Status:** Complete
