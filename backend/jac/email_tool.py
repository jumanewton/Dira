import smtplib
from email.mime.text import MIMEText
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
# Try loading from default locations
load_dotenv()

# If SMTP credentials are still missing, try specific paths
if not os.getenv("SMTP_USERNAME"):
    # Try backend/python/.env (relative to this file)
    try:
        current_dir = Path(__file__).parent.resolve()
        
        # Check backend/python/.env
        python_env = current_dir.parent / "python" / ".env"
        if python_env.exists():
            load_dotenv(dotenv_path=python_env)
            
        # Check root .env
        root_env = current_dir.parent.parent / ".env"
        if root_env.exists():
            load_dotenv(dotenv_path=root_env)
    except Exception as e:
        logging.warning(f"Error trying to load extra .env files: {e}")

# Setup logging
logging.basicConfig(filename='email_tool.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def send_email_tool(to: str, subject: str, body: str) -> dict:
    logging.info(f"Tool received email request to: {to}")
    
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    try:
        if not smtp_username or not smtp_password:
            logging.warning("SMTP credentials not set. Mocking email send.")
            print(f"Mock Email to {to}: {subject}\n{body}")
            return {"status": "sent", "method": "mock_email"}

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = to

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to, msg.as_string())
        server.quit()

        logging.info(f"Email sent successfully to {to}")
        return {"status": "sent", "method": "email"}
    except Exception as e:
        logging.error(f"Email send failed: {e}")
        print(f"Email send failed: {e}")
        return {"status": "failed", "error": str(e)}
