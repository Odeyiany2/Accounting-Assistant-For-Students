#libraries to set up embedding model and vector store
import os 
import pinecone
from pinecone import Pinecone
import torch #library for GPU support
from typing import List 
from langchain.docstore.document import Document #langchain wrapper for document object
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter #langchain wrapper for splitting text into smaller chunks
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma, Pinecone
from assistant_core.doc_handler import load_documents_from_directory
from config.logging import embedding_vec_logger




load_dotenv() #load environment variables from .env file

#set up the Pinecone API key and environment
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    embedding_vec_logger.error("PINECONE_API_KEY environment variable not set.")
    raise ValueError("PINECONE_API_KEY environment variable not set.")

#initialize pinecone 
pinecone.init(api_key = pinecone_api_key)

#create index name and check for index existence
index_name = "accounting-assistant"

if index_name not in pinecone.list_indexes().names():
    embedding_vec_logger.info(f"Creating index {index_name}...")
    pinecone.create_index(index_name, 
                          dimension=768, 
                          metric="cosine")
else:
    embedding_vec_logger.info(f"Index {index_name} already exists.")


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
    try:
        if not docs:
            print("No documents to chunk")
            embedding_vec_logger.error("No documents to chunk.")
            return []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        documents = text_splitter.split_documents(docs)
        embedding_vec_logger.info(f"Chunked {len(docs)} documents into {len(documents)} chunks.")
        return documents
    except Exception as e:
        embedding_vec_logger.error(f"Error in chunking documents: {e}")
        raise e

#embedding model 
embedding_model = HuggingFaceBgeEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs = {
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "max_length": 512,
        "batch_size": 32
    }
)

#getting the data extracted from the document handler module 
course_dir = {
    "financial_accounting": "C:\Projects_ML\Accounting-Assistant-For-Students\data\financial_accounting",
    # "finance": "C:\Projects_ML\Accounting-Assistant-For-Students\data\finance",
    # "business": "C:\Projects_ML\Accounting-Assistant-For-Students\data\business",
    # "managerial_accounting": "C:\Projects_ML\Accounting-Assistant-For-Students\data\managerial_accounting"
}
all_docs = []
for course, path in course_dir.items():
    docs = load_documents_from_directory(path)
    for doc in docs:
        doc.metadata["course"] = course
    all_docs.extend(docs)

#chunk the documents into smaller pieces
chunked_docs = chunk_docs(all_docs)


#push to pinecone index
doc_store  = Pinecone.from_documents(chunked_docs, 
                                     embedding_model, 
                                     index_name = index_name,
                                     namespace = "accounting-assistant")


