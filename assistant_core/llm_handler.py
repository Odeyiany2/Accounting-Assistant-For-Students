#retreiver and embedding functions implementation


#libraries 
import os
from dotenv import load_dotenv
from groq import Groq #language model wrapper for Groq API
from langchain_community.document_loaders import DirectoryLoader #langchain wrapper for loading documents from a directory
from langchain.text_splitter import RecursiveCharacterTextSplitter #langchain wrapper for splitting text into smaller chunks
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma 
from langchain_core.prompts import ChatPromptTemplate