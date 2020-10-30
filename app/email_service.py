import requests

from .config import get_settings

settings = get_settings()


def send_email_verification_link(email: str, token: str = ""):
    token_link = f"{token}"
    return requests.post(
        f"https://api.mailgun.net/v3/{settings.mailgun_domain}/messages",
        auth=("api", settings.mailgun_api_key),
        data={
            "from": "Park Platz Transform Verification verify@parkplatztransform.com",
            "to": [email],
            "subject": "Please verify your email address",
            "text": token_link,
        },
    )
