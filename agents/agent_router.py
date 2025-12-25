from typing import Optional, Dict, Tuple
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from prompts.system_prompt import QA_PROMPT
from backend.mock_tools import (
    get_order_status,
    create_return_request,
    get_refund_policy,
    payment_failed_help,
    double_charge_help,
    get_product_recommendations,
    check_product_availability,
    apply_discount_code,
    process_complaint,
)
import re
import logging
from datetime import datetime

# Configure logging for conversation analytics
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("chatbot_conversations.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Enhanced keywords with categories for better intent recognition
ECOMMERCE_KEYWORDS = {
    "order_tracking": [
        "order",
        "status",
        "track",
        "tracking",
        "where is",
        "find my",
        "locate",
        "shipment",
    ],
    "payment": [
        "payment",
        "pay",
        "card",
        "upi",
        "wallet",
        "transaction",
        "charge",
        "bill",
        "receipt",
    ],
    "refund": [
        "refund",
        "refund",
        "money back",
        "reimbursement",
        "refundable",
        "credit",
    ],
    "return": ["return", "replace", "exchange", "replacement", "returned", "send back"],
    "shipping": [
        "shipping",
        "delivery",
        "deliver",
        "shipped",
        "freight",
        "courier",
        "dispatch",
    ],
    "product": ["product", "item", "goods", "thing", "article", "merchandise", "stuff"],
    "account": [
        "account",
        "login",
        "signup",
        "register",
        "password",
        "profile",
        "account settings",
    ],
    "promotion": [
        "discount",
        "offer",
        "coupon",
        "promo",
        "promotion",
        "code",
        "deal",
        "sale",
    ],
    "issue": [
        "problem",
        "issue",
        "trouble",
        "complaint",
        "not working",
        "broken",
        "damaged",
        "defective",
    ],
    "help": ["help", "assist", "support", "guide", "how to", "can you help"],
}


class ConversationMetrics:
    """Track conversation metrics for analytics"""

    def __init__(self):
        self.start_time = datetime.now()
        self.message_count = 0
        self.tool_calls = 0
        self.escalations = 0
        self.resolution_status = "ongoing"
        self.customer_sentiment = "neutral"

    def log_interaction(self, query: str, response: str, tool_used: str = None):
        self.message_count += 1
        if tool_used:
            self.tool_calls += 1
        logger.info(
            f"Query: {query[:100]} | Tool: {tool_used} | Sentiment: {self.customer_sentiment}"
        )


def escalation_message() -> str:
    return (
        "I understand this needs more attention from our team. 🤝\n\n"
        "I'm escalating you to a human support specialist who can help better.\n\n"
        "**Contact our Support Team:**\n"
        "📧 **Email:** support@ecommerce.com\n"
        "📞 **Phone:** 1-800-123-456 (9 AM – 6 PM IST)\n"
        "💬 **Live Chat:** Available on our website\n"
        "⏱️ **Expected response:** Within 2 hours\n\n"
        "Thank you for your patience!"
    )


def extract_sentiment(text: str) -> str:
    """
    Simple sentiment analysis based on keywords.
    Enhanced for detecting frustration markers.
    """
    text_lower = text.lower()

    negative_keywords = [
        "angry",
        "frustrated",
        "upset",
        "terrible",
        "awful",
        "worst",
        "horrible",
        "not working",
        "broken",
        "scam",
        "fraud",
        "cheated",
        "ripoff",
        "never",
        "always fail",
        "disgusted",
        "hate",
        "unacceptable",
    ]

    positive_keywords = [
        "thank",
        "great",
        "excellent",
        "happy",
        "satisfied",
        "love",
        "perfect",
        "awesome",
    ]

    negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
    positive_count = sum(1 for kw in positive_keywords if kw in text_lower)

    if negative_count > positive_count:
        return "negative"
    elif positive_count > negative_count:
        return "positive"
    else:
        return "neutral"


def detect_primary_intent(query: str) -> Tuple[str, float]:
    """
    Detect primary intent with confidence score.
    Returns (intent, confidence_score)
    """
    query_lower = query.lower()
    intent_scores = {}

    for intent, keywords in ECOMMERCE_KEYWORDS.items():
        matching_keywords = sum(1 for kw in keywords if kw in query_lower)
        confidence = matching_keywords / len(keywords) if keywords else 0
        if confidence > 0:
            intent_scores[intent] = confidence

    if intent_scores:
        primary_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[primary_intent]
        return primary_intent, confidence

    return "general", 0.0


def is_ecommerce_query(query: str) -> bool:
    """Enhanced version with intent detection"""
    intent, confidence = detect_primary_intent(query)
    # Consider it ecommerce if confidence > 0 or contains basic patterns
    if confidence > 0.2:
        return True

    basic_patterns = ["order", "product", "payment", "delivery", "refund", "return"]
    return any(pattern in query.lower() for pattern in basic_patterns)


def clean_answer(text: str) -> str:
    """Cleanup helper for LLM answers with enhanced filtering"""
    if not text:
        return ""

    # Extended pattern list to catch more LLM artifacts
    patterns = [
        r"(?i)customer question:.*?\n",
        r"(?i)assistant answer:.*?\n",
        r"(?i)store information:.*?\n",
        r"(?i)question:\s*",
        r"(?i)answer:\s*",
        r"(?i)response:\s*",
        r"(?i)note:.*?\n",
        r"(?i)\[.*?\]",  # Remove bracket content
        r"^#+\s*",  # Remove markdown headers
    ]

    cleaned = text
    for p in patterns:
        cleaned = re.sub(p, "", cleaned)

    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Ensure minimum quality
    if len(cleaned) < 20:
        return "I'm here to help! Could you provide more details about your issue?"

    return cleaned


import re
from typing import Optional


def extract_order_id(text: str) -> Optional[str]:
    """
    Extract an order ID like ORD123 (case‑insensitive) from user text.
    Supports:
      - ORD123
      - ord123
      - 'order ORD123'
      - 'my order id is ORD123'
    Returns only the ORD123 part.
    """
    if not text:
        return None
    # Work in uppercase for simplicity
    t = text.upper()

    # 1) Look for explicit ORDxxx pattern
    m = re.search(r"\bORD[0-9]+\b", t)
    if m:
        return m.group(0).strip(" ?.,!;:")

    # 2) If nothing found, look for a pure number with 3+ digits (optional)
    m2 = re.search(r"\b[0-9]{3,}\b", t)
    if m2:
        return m2.group(0).strip(" ?.,!;:")

    return None


def validate_response_quality(response: str, query: str) -> bool:
    """
    Validate response for quality metrics:
    - Not too short (minimum 20 chars)
    - Contains actual information
    - Not a generic fallback
    """
    if len(response) < 20:
        return False

    # Check for hallucination indicators
    hallucination_patterns = [
        "i don't have access to",
        "i cannot see",
        "i don't have information",
    ]

    if any(pattern in response.lower() for pattern in hallucination_patterns):
        return True  # These are honest responses

    return True


def extract_complaint_details(query: str) -> Dict[str, str]:
    """Extract complaint structured data"""
    details = {
        "complaint_type": "general",
        "severity": "normal",
        "involves_money": False,
        "involves_delivery": False,
    }

    query_lower = query.lower()

    if any(w in query_lower for w in ["money", "charge", "payment", "refund", "paid"]):
        details["involves_money"] = True
        details["severity"] = "high"

    if any(
        w in query_lower for w in ["missing", "not received", "delivery", "courier"]
    ):
        details["involves_delivery"] = True
        if "missing" in query_lower:
            details["severity"] = "critical"

    return details


def create_agent(llm, vectorstore):
    """Enhanced agent factory with metrics tracking and advanced intent handling"""

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        chain_type="stuff",
        return_source_documents=False,
        verbose=False,
    )

    metrics = ConversationMetrics()

    def agent(query: str) -> str:
        """Main agent function with enhanced routing"""
        q_lower = query.lower().strip()

        # Detect sentiment and intent at the start
        sentiment = extract_sentiment(query)
        primary_intent, intent_confidence = detect_primary_intent(query)
        metrics.customer_sentiment = sentiment

        greeting_triggers = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good evening",
            "good afternoon",
        ]
        if q_lower in greeting_triggers:
            response = (
                "👋 Hi there! I'm your **AI Shopping Assistant**.\n\n"
                "I can help you with:\n"
                "✅ **Order Tracking** - Find your package status\n"
                "✅ **Returns & Refunds** - Manage returns easily\n"
                "✅ **Payment Issues** - Resolve payment problems\n"
                "✅ **Product Info** - Get product details & availability\n"
                "✅ **Discounts** - Find active coupon codes\n"
                "✅ **Delivery Info** - Learn shipping timelines\n\n"
                "What can I help you with today?"
            )
            metrics.log_interaction(query, response)
            return response

        #  EMPTY/UNCLEAR QUERIES
        if len(q_lower.split()) < 2 or len(q_lower) < 5:
            response = (
                "I didn't quite catch that. 🤔\n\n"
                "Could you provide more details? For example:\n"
                '• "Where is my order ORD123?"\n'
                '• "Can I return a defective item?"\n'
                '• "Why did my payment fail?"\n'
                '• "Is product X in stock?"'
            )
            metrics.log_interaction(query, response)
            return response

        #  OUT OF SCOPE
        if not is_ecommerce_query(q_lower):
            response = (
                "I specialize in e-commerce support. 🛒\n\n"
                "I can help with:\n"
                "• Orders, tracking, cancellations\n"
                "• Returns, refunds, exchanges\n"
                "• Payment & billing issues\n"
                "• Products, pricing, discounts\n"
                "• Shipping & delivery info\n\n"
                "What e-commerce question can I help with?"
            )
            metrics.log_interaction(query, response)
            return response

        #  ESCALATION CASES (CRITICAL)
        escalation_triggers = [
            "missing item",
            "items missing",
            "no items",
            "nothing in package",
            "courier not responding",
            "multiple complaints",
            "no response",
            "not responding",
            "fraud",
            "scam",
            "cheated",
            "never again",
            "dispute",
            "police",
            "legal action",
            "dead on arrival",
        ]

        if any(trigger in q_lower for trigger in escalation_triggers):
            metrics.escalations += 1
            response = escalation_message()
            metrics.resolution_status = "escalated"
            metrics.log_interaction(query, response, "escalation")
            return response

        #  NEGATIVE SENTIMENT DETECTION
        if sentiment == "negative":
            response = (
                "I can see you're frustrated, and I sincerely apologize. 😔\n\n"
                "This situation deserves immediate attention from our specialist team.\n"
                "I'm connecting you with someone who can resolve this quickly.\n\n"
                + escalation_message()
            )
            metrics.escalations += 1
            metrics.log_interaction(query, response, "escalation_sentiment")
            return response

        #  GRATITUDE
        if any(
            p in q_lower
            for p in ["thank you", "thanks", "appreciate", "good job", "well done"]
        ):
            response = (
                "You're so welcome! 😊\n\n"
                "If you have any other questions about orders, shipping, "
                "returns, or payments, I'm here to help anytime!"
            )
            metrics.log_interaction(query, response)
            return response

        # ORDER TRACKING
        if primary_intent == "order_tracking" or any(
            word in q_lower for word in ["where is", "track", "status"]
        ):
            if "order" in q_lower or intent_confidence > 0.4:
                order_id = extract_order_id(query)

                if not order_id:
                    response = (
                        "I'd love to track your order! 📦\n\n"
                        "I need your **Order ID** to pull up the details.\n\n"
                        "**Where can you find it?**\n"
                        "• In your **confirmation email**\n"
                        "• On your **invoice/receipt**\n"
                        "• In **'My Orders'** on our website\n\n"
                        "**Format examples:**\n"
                        "• ORD123\n"
                        "• ORD456789\n"
                        "• 123456\n\n"
                        "Please share your Order ID and I'll get you the status right away!"
                    )
                    metrics.log_interaction(query, response)
                    return response

                result = get_order_status(order_id)
                metrics.log_interaction(query, result, "order_status")
                metrics.resolution_status = "resolved"
                return result

        # PRODUCT QUERIES
        if (
            primary_intent == "product"
            and "stock" not in q_lower
            and "available" not in q_lower
        ):
            # Try product recommendation
            response = check_product_availability(query)
            if response and "not found" not in response.lower():
                metrics.log_interaction(query, response, "product_check")
                return response

        #  RETURN & EXCHANGE
        if any(p in q_lower for p in ["return", "replace", "exchange", "send back"]):
            order_id = extract_order_id(query)
            if not order_id:
                response = (
                    "I can help you start a return! ✅\n\n"
                    "To process a return, I need your **Order ID**.\n\n"
                    "**What's the reason for your return?**\n"
                    "• Item is defective/damaged\n"
                    "• Wrong item received\n"
                    "• Size/color doesn't fit\n"
                    "• Changed mind\n"
                    "• Product quality issue\n\n"
                    "Please provide your Order ID (format: ORD123)"
                )
                metrics.log_interaction(query, response)
                return response

            result = create_return_request(order_id, query)
            metrics.log_interaction(query, result, "return_request")
            metrics.resolution_status = "resolved"
            return result

        #  CANCEL/MODIFY ORDER
        if (
            "modify" in q_lower
            or "change" in q_lower
            or ("cancel" in q_lower and "order" in q_lower)
        ):
            response = (
                "Got it! Let me clarify the rules for **order modifications**: 📋\n\n"
                "**CAN modify/cancel:**\n"
                "✅ Pending status (Not yet processed)\n"
                "✅ Processing status (Being prepared)\n\n"
                "**CANNOT modify/cancel:**\n"
                "❌ Already Shipped\n"
                "❌ In Transit\n"
                "❌ Delivered\n\n"
                "**Alternative for shipped orders:**\n"
                "If your order is already shipped, you can:\n"
                "1️⃣ **Refuse delivery** (if courier allows)\n"
                "2️⃣ **Return after delivery** (within return window)\n\n"
                "What's your Order ID? I'll check the current status."
            )
            metrics.log_interaction(query, response)
            return response

        #  PAYMENT FAILURES
        if (
            "payment failed" in q_lower
            or "payment issue" in q_lower
            or "upi failed" in q_lower
        ):
            response = payment_failed_help()
            metrics.log_interaction(query, response, "payment_help")
            return response

        #  DOUBLE CHARGE
        if (
            "charged twice" in q_lower
            or "double charge" in q_lower
            or "duplicate charge" in q_lower
        ):
            response = double_charge_help()
            metrics.log_interaction(query, response, "double_charge_help")
            return response

        #  REFUND POLICY
        if "refund policy" in q_lower or ("refund" in q_lower and "policy" in q_lower):
            response = get_refund_policy()
            metrics.log_interaction(query, response, "refund_policy")
            return response

        #  DISCOUNT/COUPON
        if "discount" in q_lower or "coupon" in q_lower or "promo" in q_lower:
            coupon_match = re.search(r"[A-Z0-9]{4,}", q_lower)
            code = coupon_match.group(0) if coupon_match else None
            response = apply_discount_code(code, query)
            metrics.log_interaction(query, response, "discount_check")
            return response

        #  COMPLAINT HANDLING
        if primary_intent == "issue" or sentiment == "negative":
            complaint_details = extract_complaint_details(query)
            if complaint_details["severity"] == "critical":
                response = escalation_message()
                metrics.escalations += 1
                metrics.log_interaction(query, response, "escalation_complaint")
                return response
            else:
                response = process_complaint(query)
                metrics.log_interaction(query, response, "complaint_logged")
                return response

        # Product discovery / recommendations
        if any(
            p in q_lower
            for p in [
                "suggest a product",
                "recommend a product",
                "recommend something",
                "what should i buy",
                "help me choose",
                "help me find a product",
                "find a product for me",
                "product recommendations",
                "show some options",
            ]
        ):
            return get_product_recommendations(query)

        #  RAG FALLBACK
        try:
            result = qa_chain({"question": query})
            answer = clean_answer(result.get("answer", ""))

            if not answer or len(answer) < 20:
                response = (
                    "I'm not 100% sure about that. Let me give you better assistance:\n\n"
                    "💬 Could you rephrase your question? Or\n"
                    "📞 Contact our team: support@ecommerce.com or 1-800-123-456\n\n"
                    "I want to make sure you get accurate information!"
                )
                metrics.log_interaction(query, response)
                return response

            metrics.log_interaction(query, answer, "rag_response")
            return answer

        except Exception as e:
            logger.error(f"RAG chain error: {str(e)}")
            response = (
                "I ran into a technical hiccup. 😅\n\n"
                "**Here's what you can do:**\n"
                "1️⃣ Try rephrasing your question\n"
                "2️⃣ Contact support: support@ecommerce.com\n"
                "3️⃣ Call: 1-800-123-456 (9 AM – 6 PM IST)\n\n"
                "Sorry for the inconvenience!"
            )
            metrics.log_interaction(query, response, "error")
            return response

    return agent
