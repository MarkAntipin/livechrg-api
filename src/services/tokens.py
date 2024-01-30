import uuid

import asyncpg

from src.repositories.postgres.tokens import TokensRepository


class TokenServices:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._tokens_repo = TokensRepository(pool=pool)

    async def add_new_token(self) -> str:
        new_token = str(uuid.uuid4())
        await self._tokens_repo.add_new_token(new_token)
        return new_token

    async def does_token_exist(self, token: str) -> bool:
        if await self._is_valid_uuid(token):
            return await self._tokens_repo.does_token_exist(token)
        return False

    @staticmethod
    async def _is_valid_uuid(uuid_to_test: any, version: int = 4) -> bool:
        try:
            uuid_obj = uuid.UUID(uuid_to_test, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test
