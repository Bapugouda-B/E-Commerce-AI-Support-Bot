from langchain_community.vectorstores import FAISS
from data.knowledge_base import load_documents
from rag.embeddings import load_embeddings

def load_vectorstore():
    documents = load_documents()
    embeddings = load_embeddings()

    return FAISS.from_texts(
        texts=documents,
        embedding=embeddings
    )
