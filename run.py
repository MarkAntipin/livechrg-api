import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware

from settings import AppSettings
from src.api.app import create_app
from src.api.middlewares.logger import logger_middleware

app_settings = AppSettings()
app = create_app(settings=app_settings)
app.add_middleware(BaseHTTPMiddleware, dispatch=logger_middleware)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=app_settings.PORT,
    )
