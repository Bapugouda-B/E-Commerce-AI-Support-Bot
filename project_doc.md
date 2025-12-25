# E‑Commerce AI Support Bot – Project Documentation

## 1. Introduction

### 1.1 Problem Statement

Modern e‑commerce platforms receive a large volume of repetitive customer queries related to orders, payments, refunds, returns, and product information. Human agents handling all of these requests leads to:

- High operational cost.
- Longer response times during peak hours.
- Inconsistent quality of responses.
- Limited availability outside business hours.

There is a need for an automated, intelligent customer support assistant that can answer most routine queries instantly and accurately, and only escalate complex or critical issues to human support.

### 1.2 Project Objective

The objective of this project is to design and implement an **AI‑powered E‑Commerce Customer Support Bot** that:

- Understands customer queries in natural language.
- Handles common e‑commerce tasks such as:
  - Order status lookup.
  - Returns and exchanges.
  - Refund policy clarification.
  - Payment failure and double‑charge issues.
  - Discount / coupon questions.
  - Product and account information.
- Uses a **Retrieval‑Augmented Generation (RAG)** approach to answer policy/FAQ questions based on a curated knowledge base.
- Uses **mock backend tools** to simulate real order and payment operations.
- Provides a clean, user‑friendly web chat interface.
- Demonstrates good software engineering practices: modular structure, clear routing logic, and documentation.

### 1.3 Scope

The bot is designed for an e‑commerce environment, with the following scope:

- Web‑based chat UI (single page served by Flask).
- English language support.
- Stateless HTTP API with in‑memory conversation context per session.
- Mock backend data for orders and returns (no real database).
- Local LLM and embedding models (no external paid APIs required).

Out of scope:

- Real payment gateway or logistics integration.
- User authentication / login.
- Multi‑language support (can be extended as future work).

---

## 2. System Overview

### 2.1 High‑Level Architecture

The system uses three main layers:

1. **Frontend (UI Layer)**

   - Implemented as an HTML/CSS/JavaScript chat widget (`templates/index.html`, `static/style.css`).
   - Sends user queries to the backend via AJAX (`/chat` endpoint).
   - Displays bot responses, quick‑action buttons, and typing indicators.

2. **Backend (Application Layer)**

   - Implemented using Flask (`backend/app.py`).
   - Exposes REST endpoints:
     - `/` – Serve the chat UI.
     - `/chat` – Main chatbot endpoint.
     - `/api/order-status` – Direct order status API.
     - `/api/create-return` – Direct return creation API.
     - `/api/refund-policy` – Refund policy API.
   - Delegates all conversational logic to the **Agent Router**.

3. **AI & Data Layer**
   - **Agent Router** (`agents/agent_router.py`):
     - Performs intent classification using keyword patterns.
     - Routes to mock tools or RAG QA chain.
     - Manages conversation memory.
   - **LLM Loader** (`llm/llm_loader.py`):
     - Loads the text generation model (e.g., FLAN‑T5).
   - **RAG Components**:
     - `data/knowledge_base.py` – Knowledge base documents.
     - `rag/embeddings.py` – Embedding model (sentence transformer).
     - `rag/vectorstore.py` – FAISS vector store for similarity search.
     - `prompts/system_prompt.py` – QA system prompt template.
   - **Mock Backend Tools** (`backend/mock_tools.py`):
     - Simulate order, return, refund, payment, and product behavior.

### 2.2 Technology Stack

- **Programming Language**: Python 3.9+
- **Web Framework**: Flask
- **AI / NLP Libraries**:
  - Transformers (HuggingFace)
  - Sentence‑Transformers
  - LangChain / langchain‑community
- **Vector Store**: FAISS (in‑memory)
- **Frontend**:
  - HTML5, CSS3, Vanilla JavaScript

---

## 3. Functional Requirements

1. **Order Tracking**

   - User can ask: “Where is my order ORD123?”
   - System extracts `ORD123`, checks mock orders, and returns:
     - Order status (Pending, Processing, Shipped, Delivered).
     - Order date and expected delivery date.
     - Simple explanation of the status.

2. **Returns & Exchanges**

   - User can request a return or exchange.
   - System:
     - Validates order eligibility (e.g., delivered within last N days).
     - Creates a mock return request with a generated ID.
     - Returns clear next steps to the user.

