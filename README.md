# 🍽️ Menu Q&A Bot

An AI assistant that answers customer questions about a restaurant menu: veg options, spice level, prices, and allergens. It uses Retrieval-Augmented Generation (RAG), so answers come only from the real menu. It includes secure user accounts and a saved search history for each user.

**Live demo:** https://menu-qa-bot.onrender.com/
**Demo video:**  https://drive.google.com/file/d/1sGAmahA76erg4jgI8X7qUp5uepGWiYTr/view?usp=sharing

## ✨ Features

- Ask questions in plain English, e.g. "vegan options", "hot and spicy dishes", "gluten-free mains", "dishes under ₹100"
- Answers use only menu items, with no made-up dishes. If an item isn't on the menu, the bot says so.
- User registration and login with securely hashed passwords
- Per-user history of previous searches: view, delete one, or clear all
- Last conversation restored on login; follow-up questions supported
- Suggested-question buttons and a clean, responsive UI
- Friendly error messages for API or rate-limit problems

## 🏗️ Architecture

```
User (browser)
      │
      ▼
Streamlit UI (app.py): login/register, chat, sidebar history
      │                         │
      │                         ▼
      │               SQLite (app.db): users + searches
      ▼
RAG chain (ragchain.py)
  1. Question → local embedding model (MiniLM)
  2. Search ChromaDB for the most relevant dishes
  3. Menu items + question + recent chat → prompt
  4. Groq LLM answers from the menu only

ingest.py (one-time): data/menu.txt → one chunk per dish → embeddings → ChromaDB
```

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI | Python, Streamlit |
| LLM | Groq API |
| Retrieval | LangChain, ChromaDB |
| Embeddings | Local ONNX MiniLM (free, no API key) |
| Auth & history | SQLite, PBKDF2-SHA256 salted hashing |

## 👥 Users & Access

- **Guest:** can only see the Login/Register page.
- **Registered user:** can ask menu questions and manage their own search history. Users can never see each other's data.
- **No admin role:** the menu is updated by editing `data/menu.txt` and re-running `ingest.py`.

## 📁 Project Structure

```
├── app.py            # Streamlit UI, auth screens, history sidebar
├── ragchain.py       # Retrieval + Groq answer generation
├── ingest.py         # Builds the ChromaDB vector store from the menu
├── db.py             # Users and search-history database (SQLite)
├── embeddings.py     # Local embedding wrapper
├── data/menu.txt     # Menu data (one dish per block)
├── requirements.txt
└── .env.example
```

## 🚀 Run Locally

1. Clone and enter the project
   ```bash
   git clone https://github.com/gyanasreeja/menu-qa-bot.git
   cd menu-qa-bot
   ```
2. Create a virtual environment (Python 3.12 recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Add your free Groq API key from [console.groq.com/keys](https://console.groq.com/keys). Create a `.env` file:
   ```
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=openai/gpt-oss-20b
   ```
5. Build the menu database (once, and again after editing the menu)
   ```bash
   python ingest.py
   ```
6. Start the app
   ```bash
   python -m streamlit run app.py
   ```
   Open http://localhost:8501, register an account, and start asking questions.
   <img width="1493" height="723" alt="Screenshot 2026-11-20 190146" src="https://github.com/user-attachments/assets/e25bdead-6073-4d4a-aff4-ce02a37d9900" />
   <img width="865" height="686" alt="Screenshot 2026-11-20 190158" src="https://github.com/user-attachments/assets/95f9636a-2ce5-4c88-800c-ed6d1ddd48b2" />
   <img width="1919" height="985" alt="Screenshot 2026-11-20 184944" src="https://github.com/user-attachments/assets/8200dacf-c92e-4791-ad1b-ef51f6d724c2" />


