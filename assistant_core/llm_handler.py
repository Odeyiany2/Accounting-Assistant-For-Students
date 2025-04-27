#retreiver and embedding functions implementation


#libraries 
import os
import pytesseract
from typing import List
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
from pdf2image import convert_from_path
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
    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        content = "".join([doc.page_content for doc in docs])
        return len(content) == 0
    except Exception as e:
        llm_handler_logger.error(f"""Error loading PDF file - the document contains scanend images {file_path}, 
                                 Error: {e}""")
        return True
    

# Set up the OCR function to extract text from scanned images in a PDF file
def extract_text_from_scanned_pdf(file_path):
    """
    Extracts text from a scanned PDF file using OCR.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the scanned PDF.
    """
    try:
        # Use PyMuPDF to extract images from the PDF
        docs = convert_from_path(file_path, dpi=300)
        
        # Extract text from each page using OCR
        text = ""
        for i, image in enumerate(docs):
            page_text = pytesseract.image_to_string(image, lang="eng")
            text += page_text + "\n"
        llm_handler_logger.info(f"Extracted text from scanned PDF {file_path}")
        return text
    
    except Exception as e:
        llm_handler_logger.error(f"""Error extracting text from scanned PDF {file_path}, 
                                 Error: {e}""")
        return None


#set up a function to load the documents from a directory 
def load_documents_from_directory(directory_path:str) -> List[Document]:
    """
    Load documents from a specified directory using PyMuPDFLoader.
    
    Args:
        directory_path (str): The path to the directory containing the documents.
        
    Returns:
        list: A list of loaded documents.
    """

    supported_extensions = ['.pdf', '.docx', '.txt']


    # Check if the directory exists
    if not os.path.exists(directory_path):
        llm_handler_logger.error(f"Directory {directory_path} does not exist.")
        return []
    
    all_documents = []
    # Iterate through all files in the directory
    
    loader = DirectoryLoader(directory_path, glob="**/*.pdf", loader_cls=PyMuPDFLoader)
    documents = loader.load()
    return documents