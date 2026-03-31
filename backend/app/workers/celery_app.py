from __future__ import annotations

import os

from celery import Celery  # type: ignore[import-untyped]

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")

celery_app = Celery(
    "crm_workers",
    broker=broker_url,
    include=["app.modules.audit.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=os.getenv("CELERY_ALWAYS_EAGER", "false").lower() == "true",
)
