from fastapi.openapi.utils import get_openapi

from .config import get_settings


def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Parkplatz Transform",
        version="1.0.0",
        description="Parkplatz Transform API documentation",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": get_settings().base_url}
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema
