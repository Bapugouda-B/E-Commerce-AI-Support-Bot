# E-Commerce-AI-Support-Bot

An AI-powered customer support assistant for e-commerce platforms built with Python, Flask, LangChain, Hugging Face, and FAISS. It handles natural language queries about products, orders, and policies, delivering context-aware responses through semantic search and retrieval-augmented generation.

## Project Overview

This project implements an intelligent customer support assistant using:

- **LLM**: Flan-T5-Base (HuggingFace)
- **RAG**: FAISS vector store with sentence-transformer embeddings
- **Backend**: Flask + LangChain
- **Frontend**: Interactive HTML5 chat widget

## Features

### Core Capabilities

- ✅ Order tracking with status updates
- ✅ Return/exchange request processing
- ✅ Refund policy explanations
- ✅ Payment issue resolution
- ✅ Product and delivery information via RAG
- ✅ Intent classification and routing
- ✅ Conversation memory (multi-turn)
- ✅ Escalation to human agents

### Safety & Quality

- ✅ Input validation and sanitization
- ✅ Sensitive data protection
- ✅ Hallucination prevention
- ✅ Clear fallback handling
- ✅ Conversation logging for evaluation

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

`git clone <your-repo-url>`
`cd ecommerce-ai-support`

### Create virtual environment

`conda create -n ecommerce-genai python=3.9.13`
`conda activate ecommerce-genai`

### Install dependencies

`pip install -r requirements.txt`

### Run the application

`python -m backend.app`
`The bot will be available at: `http://localhost:5000`

### RAG Pipeline

1. **Documents**: 50+ e-commerce FAQs and policies
2. **Embeddings**: Sentence-BERT (all-MiniLM-L6-v2)
3. **Vector Store**: FAISS (in-memory)
4. **Retrieval**: Top-5 documents per query
5. **Generation**: Flan-T5-Base with system prompt

## Testing Scenarios

### Test Cases for Evaluation

Use these queries to verify the bot's capabilities:

#### 1. Order Tracking

- "Where is my order?"
- "Track order ORD123"
- "What's the status of ORD456?"

#### 2. Returns & Refunds

- "I want to return ORD789"
- "What's your refund policy?"
- "Can I exchange this item?"

#### 3. Payment Issues

- "My payment failed"
- "I was charged twice"
- "Payment error on my card"

#### 4. Delivery & Shipping

- "How long is delivery?"
- "Can I change my address?"
- "Free shipping available?"

#### 5. Products & Offers

- "What discounts do you have?"
- "Is this product in stock?"
- "Size chart for shoes?"

#### 6. Escalation Cases

- "I'm missing items in my order"
- "Courier is not responding"
- "Multiple complaints, no resolution"

#### 7. Out of Scope

- "What's the weather?"
- "Tell me a joke"
- "Who is the President?"

## Evaluation Criteria Met

| Criterion                | Status | Evidence                                                |
| ------------------------ | ------ | ------------------------------------------------------- |
| Problem Understanding    | ✅     | Clear scope: orders, returns, payments, FAQs            |
| Technical Implementation | ✅     | LLM + RAG + Tool calling integrated                     |
| GIAI Concepts            | ✅     | Prompts, embeddings, vector search, agentic logic       |
| Usability                | ✅     | Clear responses, helpful fallbacks, escalation          |
| Code Quality             | ✅     | Clean structure, documented, error handling             |
| Presentation             | ✅     | Test scenarios, logs, demo-ready                        |
| Safety & Ethics          | ✅     | Input validation, no hallucinations, honest uncertainty |

## Deployment Notes

### For Production:

- Replace mock tools with real APIs
- Use Pinecone/Weaviate instead of FAISS
- Deploy with Gunicorn + Nginx
- Add authentication (API keys, user sessions)
- Monitor with logging and telemetry
- Use professional LLM API (Claude, GPT-4)

### Limitations:

- Mock data only (no real orders)
- In-memory vector store (no persistence)
- Single-turn RAG (could use conversational retrieval)
- No user authentication
- Local deployment only

## Author

Bapugouda Biradar | ECE 2024

## License

Apache 2.0

### Demo Script

## Greeting & Basic Capability

1. Hi, can you help me?
2. What can you help me with?

## Order Management

3. Where is my order ORD123?
4. Track order ORD456
5. Can I modify my order?

## Returns & Refunds

6. I want to return ORD789
7. What's your refund policy?
8. Item arrived damaged, can I return it?

## Payment Issues

9. My payment failed
10. I was charged twice

## Delivery & Logistics

11. How long will delivery take?
12. Can I change my delivery address?

## Out-of-Scope & Escalation

13. Missing items in my delivery
14. Tell me a joke
15. What's the weather today?

## Edge Cases

16. Multiple complaints, no response
17. a
18. Where is order