3. **Refund Policy & Timelines**

   - User can ask about refund rules and timelines.
   - System replies using knowledge base (RAG) or a dedicated tool function.

4. **Payment Issues**

   - Handles:
     - Payment failure with money deducted.
     - Double charge / charged twice.
   - Provides generic banking and support‑contact guidance.

5. **Discounts & Coupons**

   - Explains general discount rules from knowledge base.
   - Optionally validates simple mock coupon codes (if implemented).

6. **Product & Account Information**

   - FAQ answers from knowledge base:
     - How to find products.
     - Shipping times and delivery modes.
     - Non‑returnable items.
     - Account & password reset guidance.
     - Security guidelines.

7. **Escalation to Human Support**

   - For critical issues (e.g., missing items, repeated failures, strong negative sentiment), bot:
     - Acknowledges the seriousness of the issue.
     - Shares human support contact options (email, phone, live chat).
     - Advises user on next steps.

8. **Conversation Memory**

   - Bot remembers previous user messages within the session using `ConversationBufferMemory`.

9. **Error Handling**
   - For invalid or empty input: asks the user to rephrase or provide more details.
   - For internal errors: shows a polite apology and suggests contacting support.

---

## 4. Non‑Functional Requirements

- **Usability**: Simple, intuitive chat interface with clear messages and quick‑action buttons.
- **Performance**: Responses within a few seconds on a CPU‑only machine.
- **Reliability**: Graceful handling of invalid inputs and missing order IDs.
- **Extensibility**: Easy to replace mock tools with real APIs or databases.
- **Maintainability**: Modular code structure and clear separation of concerns.

---

### 5 Key Modules

#### 5.1 `backend/app.py`

- Creates Flask app and enables CORS.
- Initializes:
  - LLM via `llm_loader.load_llm()`.
  - Vector store via `rag.vectorstore.load_vectorstore()`.
  - Chat agent via `agents.agent_router.create_agent(llm, vectorstore)`.
- Defines endpoints:
  - `/` – renders `index.html`.
  - `/chat` – main POST endpoint that accepts JSON `{ "query": "..." }` and returns `{ "response": "..." }`.
  - `/api/order-status`, `/api/create-return`, `/api/refund-policy` – auxiliary APIs.

#### 5.2 `agents/agent_router.py`

- Defines:
  - E‑commerce keyword lists.
  - Utility functions:
    - `is_ecommerce_query(query: str)`.
    - `extract_order_id(text: str)`.
    - `clean_answer(text: str)`.
    - Optional: sentiment detection or intent categorization.
  - `create_agent(llm, vectorstore)`:
    - Builds `ConversationalRetrievalChain` with QA prompt and memory.
    - Returns an `agent(query: str)` function that:
      - Handles greetings, help, and thanks.
      - Checks for out‑of‑scope queries.
      - Routes:
        - Order tracking → `get_order_status`.
        - Returns/exchanges → `create_return_request`.
        - Payment related → `payment_failed_help`, `double_charge_help`.
        - Refund policy → `get_refund_policy`.
        - Otherwise → calls the QA RAG chain.

#### 5.3 `backend/mock_tools.py`

- Contains mock data:
  `MOCK_ORDERS = {
"ORD123": {...},
"ORD456": {...},
"ORD789": {...},
}`

- Functions:

- `get_order_status(order_id: str) -> str`
- `create_return_request(order_id: str, reason: str) -> str`
- `get_refund_policy() -> str`
- `payment_failed_help() -> str`
- `double_charge_help() -> str`
- (optional) `check_product_availability(...)`, `get_product_recommendations(...)`

- Implements simple business rules (e.g., return eligibility window).

#### 5.2.4 `llm/llm_loader.py`

- Uses `transformers.pipeline` with a text‑to‑text model such as `google/flan-t5-base`.
- Wraps the pipeline in `HuggingFacePipeline` to be used by LangChain.

#### 5.2.5 `rag/embeddings.py` & `rag/vectorstore.py`

- `embeddings.py`:
- Loads `HuggingFaceEmbeddings` with model `all-MiniLM-L6-v2` (default).
- `vectorstore.py`:
- Imports documents from `data/knowledge_base.py`.
- Builds a FAISS index from these documents.
- Returns a vector store object which is used in the QA chain.

