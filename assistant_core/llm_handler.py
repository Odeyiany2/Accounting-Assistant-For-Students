#retreiver and embedding functions implementation


#libraries 
import os
import pytesseract
from dotenv import load_dotenv
from groq import Groq #language model wrapper for Groq API
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader, Docx2txtLoader#langchain wrapper for loading documents from a directory
from langchain.text_splitter import RecursiveCharacterTextSplitter #langchain wrapper for splitting text into smaller chunks
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma 
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.docstore.document import Document
from assistant_core.logging import llm_handler_logger

load_dotenv() #load environment variables from .env file

# Set up the Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set.")


# Set up the Groq API client
model = Groq(
    api_key = groq_api_key,
    model = "deepseek-r1-distill-llama-70b",
    temperature = 0.5
)


#check if a pdf contains scanned images 
def is_scanned_pdf(file_path):
    """
    Checks if a PDF file contains scanned images

    Args:
        file_path (str): The path to the PDF file.
    
    Returns:
         True if the PDF contains scanned images, otherwise False
    """

    
#set up a function to load the documents from a directory 
def load_documents_from_directory(directory_path):
    """
    Load documents from a specified directory using PyMuPDFLoader.
    
    Args:
        directory_path (str): The path to the directory containing the documents.
        
    Returns:
        list: A list of loaded documents.
    """
    loader = DirectoryLoader(directory_path, glob="**/*.pdf", loader_cls=PyMuPDFLoader)
    documents = loader.load()
    return documents