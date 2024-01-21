# livechrg-api

## Run App

### Without Docker
**Dependencies:**

- postgres
- postgis (https://postgis.net)
- golang-migrate (https://github.com/golang-migrate/migrate)
- poetry (https://python-poetry.org)

**Create .env with:**
```
PG_HOST=
PG_PORT=
PG_USER=
PG_PASSWORD=
PG_DATABASE=
```

**Install libs:**
```
poetry install
```

**Apply migrations**
```
migrate -path ./migrations -database "postgres://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}?sslmode=disable" up
```

**Run App**
```
python run.py
```

### With Docker
Build image:
```
docker build --no-cache -t livechrg-api .
```

Change in docker-compose.yml env vars and:
```
docker-compose up -d --no-deps
```



## Development

### Create migrations
```
migrate create -ext sql -dir migrations {migration-name} 
```


### Linter:
```
poetry run ruff check . --fix
```

### Functional Tests:
**Run postgres for tests**
```
docker run --name livechrg-api-pg -e POSTGRES_USER=livechrg-api -e POSTGRES_PASSWORD=livechrg-api -e POSTGRES_DB=livechrg-api -p 5437:5432 -d postgis/postgis:14-3.3-alpine
```
**Apply migrations**
```
migrate -path ./migrations -database "postgres://livechrg-api:livechrg-api@localhost:5436/livechrg-api?sslmode=disable" up
```
**Apply migrations**
```
pytest -v tests_functional
```
**Stop postgres for tests**
```
docker stop livechrg-api-pg | xargs docker rm
```
