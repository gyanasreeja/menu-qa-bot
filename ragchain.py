from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma


load_dotenv()

DB_DIR = "./chroma_db"

# 1. Same embedding model as ingest.py (must match!)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 2. Load the saved vector store
vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# 3. LLM
llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0)

# 4. Prompt template
PROMPT = """You are a helpful restaurant assistant.
Answer the customer's question using ONLY the menu items below.
If the answer is not in the menu, say "Sorry, I don't see that on our menu."

Menu items:
{context}

Question: {question}

Answer:"""


def ask(question: str) -> str:
    # Retrieve top matching dishes
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    # Build prompt and call Gemini
    prompt = PROMPT.format(context=context, question=question)
    response = llm.invoke(prompt)

    # Newer Gemini models return a list of blocks, so extract only the text
    content = response.content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return content



if __name__ == "__main__":
    while True:
        q = input("\nAsk about the menu (or type 'exit'): ")
        if q.lower() == "exit":
            break
        print("\n", ask(q))