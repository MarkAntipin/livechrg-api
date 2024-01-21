CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS stations (
    id SERIAL NOT NULL PRIMARY KEY,
    coordinates geography(POINT) NOT NULL,
    geo JSONB,
    address TEXT,
    ocpi_ids JSONB,
    rating FLOAT,

    created_at TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS stations_coordinates_idx ON stations USING GIST(coordinates);


CREATE TABLE IF NOT EXISTS sources (
    station_id INTEGER NOT NULL,
    station_inner_id BIGINT NOT NULL,
    source TEXT NOT NULL,

    FOREIGN KEY (station_id) REFERENCES stations (id) ON DELETE CASCADE,
    CONSTRAINT station_inner_id_source_unique UNIQUE (station_inner_id, source)
);
CREATE INDEX IF NOT EXISTS sources_station_id_idx ON sources (station_id);


CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    charged_at TIMESTAMPTZ NOT NULL,
    name TEXT,
    is_problem BOOLEAN,

    FOREIGN KEY (station_id) REFERENCES stations (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS events_station_id_idx ON events (station_id);


CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    user_name TEXT,
    created_at TIMESTAMPTZ,
    source TEXT NOT NULL,
    rating INTEGER,

    FOREIGN KEY (station_id) REFERENCES stations (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS comments_station_id_idx ON comments (station_id);


CREATE TABLE IF NOT EXISTS chargers (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL,
    ocpi_ids JSONB,
    network TEXT,

    FOREIGN KEY (station_id) REFERENCES stations (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS chargers_station_id_idx ON chargers (station_id);
