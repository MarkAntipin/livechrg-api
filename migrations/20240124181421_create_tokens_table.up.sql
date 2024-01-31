CREATE TABLE IF NOT EXISTS tokens (
    id SERIAL PRIMARY KEY,
--     # TODO: TEXT
    api_key VARCHAR(100) NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 0,
--     # TODO: CURRENT_TIMESTAMP
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT api_key_unique UNIQUE (api_key)
);