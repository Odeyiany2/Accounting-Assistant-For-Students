#fastapi implementation
import uvicorn 
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from config.logging import fastapi_app_logger
from assistant_core.retriever_prompt import ask_assistant
import os

#creating the fastapi instance
app = FastAPI(title="AI-Powered Assistant for Accounting Students",
             description="An AI-powered assistant to help accounting students with their queries.",
             version="1.0.0")

#allowing CORS for all origins
app.add_middleware(
    CORSMiddleware, 
    allow_origins = ["*"],
    allow_credentials = True, 
    allow_methods = ["*"], 
    allow_headers = ["*"]
)



#getting the health status of the API 
@app.get("/health")
async def health_check():
    """
    Health check point to verify if the API is running smoothly
    """
    return JSONResponse(
        content={"status": "ok", "message": "Welcome to the AI Assistant API 🚀"}, 
        status_code=200)


@app.post("/query")
async def query_chatbot(request:Request):
    """
    Endpoint to handle user queries and return responses from the AI assistant.
    """
    try:
        data = await request.json()
        query = data.get("query")

        if not query:
            fastapi_app_logger.error("Query parameter is missing")
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        #calling the assistant function to get the response 
        response = ask_assistant(query)
        fastapi_app_logger.info(f"Received response from the assistant: {response}")
        
        if not response:
            fastapi_app_logger.error("No response from the assistant")
            raise HTTPException(status_code=500, detail="No response from the assistant")
        
        #returning the response as plain text
        return PlainTextResponse(content=response, status_code=200)
        
    except HTTPException as http_exc:
        fastapi_app_logger.error(f"HTTP Exception: {http_exc.detail}")
        raise http_exc




if __name__ == "__main__":
    load_dotenv()
    print("Starting AI-Powered Assistant for Accounting Students API")
    uvicorn.run("app:app", host = "0.0.0", port = 5000, reload = True)
