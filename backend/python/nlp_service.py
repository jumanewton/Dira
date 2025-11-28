# NLP Service for entity extraction, classification, confidence scoring

from fastapi import FastAPI
import spacy
from transformers import pipeline

app = FastAPI()

# Load models
nlp = spacy.load("en_core_web_sm")
classifier = pipeline("text-classification", model="microsoft/DialoGPT-medium")

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
    # Placeholder classification
    result = classifier(text[:512])  # Truncate for model
    category = result[0]["label"]
    confidence = result[0]["score"]
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)