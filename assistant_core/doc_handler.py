#retreiver and embedding functions implementation


#libraries 
import os
import pytesseract
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq #language model wrapper for Groq API
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, Docx2txtLoader#langchain wrapper for loading documents from a directory
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.docstore.document import Document
from pdf2image import convert_from_path
from config.logging import doc_handler_logger

load_dotenv() #load environment variables from .env file

# Set up the Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    doc_handler_logger.error("GROQ_API_KEY environment variable not set.")
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
        doc_handler_logger.error(f"""Error loading PDF file - the document contains scanend images {file_path}, 
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
        doc_handler_logger.info(f"Extracted text from scanned PDF {file_path}")
        return text
    
    except Exception as e:
        doc_handler_logger.error(f"""Error extracting text from scanned PDF {file_path}, 
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
        doc_handler_logger.error(f"Directory {directory_path} does not exist.")
        return []
    
    all_documents = []
    # Iterate through all files in the directory
    for subdir, _, files in os.walk(directory_path):
        subject = Path(subdir).name
        for file in files:
            file_path = os.path.join(subdir, file)
            file_ext = os.path.splitext(file)[1].lower()

            #check if the file extension is supported 

            if file_ext == ".pdf":
                if is_scanned_pdf(file_path):
                    print(f"[OCR] Processing scanned PDF: {file}")
                    doc_handler_logger.info(f"[OCR] Processing scanned PDF: {file}")
                    # Extract text from scanned PDF using OCR
                    text = extract_text_from_scanned_pdf(file_path)
                    if text:
                        all_documents.append(Document(page_content = text,
                                                       metadata = {"source":file_path, "subject":subject}))

                else:
                    try:
                        print(f"[PDF] Processing PDF: {file}")
                        doc_handler_logger.info(f"[PDF] Processing PDF: {file}")
                        #load the pdf file using PyMuPDFLoader
                        loader = PyMuPDFLoader(file_path=file_path)
                        docs = loader.load()
                        for d in docs:
                            d.metadata["subject"] = subject
                            all_documents.extend(d)
                    except Exception as e:
                        doc_handler_logger.error(f"Error loading PDF file {file_path}, Error: {e}")
                        continue
            elif file_ext == ".docx":
                try:
                    print(f"[DOCX] Processing DOCX: {file}")
                    doc_handler_logger.info(f"[DOCX] Processing DOCX: {file}")
                    #load the docx file using Docx2txtLoader
                    loader = Docx2txtLoader(file_path=file_path)
                    docs = loader.load()
                    for d in docs:
                        d.metadata["subject"] = subject
                        all_documents.extend(d)
                except Exception as e:
                    doc_handler_logger.error(f"Error loading DOCX file {file_path}, Error: {e}")
                    continue
            elif file_ext == ".txt":
                print(f"[TXT] Processing TXT: {file}")
                doc_handler_logger.info(f"[TXT] Processing TXT: {file}")
                #load the txt file using 
                loader = TextLoader(file_path=file_path, encoding="utf-8")
                docs = loader.load()
                for d in docs:
                    d.metadata["subject"] = subject
                    all_documents.extend(d)
            else:
                doc_handler_logger.warning(f"Unsupported file type: {file_ext}. Skipping file: {file_path}")
                continue
    return all_documents

