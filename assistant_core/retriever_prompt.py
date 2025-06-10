#implementation for retrieving, conversation awareness and also for prompt engineering
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from embedding_vec import embedding_model



#RAFT Prompting 
RAFT_prompt = ChatPromptTemplate.from_template("""
You are an expert accounting tutor helping students with questions in the following courses: 
- Finance
- Business
- Financial Accounting

A student has asked a question.

You have access to the following documents. Some are helpful, others may not be. Please:
1. Identify which document(s) are useful
2. Explain your reasoning step by step
3. Provide a detailed and accurate answer

If the question requires a financial statement, present it in a **vertical format**.

If the answer is not available in the knowledge base, apologize and let the student know that you will search 
the web to find an accurate answer.

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
def query_engine():
    pass