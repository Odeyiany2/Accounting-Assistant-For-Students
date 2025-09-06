#libraries to set up embedding model and vector store
import os 
import pinecone
from pinecone import Pinecone, ServerlessSpec
import torch #library for GPU support
from typing import List 
from langchain.docstore.document import Document #langchain wrapper for document object
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter #langchain wrapper for splitting text into smaller chunks
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from assistant_core.doc_handler import load_documents_from_directory, load_documents_from_upload
from config.logging import embedding_vec_logger




load_dotenv() #load environment variables from .env file

#set up the Pinecone API key and environment
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    embedding_vec_logger.error("PINECONE_API_KEY environment variable not set.")
    raise ValueError("PINECONE_API_KEY environment variable not set.")

#initialize pinecone 
pc = Pinecone(api_key = os.getenv("PINECONE_API_KEY"))

#create index name and check for index existence
index_name = "accounting-assistant"

if index_name not in pc.list_indexes().names():
    embedding_vec_logger.info(f"Creating index {index_name}...")
    pc.create_index(index_name, 
                          dimension=1536, 
                          metric="cosine",
                          vector_type= "dense",
                          spec=ServerlessSpec(
                              cloud= "aws",
                              region ="us-east-1"
                          ))
else:
    embedding_vec_logger.info(f"Index {index_name} already exists.")


#function for chunking 
def chunk_docs(docs: List[Document], chunk_size: int = 800, chunk_overlap: int = 150) -> List[Document]:
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
                                     namespace = "financial_accounting")



#temporary storage for user uploaded documents
def build_temp_doc_store(uploaded_docs: List[Document]) -> Pinecone:
    """
    Build a temporary in-memory Chroma vector store for user-uploaded documents.
    This avoids polluting the main Pinecone index with temporary data.

    Args:
        uploaded_docs (List[Document]): List of user-uploaded documents.
    
    Returns:
        Pinecone: Pinecone vector store containing embeddings of the uploaded documents.
    """
    try:
        if not uploaded_docs:
            embedding_vec_logger.warning("No uploaded documents provided to build temporary doc store.")
            return None
        
        chunked_uploaded_docs = chunk_docs(uploaded_docs)
        # Build temporary in-memory Chroma store
        temp_doc_store = Chroma.from_documents(
            documents=chunked_uploaded_docs,
            embedding=embedding_model,
            collection_name="user_uploads",
            persist_directory=None  # In-memory, won't persist after session ends
        )
        embedding_vec_logger.info(f"Built temporary document store with {len(chunked_uploaded_docs)} chunks from uploaded documents.")
        return temp_doc_store
    except Exception as e:
        embedding_vec_logger.error(f"Error building temporary document store: {e}")
        raise e