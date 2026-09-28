import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


load_dotenv()

DB_DIR = "./chroma_db"

# 1. Embedding model
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 2. Clear old data from the existing store (no folder deletion needed)
if os.path.exists(DB_DIR):
    old_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    old_store.delete_collection()

# 3. Load the menu file
with open("data/menu.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# 4. One chunk per dish (split on blank lines)
dish_blocks = [block.strip() for block in raw_text.split("\n\n") if block.strip()]
chunks = [Document(page_content=block) for block in dish_blocks]

print(f"Split menu into {len(chunks)} chunks")
print("Example chunk:\n", chunks[0].page_content)

# 5. Store in ChromaDB
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB_DIR
)

print("Ingestion complete. Vector store saved to", DB_DIR)