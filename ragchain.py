import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_chroma import Chroma

from Embeddings import LocalEmbeddings

load_dotenv(override=True)

DB_DIR = "./chroma_db"
# Free-tier friendly options: "llama-3.3-70b-versatile" (smarter),
# "llama-3.1-8b-instant" (faster, higher limits)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

embeddings = LocalEmbeddings()
vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
# k=12 so list-style questions ("all veg starters") see enough dishes
retriever = vectorstore.as_retriever(search_kwargs={"k": 12})

llm = ChatGroq(model=GROQ_MODEL, temperature=0)  # reads GROQ_API_KEY from .env

PROMPT = """You are a friendly, concise restaurant assistant.
Answer the customer's question using ONLY the menu items below.
Prices are in rupees (₹). If the answer is not in the menu, say
"Sorry, I don't see that on our menu."
When listing dishes, include the price. Use short bullet points for lists.
For allergen/diet questions, rely strictly on the Description text and
mention that guests with severe allergies should confirm with staff.

Recent conversation (for follow-up questions):
{history}

Menu items:
{context}

Question: {question}

Answer:"""


def ask(question: str, history: list[dict] | None = None) -> str:
    history = history or []
    recent = history[-4:]

    # Include the previous user question in retrieval so follow-ups
    # like "and the vegan ones?" still find the right dishes.
    prev_user = next((m["content"] for m in reversed(recent) if m["role"] == "user"), "")
    docs = retriever.invoke(f"{prev_user} {question}".strip())
    context = "\n\n".join(d.page_content for d in docs)

    hist_text = "\n".join(
        f"{m['role'].capitalize()}: {m['content'][:300]}" for m in recent
    ) or "(none)"

    prompt = PROMPT.format(context=context, question=question, history=hist_text)
    response = llm.invoke(prompt)
    return response.content if isinstance(response.content, str) else str(response.content)


if __name__ == "__main__":
    while True:
        q = input("\nAsk about the menu (or type 'exit'): ")
        if q.lower() == "exit":
            break
        print("\n", ask(q))