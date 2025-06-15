#fastapi implementation
import uvicorn 
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from config.logging import fastapi_app_logger
from assistant_core.retriever_prompt import ask_assistant
import os

app = FastAPI()


#getting the health status of the API 
@app.get("/health")
async def health_check():
    """
    Health check point to verify if the API is running smoothly
    """
    return JSONResponse(content={"status": "ok", "message": "Welcome to the AI-Powered Assistant for Accounting Students"}, status_code=200)


@app.post("/query")
async def query_chatbot():
    pass
