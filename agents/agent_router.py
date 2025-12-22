from typing import Optional

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from prompts.system_prompt import QA_PROMPT

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

# Quick intent filter.
def is_ecommerce_query(query: str) -> bool:
    q = query.lower()
    return any(word in q for word in ECOMMERCE_KEYWORDS)

def create_agent(llm, vectorstore):
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
