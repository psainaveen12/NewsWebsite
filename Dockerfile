FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --system --gid 10001 newsapp \
    && useradd --system --uid 10001 --gid newsapp --home-dir /app newsapp

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
COPY docker/entrypoint.sh /usr/local/bin/entrypoint

RUN chmod 0555 /usr/local/bin/entrypoint \
    && mkdir -p /data/imports /data/media \
    && chown -R newsapp:newsapp /data

USER newsapp
EXPOSE 8000

ENTRYPOINT ["entrypoint"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
