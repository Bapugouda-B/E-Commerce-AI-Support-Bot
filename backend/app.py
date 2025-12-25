from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import json
from datetime import datetime

from backend.mock_tools import (
    get_order_status,
    create_return_request,
    get_refund_policy,
)
from llm.llm_loader import load_llm
from rag.vectorstore import load_vectorstore
from agents.agent_router import create_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

# Initialize models
logger.info("Initializing Ecommerce AI Support System...")
try:
    llm = load_llm()
    vectorstore = load_vectorstore()
    agent = create_agent(llm, vectorstore)
    logger.info("✅ System initialized successfully!")
except Exception as e:
    logger.error(f"❌ Initialization failed: {str(e)}")
    raise


@app.route("/")
def home():
    """Serve the chat interface"""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json(force=True)
        query = data.get("query", "").strip()

        if not query:
            return (
                jsonify({"response": "Please type a message so I can help you! 😊"}),
                400,
            )

        # Log the incoming query
        logger.info(f"Query: {query[:100]}")

        # Get response from agent
        answer = agent(query)

        logger.info(f"Response length: {len(answer)} chars")

        return (
            jsonify({"response": answer, "timestamp": datetime.now().isoformat()}),
            200,
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "response": (
                        "Oops! Something went wrong. 😅\n\n"
                        "Please try again or contact support at:\n"
                        "📧 support@ecommerce.com\n"
                        "📞 1-800-123-456"
                    )
                }
            ),
            500,
        )


@app.route("/api/order-status", methods=["POST"])
def api_order_status():
    """API endpoint for order status"""
    try:
        data = request.get_json(force=True)
        order_id = data.get("order_id", "").strip()

        if not order_id:
            return jsonify({"error": "Order ID required"}), 400

        response = get_order_status(order_id)
        return jsonify({"response": response}), 200
    except Exception as e:
        logger.error(f"Order status error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/create-return", methods=["POST"])
def api_create_return():
    """API endpoint for creating returns"""
    try:
        data = request.get_json(force=True)
        order_id = data.get("order_id", "").strip()
        reason = data.get("reason", "").strip()

        if not order_id or not reason:
            return jsonify({"error": "Order ID and reason required"}), 400

        response = create_return_request(order_id, reason)
        return jsonify({"response": response}), 200
    except Exception as e:
        logger.error(f"Return creation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/refund-policy", methods=["GET"])
def api_refund_policy():
    """API endpoint for refund policy"""
    try:
        response = get_refund_policy()
        return jsonify({"response": response}), 200
    except Exception as e:
        logger.error(f"Refund policy error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    """Collect user feedback"""
    try:
        data = request.get_json(force=True)
        message_id = data.get("message_id")
        helpful = data.get("helpful")
        timestamp = data.get("timestamp")

        logger.info(f"Feedback: Message {message_id} - Helpful: {helpful}")

        # You can store this in a database later
        return jsonify({"status": "received"}), 200
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "Ecommerce AI Support",
            }
        ),
        200,
    )


if __name__ == "__main__":
    logger.info("Starting Ecommerce AI Support Server...")
    app.run(debug=True, host="0.0.0.0", port=5000)
