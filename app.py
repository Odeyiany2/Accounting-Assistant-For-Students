#fastapi implementation

import uvicorn 
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
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