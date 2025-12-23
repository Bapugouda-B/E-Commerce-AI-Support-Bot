from typing import Optional

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from prompts.system_prompt import QA_PROMPT
from backend.mock_tools import (
    get_order_status,
    create_return_request,
    get_refund_policy,
    payment_failed_help,
    double_charge_help,
)
import re


# Keywords used to quickly check if a query is related to e‑commerce.
ECOMMERCE_KEYWORDS = [
    "order", "refund", "payment", "pay", "card", "upi", "wallet",
    "shipping", "delivery", "track", "tracking",
    "product", "item", "size", "color", "stock", "availability",
    "price", "discount", "offer", "coupon", "promo",
    "return", "replace", "exchange", "cancel", "cancellation",
    "invoice", "bill", "receipt",
    "account", "login", "signup", "register", "address",
]

def escalation_message() -> str:
    return (
        "I might not be able to fully resolve this through the chatbot. "
        "I recommend escalating this to a human support agent.\n\n"
        "You can contact customer support via:\n"
        "- Email: support@example.com\n"
        "- Phone: 1800-123-456\n"
        "- Live chat (9 AM – 6 PM)"
    )

# Quick intent filter.
def is_ecommerce_query(query: str) -> bool:
    q = query.lower()
    return any(word in q for word in ECOMMERCE_KEYWORDS)

def clean_answer(text: str) -> str:
    """
    Cleanup helper for LLM answers.

    Sometimes the model may echo prompt labels like “Question:” or “Answer:”.
    This function removes those fixed fragments and normalizes whitespace so
    the final message looks like a natural support reply.
    """
    if not text:
        return ""

    patterns = [
        r"(?i)customer question:.*",
        r"(?i)assistant answer:.*",
        r"(?i)store information:.*",
        r"(?i)question:\s*",
        r"(?i)answer:\s*",
    ]
    cleaned = text
    for p in patterns:
        cleaned = re.sub(p, "", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_order_id(text: str) -> Optional[str]:
    """
    Extract an order ID like ORD123 or a numeric ID from free text.
    Ignores the generic word 'order' and strips punctuation.
    """
    tokens = text.replace("#", " ").replace(",", " ").split()
    for t in tokens:
        # remove trailing punctuation like ? or .
        t_clean = t.strip().upper().rstrip("?.!:,")
        if t_clean == "ORDER":
            continue
        if t_clean.startswith("ORD") and len(t_clean) > 3:
            return t_clean
        if t_clean.isdigit():
            return t_clean
    return None


def create_agent(llm, vectorstore):
    """
    Agent factory.

    - Builds a ConversationalRetrievalChain (LLM + vector store + memory)
      used for FAQ / policy questions (shipping time, discounts, payments, etc.).
    - Wraps that chain in an `agent` function which:
        * Filters out non‑ecommerce queries.
        * Calls mock backend tools for order_status / return / refund policy.
        * Falls back to RAG+LLM when no tool is needed.
    """

    # Multi‑turn chat memory so the chain can see previous messages.
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )

    # RAG chain over your knowledge base documents.
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        chain_type="stuff",
        return_source_documents=False,
        verbose=False,
    )

    def agent(query: str) -> str:
        q_lower = query.lower()
        
        # Friendly greetings
        if q_lower.strip() in ["hi", "hello", "hey", "good morning", "good evening"]:
            return (
                "Hi! 👋 I’m your shopping assistant. "
                "I can help you track orders, manage returns, handle payments, "
                "or answer questions about delivery and offers."
            )

        # Generic help
        if q_lower.strip() in ["i need help", "help", "can you help me"]:
            return (
                "Of course! 😊 Please tell me what you need help with — "
                "for example, tracking an order, returns, refunds, or payment issues."
            )

        # 0. Polite appreciation
        if any(p in q_lower for p in ["thank you", "thanks", "appreciate", "good job"]):
            return (
                "You’re welcome! If you have any more questions about orders, "
                "shipping, returns, or payments, feel free to ask anytime."
            )

        # Repeated complaints / no response
        if "multiple complaints" in q_lower or "no response" in q_lower:
            return (
                "I’m really sorry about the inconvenience. "
                "It looks like this issue needs attention from our human support team.\n\n"
                "You can contact customer support via:\n"
                "- Email: support@example.com\n"
                "- Phone: 1800-123-456\n"
                "- Live chat (9 AM – 6 PM)"
            )
        # Very short or unclear queries
        if len(q_lower.split()) < 2:
            return (
                "Could you please provide a bit more detail? 😊 "
                "For example, you can ask about order status, delivery time, refunds, or payments."
            )
        # 1. Out-of-scope
        if not is_ecommerce_query(q_lower):
             return (
                "I can help with shopping-related questions like orders, "
                "returns, refunds, payments, delivery, and offers. "
                "Please let me know how I can assist you."
            )

        # 2. Escalation cases (CRITICAL)
        if any(p in q_lower for p in [
            "missing item", "items missing", "courier not responding",
            "multiple complaints", "no response", "not responding"
        ]):
            return escalation_message()

        # 3. Order tracking
        if "order" in q_lower and ("status" in q_lower or "track" in q_lower or "where is" in q_lower):
            order_id = extract_order_id(query)
            if not order_id:
                return (
                    "I can help you track an order, but I need the order ID first. "
                    "For example: 'Where is my order ORD123?'."
                )
            return get_order_status(order_id)

        # 4. Return / exchange
        if any(p in q_lower for p in ["return", "replace", "exchange"]):
            order_id = extract_order_id(query)
            if not order_id:
                return (
                    "Please include your order ID to start a return or exchange. "
                    "Example: 'I want to return order ORD123 because the item is damaged.'"
                )
            return create_return_request(order_id, query)

        # 5. Modify / cancel order
        if "modify my order" in q_lower or "change my order" in q_lower:
            return (
                "Orders can be modified or cancelled only while they are in Pending "
                "or Processing status. Once shipped, changes are not possible and "
                "a return may be requested after delivery."
            )
            
        # Mixed intent: payment + cancel
        if "payment" in q_lower and "cancel" in q_lower:
            payment_msg = (
                "If your payment failed but money was deducted, "
                "it is usually reversed automatically within 5–7 business days."
            )
            cancel_msg = (
                "Regarding cancellation: orders can only be cancelled while they are "
                "in Pending or Processing status. Shipped orders cannot be cancelled "
                "and may need a return after delivery."
            )
            return payment_msg + "\n\n" + cancel_msg

        # 6. Payment failures
        if "payment failed" in q_lower or "upi failed" in q_lower:
            return payment_failed_help()

        if "charged twice" in q_lower or "double charge" in q_lower:
            return double_charge_help()

        # 7. Refund policy
        if "refund policy" in q_lower:
            return get_refund_policy()

        # 8. Generic help
        if q_lower.strip() in ["help", "i need help"]:
            return (
                "I can assist you with:\n"
                "- Order tracking\n"
                "- Returns & refunds\n"
                "- Payment issues\n"
                "- Delivery & offers\n\n"
                "Please tell me what you need help with."
            )

        # 9. RAG fallback (FAQs only)
        try:
            result = qa_chain({"question": query})
            answer = clean_answer(result.get("answer", ""))
        except Exception:
            return (
                "Sorry, I ran into a technical issue. Please try again later or "
                "contact customer support."
            )

        if not answer or len(answer) < 20:
            return (
                "I’m not completely sure about that. Could you please provide "
                "a bit more detail about your issue?"
            )

        return answer

    # Return the configured agent function to the Flask app.
    return agent
