import smtplib

from fastapi import BackgroundTasks, FastAPI
from email.mime.text import MIMEText
import requests

from config import get_settings

settings = get_settings()

# TOOD: discuss and fill appropriate values here
def email_verification_link(email: str, token: str = ""):
    token_link = f"https://frontend-domain.com/verify?token={token}"
    print("Email: ", token_link)
    return requests.post(
        f"https://api.mailgun.net/v3/{settings.mailgun_domain}/messages",
        auth=("api", settings.mailgun_api_key),
        data={
            "from": "Park Platz Verification verify@parkplatztransform.com",
            "to": [email],
            "subject": "Please verify your email address",
            "text": token_link,
        },
    )


async def send_verification(email: str, token: str):
    BackgroundTasks.add_task(email_verification_link, email, token=token)
    return {"message": "Notification sent in the background"}
