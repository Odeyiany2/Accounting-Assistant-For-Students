#implementation for retrieving, conversation awareness and also for prompt engineering
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from embedding_vec import embedding_model
import os
from dotenv import load_dotenv
from groq import Groq #language model wrapper for Groq API
from config.logging import retriever_prompt_logger

load_dotenv() #load environment variables from .env file

# Set up the Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    retriever_prompt_logger.error("GROQ_API_KEY environment variable not set.")
    raise ValueError("GROQ_API_KEY environment variable not set.")

# Set up the Groq API client
model = Groq(
    api_key = groq_api_key,
    model = "deepseek-r1-distill-llama-70b",
    temperature = 0.5
)

#document chain 
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



#retrieval function plus prompting
def retrieve_and_prompt(question: str, documents: list[Document]) -> str:
    pass