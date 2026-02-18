import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os

def main():
    # Load metadata
    with open("data/metadata_descriptions.json", "r") as f:
        data = json.load(f)
    
    descriptions = [item["description"] for item in data]
    
    # Load model
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = model.encode(descriptions)
    embeddings = np.array(embeddings).astype('float32')
    
    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index and metadata mapping
    os.makedirs("data/index", exist_ok=True)
    faiss.write_index(index, "data/index/geophysical_data.index")
    
    # Save the mapping between index and original data
    with open("data/index/mapping.json", "w") as f:
        json.dump(data, f, indent=4)
        
    print(f"Index built with {len(data)} items and saved to data/index/")

if __name__ == "__main__":
    main()
