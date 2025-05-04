#libraries to set up embedding model and vector store
import os 
import pinecone
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
