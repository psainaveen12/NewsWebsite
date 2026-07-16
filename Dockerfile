FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv/app

RUN groupadd --system app && useradd --system --gid app --home-dir /srv/app app

COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY --chown=app:app app ./app
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app docker ./docker
COPY --chown=app:app alembic.ini ./

USER app
EXPOSE 8000

ENTRYPOINT ["/srv/app/docker/entrypoint.sh"]
