# Demo project for graduation thesis

# Requirements:

- Docker

## Running:

1. `docker-compose up` to start Docker network
2. Attach shell to `web` container and run `python3 manage.py db upgrade` to migrate database
3. Start Celery Beat on Flask by using `celery -A tasks.celery beat`
4. Start Celery worker by using `celery -A tasks.celery worker --loglevel=info --concurrency=1`

