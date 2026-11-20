"""Free local embeddings (Groq has no embeddings API).

Uses Chroma's built-in ONNX MiniLM model: no API key, no torch needed.
The model (~80 MB) downloads automatically on first use.
"""
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_core.embeddings import Embeddings


class LocalEmbeddings(Embeddings):
    def __init__(self):
        self._fn = DefaultEmbeddingFunction()

    def embed_documents(self, texts):
        return [[float(x) for x in vec] for vec in self._fn(list(texts))]

    def embed_query(self, text):
        return self.embed_documents([text])[0]