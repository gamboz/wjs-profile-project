"""Celery application (app) for async tasks."""

import time
from numbers import Number

from celery import Celery

app = Celery(main="wjs-tasks", broker="pyamqp://guest@localhost")


@app.task
def add(x: Number, y: Number, sleep: Number = 0) -> Number:
    """Sum two numbers."""
    time.sleep(sleep)
    return x + y
