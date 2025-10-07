# backend/main.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.utils.foo import ask_chatbot

app = Flask(__name__)
CORS(app)  # Allows React frontend to connect without CORS issues

@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return chatbot response."""
    data = request.get_json()
    user_query = data.get("message", "")

    if not user_query:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = ask_chatbot(user_query)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)


