import os
import json
import faiss
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import google.generativeai as genai
from tenacity import retry, wait_exponential, stop_after_attempt
import threading

load_dotenv()

app = Flask(__name__)

@app.route('/branding/<path:filename>')
def serve_branding(filename):
    return send_from_directory('branding', filename)

# Download counter
DOWNLOAD_STATS_FILE = "data/download_stats.json"
_stats_lock = threading.Lock()

def load_stats():
    if os.path.exists(DOWNLOAD_STATS_FILE):
        with open(DOWNLOAD_STATS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(DOWNLOAD_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def increment_download(filename):
    with _stats_lock:
        stats = load_stats()
        stats[filename] = stats.get(filename, 0) + 1
        save_stats(stats)
        return stats[filename]

# Initialize AI and Search
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model_gemini = genai.GenerativeModel("gemini-2.0-flash")
else:
    model_gemini = None

print("Loading search models...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index("data/index/geophysical_data.index")
with open("data/index/mapping.json", "r") as f:
    mapping = json.load(f)

@app.route("/")
def index_view():
    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    """Serve a file from data/raw and track downloads."""
    data_dir = os.path.join(os.getcwd(), "data", "raw")
    if not os.path.exists(os.path.join(data_dir, filename)):
        return jsonify({"error": "File not found"}), 404
    count = increment_download(filename)
    return send_from_directory(data_dir, filename, as_attachment=True)

@app.route("/stats")
def stats():
    """Return download statistics."""
    return jsonify(load_stats())

@app.route("/search")
def search():
    query = request.args.get("q", "")
    if not query:
        return jsonify([])
    
    # Embed query
    query_vec = embed_model.encode([query]).astype('float32')
    
    # Search index
    D, I = index.search(query_vec, k=5)
    
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < len(mapping) and idx != -1:
            item = mapping[idx].copy()
            item["score"] = float(score)
            # Convert L2 distance to cosine similarity percentage: similarity = (1 - distance^2 / 2) * 100
            # Since vectors are normalized, L2^2 = 2(1-cosine). So cosine = 1 - L2^2/2.
            similarity = max(0, (1 - float(score) / 2.0)) * 100
            item["similarity"] = round(similarity, 1)
            results.append(item)
            
    return jsonify(results)

@app.route("/datasets")
def get_datasets():
    """Return all datasets with metadata for map view."""
    return jsonify(mapping)

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def call_gemini(prompt):
    if not model_gemini:
        return "Gemini API key not configured."
    response = model_gemini.generate_content(prompt)
    return response.text

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    description = data.get("description", "")
    filename = data.get("file", "Unknown File")
    
    if not description:
        return jsonify({"summary": "No description available to summarize."})
    
    prompt = f"Summarize the following geophysical dataset metadata for a researcher. Focus on its format, dimensions, and potential usefulness.\n\nFile: {filename}\nMetadata: {description}"
    
    try:
        summary = call_gemini(prompt)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"summary": f"Error generating summary: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
