from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .routers import segments, users
from .open_api import custom_openapi

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


app.openapi = lambda: custom_openapi(app)


app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(users.router)
app.include_router(segments.router)
