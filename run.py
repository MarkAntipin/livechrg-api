import uvicorn

from settings import app_settings
from src.api.app import create_app

app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=app_settings.PORT,
    )
