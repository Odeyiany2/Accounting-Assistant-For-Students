#fastapi implementation
import uvicorn 
import uuid
from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from typing import List
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from config.logging import fastapi_app_logger
from assistant_core.retriever_prompt import ask_assistant
from assistant_core.doc_handler import load_documents_from_upload
import os

#creating the fastapi instance
app = FastAPI(title="AI-Powered Assistant for Accounting Students",
             description="An AI-powered assistant to assist accounting students with Financial Accounting",
             version="1.0.0")

#allowing CORS for all origins
app.add_middleware(
    CORSMiddleware, 
    allow_origins = ["*"],
    allow_credentials = True, 
    allow_methods = ["*"], 
    allow_headers = ["*"]
)

user_uploaded_docs = {}

#getting the health status of the API 
@app.get("/health")
async def health_check():
    """
    Health check point to verify if the API is running smoothly
    """
    return JSONResponse(
        content={"status": "ok", "message": "Welcome to the AI Assistant API 🚀"}, 
        status_code=200)

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Endpoint to handle document uploads from users.
    """
    # Placeholder implementation
    try:
        #parse uploaded files from the request 
        docs = load_documents_from_upload(files)

        if not docs:
            fastapi_app_logger.error("No valid documents were uploaded.")
            raise HTTPException(status_code=400, detail="No valid documents were uploaded.")
        session_id = str(uuid.uuid4())
        user_uploaded_docs[session_id] = docs
        fastapi_app_logger.info(f"Successfully processed {len(docs)} documents from upload.")

        return JSONResponse(
            content = {
                "status": "success", 
                "message": f"Successfully uploaded and processed {len(docs)} documents.",
                "session_id": session_id
            },
            status_code=200
        )
    except Exception as e:
        fastapi_app_logger.error(f"Error processing uploaded documents: {e}")
        raise HTTPException(status_code=500, detail="Error processing uploaded documents.")



@app.post("/query")
async def query_chatbot(request:Request):
    """
    Endpoint to handle user queries and return responses from the AI assistant.
    """
    try:
        data = await request.json()
        query = data.get("query")
        session_id = data.get("session_id")
        course = data.get("course")  #optional course filter
        chat_history = data.get("history", [])  #optional chat history

        if not query:
            fastapi_app_logger.error("Query parameter is missing")
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        #retrieving user-uploaded documents for the session if available
        uploaded_docs = user_uploaded_docs.get(session_id, []) if session_id else []

        #calling the assistant function to get the response 
        response = ask_assistant(
            question=query, 
            course=course, 
            chat_history=chat_history,
            uploaded_docs=uploaded_docs
        )
        fastapi_app_logger.info(f"Received response from the assistant: {response}")
        
        if not response:
            fastapi_app_logger.error("No response from the assistant")
            raise HTTPException(status_code=500, detail="No response from the assistant")
        
        #returning the response as plain text
        return PlainTextResponse(content=response, status_code=200)
        
    except HTTPException as http_exc:
        fastapi_app_logger.error(f"HTTP Exception: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        fastapi_app_logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Error processing query")




if __name__ == "__main__":
    load_dotenv()
    print("Starting AI-Powered Assistant for Accounting Students API")
    uvicorn.run("app:app", host = "0.0.0", port = 5000, reload = True)
