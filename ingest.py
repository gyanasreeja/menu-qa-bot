import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_chroma import Chroma

from Embeddings import LocalEmbeddings

load_dotenv()

DB_DIR = "./chroma_db"
embeddings = LocalEmbeddings()

# Clear old data
if os.path.exists(DB_DIR):
    old_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    old_store.delete_collection()

# Load the menu file
with open("data/menu.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# One chunk per dish (split on blank lines)
dish_blocks = [b.strip() for b in raw_text.split("\n\n") if b.strip()]
chunks = []
for block in dish_blocks:
    first_line = block.splitlines()[0]
    name = first_line.replace("Dish:", "").strip()
    chunks.append(Document(page_content=block, metadata={"dish": name}))

print(f"Split menu into {len(chunks)} chunks")
print("Example chunk:\n", chunks[0].page_content)

Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB_DIR,
)
print("Ingestion complete. Vector store saved to", DB_DIR)