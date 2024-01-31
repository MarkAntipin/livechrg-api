import asyncpg
import pytest
from fastapi.testclient import TestClient

from settings import TestSettings

test_settings = TestSettings()


@pytest.fixture(name='pg')
async def pg_fixture() -> asyncpg.Pool:
    pool = await asyncpg.create_pool(
        dsn=f'postgresql://{test_settings.PG_USER}:{test_settings.PG_PASSWORD}'
        f'@{test_settings.PG_HOST}:{test_settings.PG_PORT}/{test_settings.PG_DATABASE}'
    )

    async def teardown() -> None:
        await pool.execute('DELETE FROM stations;')
        await pool.execute('DELETE FROM comments;')
        await pool.execute('DELETE FROM sources;')
        await pool.execute('DELETE FROM events;')
        await pool.execute('DELETE FROM chargers;')
        await pool.execute('DELETE FROM tokens;')

    await teardown()

    yield pool

    await teardown()


@pytest.fixture()
async def client() -> TestClient:
    from run import app
    with TestClient(app=app) as client:
        yield client


@pytest.fixture(autouse=True)
async def env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('PG_HOST', test_settings.PG_HOST)
    monkeypatch.setenv('PG_PORT', str(test_settings.PG_PORT))
    monkeypatch.setenv('PG_USER', test_settings.PG_USER)
    monkeypatch.setenv('PG_PASSWORD', test_settings.PG_PASSWORD)
    monkeypatch.setenv('PG_DATABASE', test_settings.PG_DATABASE)
