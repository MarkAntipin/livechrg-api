
import asyncpg

from src.repositories.postgres.tokens import TokensRepository


class TokenServices:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._tokens_repo = TokensRepository(pool=pool)

    async def does_token_exist(self, token: str) -> bool:
        return await self._tokens_repo.does_token_exist(token)
