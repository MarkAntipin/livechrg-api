import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import PostgresSettings, app_settings
from src.api.routers.v1.stations import router as stations_router_v1


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def setup_pg_pool(app: FastAPI) -> None:
    pg_settings = PostgresSettings()
    pool = await asyncpg.create_pool(dsn=pg_settings.url)
    app.state.pool = pool


def create_app() -> FastAPI:
    app = FastAPI(
        title=app_settings.TITLE,
        version=app_settings.VERSION,
    )
    setup_middlewares(app)

    @app.on_event('startup')
    async def startup() -> None:
        await setup_pg_pool(app)

    @app.on_event('shutdown')
    async def shutdown() -> None:
        await app.state.pool.close()

    app.include_router(stations_router_v1)
    return app
