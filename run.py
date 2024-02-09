import uvicorn

from settings import AppSettings
from src.api.app import create_app

app_settings = AppSettings()
app = create_app(settings=app_settings)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=app_settings.PORT,
    )