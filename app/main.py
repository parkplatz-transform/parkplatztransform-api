from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from .routers import segments, users

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(users.router)
app.include_router(segments.router)
