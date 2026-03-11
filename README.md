# 📄 Ask Me Anything From Your PDF

### 🔍 Lens_Craft_PDF — Intelligent PDF Question Answering

Hey there! 👋
I'm **Lens_Craft_PDF**, an AI-powered system that allows you to **ask questions directly from your PDF documents** and get accurate answers instantly.

Instead of manually searching through long documents, simply **ask a question and the system retrieves the relevant information from the PDF and generates a response.**

---

# ✨ Features

📄 **PDF Ingestion**
Upload and process PDF documents easily.

🔎 **Semantic Search**
Find the most relevant information using vector embeddings.

🧠 **Retrieval-Augmented Generation (RAG)**
Combines document retrieval with AI-generated answers for accurate responses.

⚡ **Fast Backend API**
Built with **FastAPI** for high performance.

🤖 **LLM Powered**
Uses Large Language Models to understand questions and generate context-aware answers.

---

# 🧠 How It Works

1️⃣ Upload a **PDF document**
2️⃣ Text is **extracted and chunked**
3️⃣ Each chunk is converted into **vector embeddings**
4️⃣ Embeddings are stored in a **vector database**
5️⃣ When a user asks a question:

* Relevant chunks are retrieved
* AI generates an answer based on the retrieved context

This architecture is called **RAG (Retrieval-Augmented Generation)**.

---

# 🛠️ Tech Stack

* 🐍 **Python**
* ⚡ **FastAPI**
* 🧠 **Vector Embeddings**
* 📄 **PDF Processing**
* 🤖 **LLM Integration**
* 🔍 **Semantic Retrieval**

---

# 📂 Project Structure

```
project/
│
├── main.py              # FastAPI application
├── ingestion.py         # PDF ingestion pipeline
├── rag_pipeline.py      # Retrieval logic
├── embeddings.py        # Vector embedding creation
├── .env                 # Environment variables (not pushed)
├── .env.example         # Example environment variables
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/your-username/your-repo-name.git
```

Go to the project directory:

```bash
cd your-repo-name
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔑 Setup Environment Variables

download Ollama, and pull a suitable model according to your work load!!

import that model in your code, smaller model = Faster responce.

⚠️ Never push `.env` to GitHub.

---

# ▶️ Run the Server

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will run at:

```
http://127.0.0.1:8000
```

---

# 📌 Example API Query

```
POST /ask
```

Request body:

```json
{
  "question": "Explain the optimal riding system project."
}
```

---

# 🌟 Future Improvements

* Multi-document support
* Source citation in answers
* UI interface
* Deployment support

---

# 👨‍💻 Author

Developed with ❤️ by **Lens_Craft_PDF**

---

⭐ If you like this project, consider **starring the repository**!

