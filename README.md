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
- Sentence Transformers
- FAISS
- Google Gemini API
- python-dotenv

### Frontend

- HTML
- CSS
- JavaScript

### Embedding Model

`all-MiniLM-L6-v2`

### Vector Database

FAISS using normalized embeddings and inner-product similarity search.

### Language Model

Google Gemini API using the configured Gemini model.

---

## 4. Project Structure

```text
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
└── static/
    ├── style.css
    └── script.js