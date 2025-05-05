#libraries to set up embedding model and vector store
import os 
import pinecone
from typing import List 
from langchain.docstore.document import Document #langchain wrapper for document object
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter #langchain wrapper for splitting text into smaller chunks
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma, Pinecone
from config.logging import embedding_vec_logger


load_dotenv() #load environment variables from .env file

#set up the Pinecone API key and environment
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    embedding_vec_logger.error("PINECONE_API_KEY environment variable not set.")
    raise ValueError("PINECONE_API_KEY environment variable not set.")

#function for chunking 

def chunk_docs(docs: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    This function is used to chunk documents into smaller pieces for embedding. 
    It uses langchain's RecursiveCharacterTextSplitter to split the loaded documents into smaller chunks
    
    Args:
        docs (List[Document]): List of documents to be chunked.
        chunk_size (int): Size of each chunk.
        chunk_overlap (int): Overlap between chunks.

    Returns:
        List[Document]: List of chunked documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    documents = text_splitter.split_documents(docs)
    embedding_vec_logger.info(f"Chunked {len(docs)} documents into {len(documents)} chunks.")
    return documents

#embedding model 
embedding_model = HuggingFaceBgeEmbeddings()
