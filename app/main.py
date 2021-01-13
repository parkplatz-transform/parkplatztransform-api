from sentry_sdk import init, capture_message
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from .routers import segments, users
from .config import get_settings

settings = get_settings()

init(
    dsn=settings.sentry_url,
    integrations=[SqlalchemyIntegration()]
)

app = FastAPI()

origins = [
    "https://pt.moewencloud.de",
    "https://app.xtransform.org",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openapi_schema = get_openapi(
    title="Parkplatz Transform",
    version="1.0.0",
    description="Parkplatz Transform API documentation",
    routes=app.routes,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(users.router)
app.include_router(segments.router)

app = SentryAsgiMiddleware(app)