#### 5.2.6 `data/knowledge_base.py`

- Contains a list of text strings describing:
- How to find products.
- Order tracking and statuses.
- Shipping and delivery timelines.
- Return and refund rules.
- Payment options and failure handling.
- Discount / coupon usage.
- Product information and stock.
- Account management and security.
- Support and escalation procedures.

#### 5.2.7 `templates/index.html` & `static/style.css`

- Provide:
- A responsive chat widget with:
  - Header, greeting, quick‑action buttons.
  - Message area with user and bot bubbles.
  - Input box and send button.
  - Optional typing indicator and feedback section.
- JavaScript to:
  - Append messages to chat.
  - Call `/chat` endpoint via `fetch`.
  - Handle quick buttons (e.g., “Track my order”, “Payment issue”).

---

## 6. How to Run the Project

### 6.1 Environment Setup

1. Install Python 3.9+.
2. Create and activate a virtual environment (`conda` or `venv`).
3. Install dependencies from requirement.txt

### 6.2 Running the Server

From the project root (`E-Commerce-AI-Support-Bot`):

**Option A – Using `python -m backend.app`:**

The server will start at: `http://127.0.0.1:5000/`

### 6.3 Interacting with the Bot

Open a browser and go to `http://127.0.0.1:5000`.  
Use the chat widget to try prompts like:

- `Hi`
- `Where is my order ORD123?`
- `I want to return order ORD789 because it arrived damaged`
- `Tell me your refund policy`
- `My payment failed but money was deducted`
- `I was charged twice for my order`
- `Tell me about discounts and offers`
- `I think courier is not responding and my items are missing`

---

## 7. Testing & Validation

### 7.1 Manual Test Cases

| ID   | Scenario                    | Input Example                            | Expected Outcome                                  |
| ---- | --------------------------- | ---------------------------------------- | ------------------------------------------------- |
| TC1  | Greeting                    | `Hi`                                     | Bot introduces itself and explains capabilities.  |
| TC2  | Order status (valid)        | `Where is my order ORD123?`              | Shows status, dates, and short explanation.       |
| TC3  | Order status (missing ID)   | `Where is my order`                      | Asks user to provide a valid Order ID.            |
| TC4  | Return eligible order       | `I want to return order ORD789`          | Creates return request with ID and next steps.    |
| TC5  | Return not eligible         | `Return order ORD123` (not delivered)    | Explains that return is not yet allowed.          |
| TC6  | Refund policy               | `Tell me about your refund policy`       | Provides refund timelines and rules.              |
| TC7  | Payment failure             | `My payment failed`                      | Explains auto‑reversal and contact details.       |
| TC8  | Double charge               | `I was charged twice`                    | Explains double charge handling process.          |
| TC9  | Out of scope                | `Explain Python inheritance`             | Says it handles only e‑commerce support.          |
| TC10 | Escalation (critical issue) | `My order arrived but items are missing` | Provides escalation message and support contacts. |

### 7.2 Evaluation Criteria Coverage

- Intent detection and routing.
- Entity extraction (Order IDs).
- Use of external tools (mock functions).
- Use of knowledge base (RAG).
- Error and edge‑case handling.
- Escalation mechanism.
- UI usability.
- Code modularity and documentation.

---

## 8. Limitations and Future Work

### 8.1 Current Limitations

- Uses mock data instead of real databases/APIs.
- English‑only responses.
- Simple keyword‑based intent detection (no ML classifier).
- In‑memory state only (conversation not persisted across server restarts).

### 8.2 Future Enhancements

- Integrate with real order management and payment systems.
- Add authentication and personalized context per user.
- Replace keyword intents with a trained intent classification model.
- Add support for regional languages (e.g., Hindi, Kannada).
- Deploy as a cloud service and integrate with a live e‑commerce site.

---

## 9. Conclusion

This project implements a complete **E‑Commerce AI Support Bot** using modern NLP tools and a RAG architecture. It demonstrates how a combination of:

- Rule‑based intent routing,
- Mock transactional tools, and
- Retrieval‑based QA over a curated knowledge base

can deliver a practical, extensible customer support assistant.  
The solution is suitable as a capstone project, showcasing both software engineering discipline and applied AI capabilities in a realistic e‑commerce scenario.

---
