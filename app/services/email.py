import requests

from app.config import get_settings

settings = get_settings()


class EmailService:
    base_url: str = settings.base_url
    mailgun_domain: str = settings.mailgun_domain
    mailgun_api_key: str = settings.mailgun_api_key
    token_link: str = ""

    def send_email_verification_link(self, email: str, token: str = ""):
        return requests.post(
            f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
            auth=("api", self.mailgun_api_key),
            data={
                "from": "Parkplatz Transform Verification verify@parkplatztransform.com",
                "to": [email],
                "subject": "Please verify your email address",
                "text": f"http://{self.base_url}/verify/?code={token}&email={email}",
            },
        )
