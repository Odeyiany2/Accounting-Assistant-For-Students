import os 
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest

#load the environment variables
load_dotenv()

# Set up the Azure Document Intelligence API key and endpoint
azure_document_api_key = os.getenv("AZURE_DOCUMENT_API_KEY")
azure_document_endpoint = os.getenv("AZURE_DOCUMENT_ENDPOINT")
