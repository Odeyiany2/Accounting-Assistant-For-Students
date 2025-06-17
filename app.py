#fastapi implementation
import uvicorn 
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
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
    pass



if __name__ == "__main__":
    load_dotenv()
    print("Starting AI-Powered Assistant for Accounting Students API")
    uvicorn.run("app:app", host = "0.0.0", port = 5000, reload = True)
