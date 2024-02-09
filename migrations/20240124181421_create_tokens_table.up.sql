CREATE TABLE IF NOT EXISTS tokens (
    id SERIAL PRIMARY KEY,
    api_key TEXT NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT api_key_unique UNIQUE (api_key)
);