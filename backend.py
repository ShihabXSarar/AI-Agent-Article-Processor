import os
import uuid
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Agent Backend")

# Configure CORS to allow all origins so Streamlit can communicate seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic model for data validation
class ArticleRequest(BaseModel):
    email: str
    article_url: str


# n8n Webhook URL loaded from env
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
if not N8N_WEBHOOK_URL:
    raise ValueError("ERROR: N8N_WEBHOOK_URL is not set in environment variables or .env file.")


@app.post("/process-article")
async def process_article(request_data: ArticleRequest):
    try:
        # 1. Generate a completely random, unique session ID
        session_id = str(uuid.uuid4())

        # 2. Construct the JSON payload
        payload = {
            "email": request_data.email,
            "article_url": request_data.article_url,
            "session_id": session_id,
        }

        # 3. Send HTTP POST request to the n8n Webhook URL
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)

        # Raise an exception if the response status code indicates an HTTP error
        response.raise_for_status()

        # 4. Return success response
        return {"status": "success", "session_id": session_id}

    except requests.exceptions.RequestException as e:
        # Capture the error gracefully and return a helpful failure message
        print(f"Error forwarding request to n8n webhook: {e}")
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with the automation pipeline. Please try again later.",
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred.",
        )


# Root endpoint for health check
@app.get("/")
def read_root():
    return {"status": "Backend is running!"}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
