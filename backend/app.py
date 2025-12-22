from flask import Flask
from llm.llm_loader import load_llm
from rag.vectorstore import load_vectorstore
from agents.agent_router import create_agent

app = Flask(__name__)

print("🔄 Initializing system...")

llm = load_llm()
vectorstore = load_vectorstore()
agent = create_agent(llm, vectorstore)

print("✅ System ready")

@app.route("/")
def home():
    return "Welcome to the E-Commerce AI Support Bot!"

if __name__ == "__main__":
    app.run(debug=True)
