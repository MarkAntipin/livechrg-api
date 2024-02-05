import asyncpg


class TokensRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def does_token_exist(self, token: str) -> bool:
        return await self._update_token_usage(token)

    async def _update_token_usage(self, token: str) -> bool:
        query = """
            UPDATE
                tokens
            SET
                request_count = request_count + 1,
                updated_at = now()
            WHERE
                api_key = $1
            RETURNING api_key;
        """
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, token)
        is_updated = bool(rows)
        return is_updated
