import logging

import asyncpg


class TokensRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def does_token_exist(self, token: str) -> bool:
        return await self._update_token_usage(token)
        #TODO: remove

        try:
            await self._update_token_usage(token)
            return True
        except asyncpg.PostgresError:
            return False

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

        #TODO: remove

        try:
            async with self.pool.acquire() as connection:
                await connection.execute(query, token)
            return True
        except asyncpg.PostgresError as e:
            raise e

    # TODO: remove if not used
    async def add_new_token(self, new_token: str) -> None:
        query = """
                    INSERT
                    INTO tokens (api_key)
                    VALUES ($1);
                    """

        async with self.pool.acquire() as connection:
            await connection.execute(
                query,
                new_token
            )
