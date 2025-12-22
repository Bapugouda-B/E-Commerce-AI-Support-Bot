from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL

def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )
