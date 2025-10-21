import os 
import tempfile
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, Docx2txtLoader
from langchain.docstore.document import Document
from typing import List
from pathlib import Path
from config.logging import doc_handler_logger

#load the environment variables
load_dotenv()

# Set up the Azure Document Intelligence API key and endpoint
key = os.getenv("AZURE_DOCUMENT_API_KEY")
endpoint = os.getenv("AZURE_DOCUMENT_ENDPOINT")
if not key or not endpoint:
    raise ValueError("AZURE_DOCUMENT_API_KEY and AZURE_DOCUMENT_ENDPOINT environment variables must be set.")

#initialize the Azure Document Intelligence client
client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

#function to analyze documents in the knowledge base using Azure Document Intelligence
def extract_text_with_azure(file_path:str):
    """
    Analyzes a document using Azure Document Intelligence and returns the analysis result.

    Args:
        file_path (str): The path to the document file.
    
    Returns:
        The analysis result from Azure Document Intelligence.
    """
    try:
        with open(file_path, "rb") as f:
            poller = client.begin_analyze_document("prebuilt-layout", f)
        result = poller.result()

        text_block = []
        for result in result.pages:
            doc_handler_logger.info(f"Page {result.page_number} has width {result.width} and height {result.height}, measured in {result.unit}.")
            for line in result.lines:
                #doc_handler_logger.info(f"Line: '{line.content}'")
                text_block.append(line.content)
        
        full_text = "\n".join(text_block)
        doc_handler_logger.info(f"Extracted text from document {file_path} using Azure Document Intelligence.")
        return full_text
    
    except Exception as e:
        doc_handler_logger.error(f"Error analyzing document {file_path} with Azure Document Intelligence: {e}")
        return None
    
def is_scanned_pdf_with_fallback(file_path:str) -> bool:
    """
    Checks if a PDF file is scanned by attempting to extract text using Azure Document Intelligence.
    If no text is extracted, it is considered a scanned PDF.

    Args:
        file_path (str): The path to the PDF file.
    Returns:
         True if the PDF is scanned, otherwise False
    """
    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        content = "".join([doc.page_content for doc in docs])
        return len(content.strip()) == 0
    except Exception as e:
        return True
    
#set up a function to load the documents from a directory
def load_documents_from_directory(directory_path:str) -> List[Document]:
    """
    Hybrid document loader that uses Azure DI for scanned PDFs and LangChain loaders for others.
    """
    supported_extensions = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"]

    if not os.path.exists(directory_path):
        doc_handler_logger.error(f"Directory does not exist: {directory_path}")
        return []
    
    all_documents = []
    for subdir, _, files in os.walk(directory_path):
        subject = Path(subdir).name
        for file in files:
            file_path = os.path.join(subdir, file)
            ext = os.path.splitext(file)[1].lower()

            try:
                if ext == ".pdf":
                    if is_scanned_pdf_with_fallback(file_path):
                        text = extract_text_with_azure(file_path)
                        if text:
                            all_documents.append(
                                Document(page_content=text, metadata={"source": file_path, "subject": subject})
                            )
                    else:
                        loader = PyMuPDFLoader(file_path=file_path)
                        docs = loader.load()
                        for d in docs:
                            d.metadata["subject"] = subject
                        all_documents.extend(docs)

                elif ext == ".docx":
                    loader = Docx2txtLoader(file_path=file_path)
                    docs = loader.load()
                    for d in docs:
                        d.metadata["subject"] = subject
                    all_documents.extend(docs)

                elif ext == ".txt":
                    loader = TextLoader(file_path=file_path, encoding="utf-8")
                    docs = loader.load()
                    for d in docs:
                        d.metadata["subject"] = subject
                    all_documents.extend(docs)

                elif ext in [".png", ".jpg", ".jpeg"]:
                    text = extract_text_with_azure(file_path)
                    if text:
                        all_documents.append(
                            Document(page_content=text, metadata={"source": file_path, "subject": subject})
                        )
                else:
                    doc_handler_logger.warning(f"Unsupported file type: {ext} for {file_path}")
            except Exception as e:
                doc_handler_logger.error(f"Error processing file {file_path}: {e}")
                continue

    return all_documents


def load_documents_from_upload(uploaded_files) -> List[Document]:
    """
    Load uploaded documents from users (students) with Azure DI support.
    """
    all_docs_user = []

    for file in uploaded_files:
        suffix = os.path.splitext(file.filename)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(file.file.read() if hasattr(file, "file") else file.read())
            temp_path = temp_file.name

        try:
            if suffix in [".pdf", ".png", ".jpg", ".jpeg"]:
                text = extract_text_with_azure(temp_path)
                if text:
                    all_docs_user.append(Document(
                        page_content=text,
                        metadata={"source": file.filename, "subject": "user_upload"}
                    ))
            elif suffix == ".docx":
                loader = Docx2txtLoader(file_path=temp_path)
                docs = loader.load()
                for d in docs:
                    d.metadata["subject"] = "user_upload"
                all_docs_user.extend(docs)
            elif suffix == ".txt":
                loader = TextLoader(file_path=temp_path, encoding="utf-8")
                docs = loader.load()
                for d in docs:
                    d.metadata["subject"] = "user_upload"
                all_docs_user.extend(docs)
            else:
                doc_handler_logger.warning(f"Unsupported file type: {suffix} for {file.filename}")
        finally:
            os.remove(temp_path)

    return all_docs_user


