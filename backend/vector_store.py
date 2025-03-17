import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def create_vectorstore(documents):
    """
    Create or update a vector store from the given documents using Hugging Face embeddings.
    :param documents: List of documents to embed and store.
    :return: FAISS vector store.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    os.makedirs("data/faiss_index", exist_ok=True)  # Ensure the directory exists
    if os.path.exists("data/faiss_index/index.faiss"):
        # Load existing vector store and add new documents
        vectorstore = FAISS.load_local("data/faiss_index", embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(documents)
    else:
        # Create a new vector store
        vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local("data/faiss_index")
    return vectorstore

def load_vectorstore():
    """
    Load the pre-existing FAISS vector store using Hugging Face embeddings.
    :return: Loaded FAISS vector store.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    os.makedirs("data/faiss_index", exist_ok=True)  # Ensure the directory exists
    if os.path.exists("data/faiss_index/index.faiss"):
        return FAISS.load_local("data/faiss_index", embeddings, allow_dangerous_deserialization=True)
    else:
        raise FileNotFoundError("FAISS vector store not found. Please upload and process documents first.")

def clear_vectorstore():
    """
    Clear the existing vector store by deleting the directory.
    """
    if os.path.exists("data/faiss_index"):
        import shutil
        shutil.rmtree("data/faiss_index")  # Delete the vector store directory