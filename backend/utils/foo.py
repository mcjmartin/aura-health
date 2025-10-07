from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Load dataset ---
print("Loading psychology dataset...")
data = load_dataset("samhog/psychology-10k")["train"]
questions = [q["question"] for q in data]
answers = [q["answer"] for q in data]

# --- Create embeddings ---
print("Creating embeddings (this may take a minute)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(questions, convert_to_numpy=True)

# --- Build FAISS index ---
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

def ask_chatbot(user_query, top_k=3):
    """Return a GPT-based answer using psychology dataset as context."""
    query_embedding = model.encode([user_query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve the top relevant Q&A pairs
    context = "\n".join(
        [f"Q: {questions[i]}\nA: {answers[i]}" for i in indices[0]]
    )

    prompt = f"""
    You are a warm, empathetic mental health assistant.
    Use the psychological context below to give helpful and safe advice.

    Context:
    {context}

    User question: {user_query}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content