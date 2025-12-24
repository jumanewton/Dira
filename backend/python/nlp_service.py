# NLP Service for entity extraction, classification, confidence scoring

from fastapi import FastAPI
import spacy
from transformers import pipeline
import weaviate
from sentence_transformers import SentenceTransformer
import json
import os
import sys
import base64
import io
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from vector_db.config import WEAVIATE_URL, COLLECTION_NAME

# Load environment variables
load_dotenv()

# Logging setup
import logging
logging.basicConfig(filename='nlp_service.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Configuration from environment
CACHE_DIR = os.getenv("HUGGINGFACE_CACHE_DIR", "./models_cache")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    
    GEMINI_MODEL_NAME = 'gemini-2.5-flash' 

else:
    # print("Warning: GEMINI_API_KEY not found. Falling back to local models where possible, or failing.")
    pass

# Load models with cache directory
nlp_model = None
def get_nlp():
    global nlp_model
    if nlp_model is None:
        logging.info("Loading Spacy model...")
        nlp_model = spacy.load("en_core_web_sm")
    return nlp_model

# classifier = pipeline("text-classification", model="microsoft/DialoGPT-medium", cache_dir=CACHE_DIR) # Replaced by Gemini
# message_drafter = pipeline("text-generation", model="gpt2", cache_dir=CACHE_DIR) # Replaced by Gemini

embed_model = None
def get_embedding_model():
    global embed_model
    if embed_model is None:
        logging.info("Loading SentenceTransformer model...")
        embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder=CACHE_DIR)
    return embed_model

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
    # print(f"Warning: Could not connect to Weaviate at {WEAVIATE_URL}. Vector DB features will be disabled. Error: {e}")
    client = None

from pydantic import BaseModel

class TextRequest(BaseModel):
    text: str

@app.post("/extract_entities")
def extract_entities(request: TextRequest):
    doc = get_nlp()(request.text)
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
            
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            # Simple parsing - in production I will use structured output or robust JSON parsing
            import re
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return data
        except Exception as e:
            # print(f"Gemini classification failed: {e}")
            pass

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
    
    confidence = 0.7  # confidence
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
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            urgency = response.text.strip().lower()
            if urgency in ["low", "medium", "high"]:
                return urgency
        except Exception as e:
            # print(f"Gemini urgency assessment failed: {e}")
            pass

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
    embedding = get_embedding_model().encode(request.text).tolist()
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
    embedding = get_embedding_model().encode(text).tolist()
    client.data_object.create({
        "report_id": request.report_id,
        "title": request.title,
        "description": request.description
    }, COLLECTION_NAME, vector=embedding)
    return {"status": "stored"}

class FindDuplicatesRequest(BaseModel):
    report_id: str
    title: str
    description: str
    threshold: float = 0.8

@app.post("/find_duplicates")
def find_duplicates(request: FindDuplicatesRequest):
    logging.info(f"Finding duplicates for report {request.report_id}")
    if not client:
        logging.warning("Weaviate client not available")
        return {"duplicates": []}
        
    text = request.title + " " + request.description
    embedding = get_embedding_model().encode(text).tolist()
    
    response = (
        client.query
        .get(COLLECTION_NAME, ["report_id", "title", "description"])
        .with_near_vector({
            "vector": embedding,
            "certainty": request.threshold
        })
        .with_additional(["certainty"])
        .with_limit(100)
        .do()
    )
    
    duplicates = []
    if "data" in response and "Get" in response["data"] and COLLECTION_NAME in response["data"]["Get"]:
        results = response["data"]["Get"][COLLECTION_NAME]
        for res in results:
            if res["report_id"] != request.report_id:
                # Add certainty to the result
                if "_additional" in res:
                    res["score"] = res["_additional"]["certainty"]
                duplicates.append(res)
                logging.info(f"Found duplicate: {res['report_id']} with score {res.get('score')}")
    
    logging.info(f"Found {len(duplicates)} duplicates")
    return {"duplicates": duplicates}

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
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            message = response.text.strip()
        except Exception as e:
            # print(f"Gemini drafting failed: {e}")
            pass

    # Fallback if generation fails or no key
    if not message or len(message) < 20:
        message = f"Urgent Report: {request.title}\n\n{request.description}\n\nUrgency: {request.urgency}\n\nPlease investigate immediately."
    
    return {"message": message}

class AnalyzeImageRequest(BaseModel):
    image_data: str # base64 encoded
    mime_type: str = "image/jpeg"

@app.post("/analyze_image")
def analyze_image(request: AnalyzeImageRequest):
    if not request.image_data:
        return {"analysis": "No image provided."}
        
    if GEMINI_API_KEY:
        try:
            # Decode base64
            image_data = request.image_data
            if "," in image_data:
                image_data = image_data.split(",")[1]
            
            image_bytes = base64.b64decode(image_data)
            
            prompt = "Analyze this image for a public report. Identify if there is any infrastructure damage, safety issue, or utility problem. If found, state 'Confirmed: [Issue Type], [Severity]'. Then provide a brief description."
            
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type=request.mime_type)
                ]
            )
            return {"analysis": response.text.strip()}
        except Exception as e:
            logging.error(f"Gemini image analysis failed: {e}")
            return {"analysis": "Image analysis failed."}
            
    return {"analysis": "Image analysis not available (No API Key)."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("NLP_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)