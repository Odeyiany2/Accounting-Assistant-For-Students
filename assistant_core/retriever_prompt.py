#implementation for retrieving, conversation awareness and also for prompt engineering
import os
from tavily import TavilyClient
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from dotenv import load_dotenv
from groq import Groq #language model wrapper for Groq API
from config.logging import retriever_prompt_logger
from embedding_vec import doc_store, build_temp_doc_store



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
You are an expert **Financial Accounting tutor**. 
Your job is to help students understand topics by providing step-by-step, clear, and correct explanations.

Rules:
- Answer **only Financial Accounting questions** (ignore Finance, Managerial, Business).
- Use IFRS or IAS standards where applicable. Mention the specific standard if relevant.
- If asked to prepare accounts, use **vertical format**.
- If the answer is not in your knowledge base, apologize and search the web using reliable sources 
  (IFRS.org, IASB, ACCA, ICAN, Investopedia, academic references). Provide the source link.
- If you are not sure, clearly say so instead of guessing.

---

**Question**:
{input}

**Documents**:
{context}

---

## Reason:
<step-by-step reasoning>

## Answer:
<final, clear explanation or prepared statement>
""")

#Web search fallback function 
def search_web(query:str, num_results: int = 3):
    try:
        results = tavily_client.search(query, max_results=num_results)
        sources = [result["content"] for result in results["results"]]
        urls = [result["url"] for result in results["results"]]
        retriever_prompt_logger.info(f"Web search results for query '{query}': {urls}")
        combined_content = "\n\n".join(sources)
        return combined_content, urls
    except Exception as e:
        retriever_prompt_logger.error(f"Error occurred during web search: {e}")
        return "I encountered an error while searching the web. Please try again later.", []



#main function to handle the retrieval and response generation
def ask_assistant(question:str, course:str = None, chat_history:list = [], uploaded_docs: list = []):
    try:
        #setup retriever with course filter
        if course:
            base_retriever = doc_store.as_retriever(
                search_kwargs={"filter": {"subject": course}},
                search_type="similarity",
                k=5  #retrieve top 5 relevant documents
            )
        else:
            base_retriever = doc_store.as_retriever(k=5)  #retrieve top 5 relevant documents without course filter
        retriever_prompt_logger.info(f"Retrieving documents for question: {question} with course: {course}")
        
        #list of retrievers to combine
        retrievers = [base_retriever]

        #add temporary user-uploaded document retriever if available
        temp_doc_store = build_temp_doc_store(uploaded_docs) 
        if temp_doc_store:
            retrievers.append(temp_doc_store.as_retriever(k = 5))

        #combine retrievers using EnsembleRetriever
        combine_retriever = EnsembleRetriever(retrievers=retrievers, weights=[1]*len(retrievers))
        
        
        #wrap the retriever with history awareness
        try:
            history_aware_retriever = create_history_aware_retriever(
                retriever=combine_retriever,
                history_length=5,  #number of previous interactions to consider
                llm=model,  #use the Groq model for retrieval
                prompt=ChatPromptTemplate.from_template(
                    "You are an expert accounting tutor. "
                    "Answer the question based on the provided context: {context} "
                    "Question: {input}"
                )
            )
            retriever_prompt_logger.info("History-aware retriever created successfully.")
        except Exception as e:
            retriever_prompt_logger.error(f"Error creating history-aware retriever: {e}")
            return "Sorry, an error occurred while setting up the retriever."

        #retrieve relevant documents
        retrieved_docs = history_aware_retriever.invoke(
            {"input": question, "history": chat_history}
        )
        retriever_prompt_logger.info(f"Retrieved {len(retrieved_docs)} documents for question: {question}")

        if not retrieved_docs:
            retriever_prompt_logger.warning("No relevant documents found. Searching the web for answers.")
            try:
                web_content, web_urls = search_web(question)
                web_prompt = ChatPromptTemplate.from_template("""
    You are an expert accounting tutor. A student has asked a question that is not covered by the course materials.
    Use only reliable accounting sources (IFRS, IASB, ACCA, ICAN, Investopedia, major textbooks). Always provide the source link in your answer.

    Question: {input}
    **Web Results**:
    {context}

    ## Answer:
    """)
                answer = model.invoke(
                    web_prompt.format(input=question, context=web_content)
                ).content
                retriever_prompt_logger.info(f"Web search answer: {answer}")
                return answer + f"\nSources: {', '.join(web_urls)}"
            except Exception as e:
                retriever_prompt_logger.error(f"Error during web search: {e}")
                return "Sorry, I couldn't find any relevant information online. Please try again later."
            
        #create document chain for retrieval
        try:
            retriever_prompt_logger.info("Creating document chain for retrieval.")
            document_chain = create_stuff_documents_chain(
                llm=model,
                prompt=RAFT_prompt,
                document_variable_name="context",
                return_source_documents=True
            )
            retriever_prompt_logger.info("Document chain created successfully.")
        except Exception as e:
            retriever_prompt_logger.error(f"Error creating document chain: {e}")
            return "Sorry, an error occurred while setting up the document chain."

        #create the FINAL retrieval chain
        try:
            retriever_prompt_logger.info("Creating retrieval chain.")
            retrieval_chain = create_retrieval_chain(
                retriever=history_aware_retriever,
                document_chain=document_chain,
                return_source_documents=True
            )

            retriever_prompt_logger.info("Retrieval chain created successfully.")
        except Exception as e:
            retriever_prompt_logger.error(f"Error creating retrieval chain: {e}")
            return "Sorry, an error occurred while setting up the retrieval chain." 
        
        #invoke the retrieval chain with the question and chat history
        try:
            response = retrieval_chain.invoke(
                {"input": question, "history": chat_history}
            )
            return response["answer"]
        except Exception as e:
            retriever_prompt_logger.error(f"Error invoking final retrieval chain for a response: {e}")
            return "Sorry, an error occurred while generating a response."
    except Exception as e:
        retriever_prompt_logger.error(f"Error in ask_assistant: {e}")
        return "Sorry, an error occurred while processing your request."