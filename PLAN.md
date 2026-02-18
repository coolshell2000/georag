Scientific Big Data RAG Development Plan
This document summarizes the RAG system and its web application.

1. Sample datasets collecting from the web
Find some small datasets from the web, common formats used in geophysics for seismic data processing, such as SEG-Y, MiniSEED, etc. netcdf, hdf5, etc
2. Core RAG Integration
Generate description for each dataset, and store the description in a vector database.
Semantic Search: Implemented using SentenceTransformer and FAISS for efficient vector-based dataset retrieval.
Web Interface: A Flask-based web app with a responsive UI for searching and browsing datasets.
3. AI Summarization Feature
Gemini Integration: Connected to the Gemini API (gemini-2.0-flash) for on-demand dataset summarization.
Interactive UI: Added a ✨ icon to each search result to trigger a summary, which appears in a retractable purple section.
Global Controls: Added "Show All Summaries" and "Hide All Summaries" buttons for bulk management of AI content.
4. Stability & Robustness Fixes
PyTorch Meta Tensor Fix: Resolved a critical "Cannot copy out of meta tensor" error by explicitly forcing CPU device usage in Flask threads.
Rate Limit Resilience: Implemented exponential backoff retries using the tenacity library to handle Gemini API 429 Resource exhausted errors gracefully.
Environment Management: Moved sensitive API keys to a .env file and updated dependencies.
🛠 Current System State
Backend: Flask server with /search and /summarize endpoints.
Models: all-MiniLM-L6-v2 (Embeddings), gemini-2.0-flash (Summarization).
Frontend: Vanilla HTML/JS with modern, dynamic controls.
🚀 Potential Next Steps
Persistent Cache: Store generated summaries to avoid redundant API calls and save costs.
Enhanced Filtering: Add date ranges and other filters to the search UI.
Multi-user Support: Implement basic authentication or session-based favorites.
Performance: Optimize the FAISS index for even larger datasets.
