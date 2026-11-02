from functools import lru_cache
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings

@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_dir,
    )

def add_documents(documents):
    if documents:
        get_vectorstore().add_documents(documents)

def retrieve(question: str, k: int = 5):
    return get_vectorstore().similarity_search(question, k=k)
