
FROM python:3.9-slim


WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY nlp_service.py .

EXPOSE 8000

CMD ["python", "nlp_service.py"]
