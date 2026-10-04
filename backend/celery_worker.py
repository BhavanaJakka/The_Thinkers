import os
from celery import Celery
from backend.config import Config

def make_celery(app_name=__name__):
    redis_url = Config.REDIS_URL
    return Celery(
        app_name,
        backend=redis_url,
        broker=redis_url
    )

celery = make_celery()

def trigger_scan_task(app, scan_id: str, extract_dir: str):
    """
    Triggers scan via Celery if available, or runs in background thread / sync fallback.
    """
    try:
        @celery.task(name="execute_scan_task")
        def execute_scan_task(s_id, e_dir):
            with app.app_context():
                from backend.scanner.runner import run_scan_pipeline
                run_scan_pipeline(s_id, e_dir)

        # Attempt async execution
        execute_scan_task.delay(scan_id, extract_dir)
        print(f"[CELERY] Scan {scan_id} queued in Celery worker.")
    except Exception as e:
        print(f"[CELERY OFFLINE] Running scan {scan_id} synchronously as fallback. Info: {e}")
        from threading import Thread
        def run_in_thread():
            with app.app_context():
                from backend.scanner.runner import run_scan_pipeline
                run_scan_pipeline(scan_id, extract_dir)
        thread = Thread(target=run_in_thread)
        thread.start()
