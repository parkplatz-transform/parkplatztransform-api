import base64
import logging
import random
import string
import time

import jwt
from typing import Optional

from app.config import settings


def decode_jwt(token: str) -> dict:
    token_metadata = jwt.decode(
        token, settings.secret_key, algorithms=[settings.jwt_algorithm]
    )
    return token_metadata


# Adapted from:
# https://github.com/anthcor/pypale


class OneTimeAuth:
    JWT_ALGORITHM = settings.jwt_algorithm
    ENCODING = "utf8"

    def __init__(
        self,
        token_ttl_minutes: int = int(settings.token_ttl_minutes),
        base_url: str = settings.base_url,
        secret_key: str = settings.secret_key,
        token_issue_ttl_seconds: int = int(settings.token_issue_ttl_seconds),
    ):
        self.token_ttl_minutes = token_ttl_minutes
        self.base_url = base_url
        self.secret_key = secret_key
        self.token_issue_ttl_seconds = token_issue_ttl_seconds

    def generate_token(self, email: str) -> str:
        return base64.b64encode(
            jwt.encode(
                self.generate_token_metadata(email),
                self.secret_key,
                algorithm=self.JWT_ALGORITHM,
            )
        ).decode(self.ENCODING)

    def generate_token_metadata(self, email: str) -> dict:
        return {
            "sub": email,
            "jti": self.one_time_nonce(),
            "iat": int(time.time()),
            "exp": int(time.time()) + (self.token_ttl_minutes * 60),
            "iss": self.base_url,
        }

    def one_time_nonce(
        self, size=16, chars=string.ascii_letters + string.digits + "-"
    ) -> str:
        return "".join(random.choice(chars) for _ in range(size))

    def get_decoded_token(self, return_token: str) -> Optional[dict]:
        try:
            decoded_return_token = base64.b64decode(return_token).decode(self.ENCODING)
            return jwt.decode(
                decoded_return_token, self.secret_key, algorithms=[self.JWT_ALGORITHM]
            )
        except Exception as e:
            return None

    def valid_token(self, return_token: str, return_email: str = "") -> bool:
        try:
            decoded_token = self.get_decoded_token(return_token=return_token)
            if (decoded_token["iat"] + self.token_issue_ttl_seconds) < int(time.time()):
                logging.warning("Token was issued too long ago.")
                return False
            elif return_email != "":
                if decoded_token["sub"] != return_email:
                    logging.warning("Token is not issued to the right user.")
                    return False
                return True
            else:
                return True
        except Exception as e:
            logging.exception(f"Raised exception while validating login link: {e}")
            return False
