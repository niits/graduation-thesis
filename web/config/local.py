from datetime import timedelta

SESSION_DURATION = 1

DEBUG = True
SQLALCHEMY_DATABASE_URI = "postgresql://niits:abcd1234@db:5432/page"

CELERY_BROKER_URL = "sqla+postgresql://niits:abcd1234@db:5432/page"
SQLALCHEMY_TRACK_MODIFICATIONS = False
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERYBEAT_SCHEDULE = {
    "example_task": {
        "task": "tasks.detect_bots",
        "schedule": timedelta(minutes=SESSION_DURATION),
        "args": (),
    },
}

ERROR_404_HELP = False