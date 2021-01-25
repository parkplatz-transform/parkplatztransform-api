import requests

from app.config import get_settings

settings = get_settings()


class EmailService:
    base_url: str = settings.frontend_url
    mailgun_domain: str = settings.mailgun_domain
    mailgun_api_key: str = settings.mailgun_api_key
    token_link: str = ""

    def send_email_verification_link(self, email: str, token: str = ""):
        req = requests.post(
            f"https://api.eu.mailgun.net/v3/{self.mailgun_domain}/messages",
            auth=("api", self.mailgun_api_key),
            data={
                "from": f"ParkplatzTransform noreply@mg.xtransform.org",
                "to": [email],
                "subject": "Verifizierung deiner E-Mail Adresse erforderlich",
                "text": f"""
                Hallo lieber PTler,
                um dich einzuloggen, klicke bitte auf diesen Link: {self.base_url}/verify-token/?code={token}&email={email}
                Viel Erfolg!

                PS: Entwickler klicken während der Entwicklung hier: http://localhost:3000/verify-token/?code={token}&email={email}
                """,
            },
        )
        if req.status_code != 200:
            return Exception(req.content)
        return req
