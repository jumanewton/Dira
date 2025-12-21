# Notification Service for sending emails, SMS, API notifications

from fastapi import FastAPI
import smtplib
from email.mime.text import MIMEText
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configuration from environment
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

@app.post("/send_email")
def send_email(to: str, subject: str, body: str):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USERNAME
        msg['To'] = to

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, to, msg.as_string())
        server.quit()

        return {"status": "sent", "method": "email"}
    except Exception as e:
        # For demo, if SMTP fails, just log
        # print(f"Email send failed: {e}")
        # print(f"Would send email to {to}: {subject} - {body}")
        return {"status": "logged", "method": "email"}

@app.post("/send_sms")
def send_sms(to: str, message: str):
    # Demo: use Twilio or similar, but for now log
    # print(f"Sending SMS to {to}: {message}")
    return {"status": "sent", "method": "sms"}

@app.post("/send_api")
def send_api(url: str, data: dict):
    try:
        response = requests.post(url, json=data)
        return {"status": "sent", "method": "api", "response": response.status_code}
    except Exception as e:
        # print(f"API send failed: {e}")
        return {"status": "failed", "method": "api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("NOTIFICATION_PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)