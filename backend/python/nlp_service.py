# NLP Service for entity extraction, classification, confidence scoring

from fastapi import FastAPI
import spacy
from transformers import pipeline
import weaviate
from sentence_transformers import SentenceTransformer
import json

app = FastAPI()

# Load models
nlp = spacy.load("en_core_web_sm")
classifier = pipeline("text-classification", model="microsoft/DialoGPT-medium")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Vector DB setup
WEAVIATE_URL = "http://localhost:8080"
COLLECTION_NAME = "reports"

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

@app.post("/extract_entities")
def extract_entities(text: str):
    doc = nlp(text)
    entities = {
        "organisations": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
        "locations": [ent.text for ent in doc.ents if ent.label_ == "GPE"],
        "persons": [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    }
    return entities

@app.post("/classify")
def classify(text: str):
    # Simple keyword-based classification for demo
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

@app.post("/assess_urgency")
def assess_urgency(text: str):
    # Simple keyword-based urgency
    urgent_keywords = ["emergency", "urgent", "critical", "danger"]
    if any(word in text.lower() for word in urgent_keywords):
        return "high"
    elif "important" in text.lower():
        return "medium"
    else:
        return "low"

@app.post("/generate_embedding")
def generate_embedding(text: str):
    embedding = embedding_model.encode(text).tolist()
    return {"embedding": embedding}

@app.post("/store_embedding")
def store_embedding(report_id: str, title: str, description: str):
    text = title + " " + description
    embedding = embedding_model.encode(text).tolist()
    client.data_object.create({
        "report_id": report_id,
        "title": title,
        "description": description
    }, COLLECTION_NAME, vector=embedding)
    return {"status": "stored"}

@app.post("/find_duplicates")
def find_duplicates(report_id: str, title: str, description: str, threshold: float = 0.8):
    text = title + " " + description
    embedding = embedding_model.encode(text).tolist()
    result = client.query.get(COLLECTION_NAME, ["report_id", "title", "description", "_additional {certainty}"]).with_near_vector({"vector": embedding, "certainty": threshold}).do()
    duplicates = [obj for obj in result["data"]["Get"][COLLECTION_NAME] if obj["_additional"]["certainty"] > threshold and obj["report_id"] != report_id]
    return {"duplicates": duplicates}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)