from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from backend.mock_tools import get_order_status, create_return_request, get_refund_policy

from llm.llm_loader import load_llm
from rag.vectorstore import load_vectorstore
from agents.agent_router import create_agent

app = Flask(__name__)
CORS(app)

print("Initializing system...")

llm = load_llm()
vectorstore = load_vectorstore()
agent = create_agent(llm, vectorstore)

print("System is ready")

@app.route("/")
def home():
    return render_template_string("""
        <html>
          <head><title>Ecommerce AI Bot</title></head>
          <body>
            <h1>Ecommerce AI Bot API</h1>
            <p>Backend is running on localhost.</p>
          </body>
        </html>
    """)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        query = data.get("query", "").strip()

        if not query:
            return jsonify({
                "response": "Please type a question so I can help you 🙂"
            })

        answer = agent(query)

        return jsonify({"response": answer})

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "response": "Sorry, I ran into an internal issue. Please try again."
        })

@app.route("/api/order-status", methods=["POST"])
def api_order_status():
    data = request.get_json(force=True)
    order_id = data.get("order_id", "").strip()
    return jsonify({"response": get_order_status(order_id)})

@app.route("/api/create-return", methods=["POST"])
def api_create_return():
    data = request.get_json(force=True)
    order_id = data.get("order_id", "").strip()
    reason = data.get("reason", "").strip()
    return jsonify({"response": create_return_request(order_id, reason)})

@app.route("/api/refund-policy", methods=["GET"])
def api_refund_policy():
    return jsonify({"response": get_refund_policy()})

if __name__ == "__main__":
    app.run(debug=True)
