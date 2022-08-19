from sentry_sdk import init
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from brotli_asgi import BrotliMiddleware

from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.app import app
from app.routers import segments, users, clusters
from app.config import settings


origins = [
    "https://app.xtransform.org",
    "https://staging.app.xtransform.org",
    "https://www.xtransform.org",
    "http://yavin4.tilaa.cloud",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8023",
    "http://192.168.0.40:3000",
    "http://157.90.225.22:3000",
    "http://192.168.0.40:8000",
    "https://sleepy-mahavira-b3d8a5.netlify.app"
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

app.add_middleware(BrotliMiddleware)
app.include_router(users.router)
app.include_router(segments.router)
app.include_router(clusters.router)


if settings.sentry_url:
    init(dsn=settings.sentry_url)
    app = SentryAsgiMiddleware(app)
