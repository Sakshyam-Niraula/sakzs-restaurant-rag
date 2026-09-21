# Sakz's Restaurant — AI RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for Sakz's Restaurant.

The chatbot answers restaurant-related questions using a controlled restaurant knowledge base. It retrieves relevant information using vector similarity search and then uses Gemini to generate a natural-language answer grounded in the retrieved context.

---

## 1. Project Overview

Sakz's Restaurant AI is a working RAG prototype designed to answer questions about:

- Menu items and prices
- Opening hours
- Restaurant location and contact information
- Food delivery
- Reservations
- Payment methods
- Current offers
- Frequently asked questions

The chatbot is designed to avoid making up information. If the requested information is not available in the restaurant knowledge base, the system clearly tells the user that the information is unavailable.

---

## 2. Core RAG Pipeline

The system follows this process:

User Question
        ↓
Question Embedding
        ↓
FAISS Vector Search
        ↓
Relevant Knowledge-Base Chunks
        ↓
Context Construction
        ↓
Gemini LLM
        ↓
Grounded Restaurant Answer

The main principle is:

> Retrieve first, generate second.

The language model is not allowed to answer from general knowledge. It receives the relevant restaurant information retrieved from the knowledge base.

---

## 3. Technologies Used

### Backend

- Python
- Flask
- PyMuPDF
- FAISS
- NumPy
- Google Gemini API
- python-dotenv
- Gunicorn

### Frontend

- HTML
- CSS
- JavaScript

### Embedding Model

`gemini-embedding-001`

The project uses Google's Gemini Embedding API to convert both
knowledge-base chunks and user queries into numerical vectors.

Document chunks use the `RETRIEVAL_DOCUMENT` task type, while user
questions use the `RETRIEVAL_QUERY` task type.

The resulting embeddings use 768 dimensions in the project's FAISS

### Vector Database

FAISS using inner-product similarity search.

The current vector store contains 12 knowledge-base chunks represented
as 768-dimensional vectors.

### Language Model

Google Gemini API using the configured Gemini model.

---

## 4. Project Structure

sakzs-restaurant-rag/
│
├── app.py
├── README.md
├── requirements.txt
├── .env
│
├── data/
│   ├── sakzs_restaurant.txt
│   └── vector_store/
│       ├── sakzs.index
│       └── chunks.txt
│
├── rag/
│   ├── __init__.py
│   ├── loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── faiss_store.py
│   ├── gemini_client.py
│   └── rag_pipeline.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── tests/
    └── test_questions.md
