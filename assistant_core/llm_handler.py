#retreiver and embedding functions implementation


#libraries 
import os
from dotenv import load_dotenv
from groq import Groq #language model wrapper for Groq API
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader#langchain wrapper for loading documents from a directory
from langchain.text_splitter import RecursiveCharacterTextSplitter #langchain wrapper for splitting text into smaller chunks
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma 
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from assistant_core.logging import llm_handler_logger

load_dotenv() #load environment variables from .env file

# Set up the Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set.")