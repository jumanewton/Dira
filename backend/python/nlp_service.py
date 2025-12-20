# NLP Service for entity extraction, classification, confidence scoring

from fastapi import FastAPI
import spacy
from transformers import pipeline
import weaviate
from sentence_transformers import SentenceTransformer
import json
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from vector_db.config import WEAVIATE_URL, COLLECTION_NAME

# Load environment variables
load_dotenv()

app = FastAPI()

# Configuration from environment
CACHE_DIR = os.getenv("HUGGINGFACE_CACHE_DIR", "./models_cache")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use Gemini 3 Pro (Preview)
    gemini_model = genai.GenerativeModel('gemini-3.0-pro-preview') 
else:
    print("Warning: GEMINI_API_KEY not found. Falling back to local models where possible, or failing.")

# Load models with cache directory
nlp = spacy.load("en_core_web_sm")
# classifier = pipeline("text-classification", model="microsoft/DialoGPT-medium", cache_dir=CACHE_DIR) # Replaced by Gemini
# message_drafter = pipeline("text-generation", model="gpt2", cache_dir=CACHE_DIR) # Replaced by Gemini
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder=CACHE_DIR) # Keep local embedding for now or switch to Gemini embedding

try:
    client = weaviate.Client(url=WEAVIATE_URL)
    # Create collection if not exists
    if not client.schema.exists(COLLECTION_NAME):
        client.schema.create_class({
            "class": COLLECTION_NAME,
            "properties": [
                {"name": "report_id", "dataType": ["string"]},
                {"name": "title", "dataType": ["string"]},
                {"name": "description", "dataType": ["string"]},
            ],
            "vectorizer": "none"  # we'll provide vectors
        })
except Exception as e:
    print(f"Warning: Could not connect to Weaviate at {WEAVIATE_URL}. Vector DB features will be disabled. Error: {e}")
    client = None

from pydantic import BaseModel

class TextRequest(BaseModel):
    text: str

@app.post("/extract_entities")
def extract_entities(request: TextRequest):
    doc = nlp(request.text)
    entities = {
        "organisations": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
        "locations": [ent.text for ent in doc.ents if ent.label_ == "GPE"],
        "persons": [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    }
    return entities

class ClassifyRequest(BaseModel):
    text: str

@app.post("/classify")
def classify(request: ClassifyRequest):
    text = request.text
    if GEMINI_API_KEY:
        try:
            prompt = f"""Classify the following public report into one of these categories: infrastructure, safety, utility, health, general.
            Also provide a confidence score between 0.0 and 1.0.
            Return JSON with keys 'category' and 'confidence'.
            
            Report: {text}"""
            
            response = gemini_model.generate_content(prompt)
            # Simple parsing - in production use structured output or robust JSON parsing
            import re
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return data
        except Exception as e:
            print(f"Gemini classification failed: {e}")

    # Fallback to keyword-based classification
    text_lower = text.lower()
    if any(word in text_lower for word in ["road", "street", "pothole", "traffic", "infrastructure"]):
        category = "infrastructure"
    elif any(word in text_lower for word in ["police", "crime", "safety", "security"]):
        category = "safety"
    elif any(word in text_lower for word in ["water", "electricity", "power", "utility"]):
        category = "utility"
    elif any(word in text_lower for word in ["health", "medical", "hospital"]):
        category = "health"
    else:
        category = "general"
    
    confidence = 0.7  # Placeholder confidence
    return {"category": category, "confidence": confidence}

class UrgencyRequest(BaseModel):
    text: str

@app.post("/assess_urgency")
def assess_urgency(request: UrgencyRequest):
    text = request.text
    if GEMINI_API_KEY:
        try:
            prompt = f"""Assess the urgency of this public report as 'low', 'medium', or 'high'.
            Return only the urgency level string.
            
            Report: {text}"""
            response = gemini_model.generate_content(prompt)
            urgency = response.text.strip().lower()
            if urgency in ["low", "medium", "high"]:
                return urgency
        except Exception as e:
            print(f"Gemini urgency assessment failed: {e}")

    # Simple keyword-based urgency
    urgent_keywords = ["emergency", "urgent", "critical", "danger"]
    if any(word in text.lower() for word in urgent_keywords):
        return "high"
    elif "important" in text.lower():
        return "medium"
    else:
        return "low"

class EmbeddingRequest(BaseModel):
    text: str

@app.post("/generate_embedding")
def generate_embedding(request: EmbeddingRequest):
    embedding = embedding_model.encode(request.text).tolist()
    return {"embedding": embedding}

class StoreEmbeddingRequest(BaseModel):
    report_id: str
    title: str
    description: str

@app.post("/store_embedding")
def store_embedding(request: StoreEmbeddingRequest):
    if not client:
        return {"status": "skipped", "reason": "Weaviate not connected"}
        
    text = request.title + " " + request.description
    embedding = embedding_model.encode(text).tolist()
    client.data_object.create({
        "report_id": request.report_id,
        "title": request.title,
        "description": request.description
    }, COLLECTION_NAME, vector=embedding)
    return {"status": "stored"}

class DraftMessageRequest(BaseModel):
    title: str
    description: str
    urgency: str
    org_type: str

@app.post("/draft_message")
def draft_message(request: DraftMessageRequest):
    prompt = f"Draft a professional notification message to a {request.org_type} organization about this public report. Title: {request.title}. Description: {request.description}. Urgency level: {request.urgency}. Keep it concise and professional."
    
    message = ""
    if GEMINI_API_KEY:
        try:
            response = gemini_model.generate_content(prompt)
            message = response.text.strip()
        except Exception as e:
            print(f"Gemini drafting failed: {e}")

    # Fallback if generation fails or no key
    if not message or len(message) < 20:
        message = f"Urgent Report: {request.title}\n\n{request.description}\n\nUrgency: {request.urgency}\n\nPlease investigate immediately."
    
    return {"message": message}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("NLP_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)