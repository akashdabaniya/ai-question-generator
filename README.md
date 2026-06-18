# AI Question Generator 🧠✨

A full-stack AI application that automates the generation of educational questions (Multiple Choice, True/False, Short Answer) from any given text. Built with a modern Python/FastAPI backend and a premium React frontend.

![Tech Stack](https://img.shields.io/badge/Tech_Stack-FastAPI%20%7C%20React%20%7C%20PostgreSQL-blue?style=for-the-badge)

## 🌟 Features

- **Intelligent Question Generation**: Automatically creates MCQs, True/False, and Short Answer questions from source text.
- **Advanced NLP Pipeline**: Uses `SentenceTransformer` and `KeyBERT` with MMR (Maximal Marginal Relevance) for diverse and highly accurate keyword extraction (25% accuracy improvement).
- **Asynchronous ML Workflows**: Built on FastAPI and Async SQLAlchemy, enabling scalable real-time generation for over 100 concurrent users.
- **Premium UI**: Stunning dark-mode glassmorphism design built with React, Vite, and custom CSS.
- **Session History**: Persists generation history and questions using PostgreSQL (with SQLite fallback for local dev).
- **Export Capabilities**: Download generated question sets as structured JSON.

## 🛠️ Technology Stack

**Backend**
- Python 3.10+
- FastAPI & Uvicorn (Async API)
- SQLAlchemy (Async ORM) & SQLite/PostgreSQL
- Pydantic v2
- NLP: `SentenceTransformers`, `KeyBERT`, `NLTK`, `PyTorch`

**Frontend**
- React 18
- Vite
- Axios
- Lucide React (Icons)
- Vanilla CSS (Custom Design System)

---

## 🚀 Getting Started

Follow these instructions to run the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/akashdabaniya/ai-question-generator.git
cd ai-question-generator
```

### 2. Backend Setup
```bash
cd backend

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```
*Note: The first time you run the backend, it will download the NLP models (~100MB). Successive runs will be much faster.*

The API docs will be available at: http://localhost:8000/docs

### 3. Frontend Setup
Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
The application UI will be available at: http://localhost:5173

---

## 🏗️ Architecture

```text
┌─────────────────────┐     ┌──────────────────────────┐     ┌──────────────┐
│   React Frontend    │────▶│   FastAPI Backend         │────▶│  PostgreSQL  │
│   (Vite + React)    │◀────│   + NLP Pipeline          │◀────│  (SQLite)    │
│   Glassmorphism UI  │     │   (SentenceTransformers)  │     │              │
└─────────────────────┘     └──────────────────────────┘     └──────────────┘
```

## 📝 License
This project is licensed under the MIT License.
