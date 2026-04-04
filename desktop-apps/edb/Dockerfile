FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

EXPOSE 8000

ENV EDB_DB_PATH=/data/edb.db
ENV EDB_API_HOST=0.0.0.0
ENV EDB_API_PORT=8000

VOLUME /data

CMD ["edb", "serve"]
