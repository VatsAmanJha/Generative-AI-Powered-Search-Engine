from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from ai_search_engine import generate_content

# Initialize FastAPI
app = FastAPI()

# Define CORS settings
origins = [
    "*",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


# Define request body model
class Question(BaseModel):
    user_question: str


# Endpoint to handle POST requests for generating content
@app.post("/generate_content/")
def generate_content_api(question: Question):
    try:
        user_question = question.user_question
        # Generate content using the provided question
        generated_html, url = generate_content(user_question)
        return {
            "html_response": generated_html,
            "url": url,
            "user_question": user_question,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
