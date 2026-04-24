from celery import shared_task

from apps.syncengine.services import sync_from_enriched_view


@shared_task
def sync_enriched_events_task(limit: int = 500):
    safe_limit = max(1, min(int(limit or 500), 5000))
    return sync_from_enriched_view(limit=safe_limit)


@shared_task
def sync_test_events_task(limit: int = 500):
    # Backward-compatible task name used by older scripts.
    safe_limit = max(1, min(int(limit or 500), 5000))
    return sync_from_enriched_view(limit=safe_limit)
