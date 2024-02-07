import asyncpg

from src.repositories.postgres.tokens import TokensRepository


class TokenServices:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._tokens_repo = TokensRepository(pool=pool)

    async def is_existing_token(self, token: str) -> bool:
        return await self._tokens_repo.is_existing_token(str(token))
