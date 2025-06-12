#implementation for retrieving, conversation awareness and also for prompt engineering
import os
from tavily import TavilyClient
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from dotenv import load_dotenv
from groq import Groq #language model wrapper for Groq API
from config.logging import retriever_prompt_logger
from embedding_vec import doc_store



load_dotenv() #load environment variables from .env file

# Set up the Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    retriever_prompt_logger.error("GROQ_API_KEY environment variable not set.")
    raise ValueError("GROQ_API_KEY environment variable not set.")

#set up the Tavily API key 
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    retriever_prompt_logger.error("TAVILY_API_KEY environment variable not set.")
    raise ValueError("TAVILY_API_KEY environment variable not set.")

# Initialize the Tavily client for web search
tavily_client = TavilyClient(tavily_api_key)

# Set up the Groq API client
model = Groq(
    api_key = groq_api_key,
    model = "deepseek-r1-distill-llama-70b",
    temperature = 0.5
)


#RAFT Prompting 
RAFT_prompt = ChatPromptTemplate.from_template("""
You are an expert accounting tutor helping students with questions in the following courses: 
- Finance
- Business
- Financial Accounting
- Managerial Accounting                                              

A student has asked a question.

You have access to the following documents. Some are helpful, others may not be. Please:
1. Identify which document(s) are useful
2. Explain your reasoning step by step
3. Provide a detailed and accurate answer

If the question requires a financial statement, present it in a **vertical format**.

If the answer is not available in the knowledge base, apologize and let the student know that you will search 
the web to find an accurate answer and then provide the web search result with a link to the source.
If the question is not related to the courses listed above, politely inform the student 
that you can only assist with questions related to those courses.

---

**Question**:
{input}

**Documents**:
{context}

---

## Reason:
<explain your reasoning using only relevant content>

## Answer:
<final answer goes here>
""")

#Web search fallback function 
def search_web(query:str, num_results: int = 3):
    try:
        results = tavily_client.search(query, max_results=num_results)
        sources = [results["content"] for result in results["results"]]
        urls = [result["url"] for result in results["results"]]
        retriever_prompt_logger.info(f"Web search results for query '{query}': {urls}")
        combined_content = "\n\n".join(sources)
        return combined_content, urls
    except Exception as e:
        retriever_prompt_logger.error(f"Error occurred during web search: {e}")
        return "I encountered an error while searching the web. Please try again later.", []





#retrieval chain setup
retrieval = create_history_aware_retriever(
    retriever=doc_store.as_retriever(),  # Retrieve top 5 relevant documents based on the course and query
    history_length=5,  # Number of previous interactions to consider
    llm=model,  # Use the Groq model for retrieval
    prompt=ChatPromptTemplate.from_template(
        "You are an expert accounting tutor. "
        "Answer the question based on the provided context: {context} "
        "Question: {input}"
    )
)

#create a document chain for retrieval
document_chain = create_stuff_documents_chain(
    llm=model,
    prompt=RAFT_prompt,
    document_variable_name="context",
    return_source_documents=True
)

#create the retrieval chain
retrieval_chain = create_retrieval_chain(
    retriever=retrieval,
    document_chain=document_chain,
    return_source_documents=True
)