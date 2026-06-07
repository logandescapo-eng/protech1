"""Project-level views (health check)."""

import logging

from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health(request):
    payload = {'status': 'ok', 'app': 'protech'}
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
        payload['database'] = 'connected'
    except Exception as exc:
        logger.warning('Health check DB error: %s', exc)
        payload['database'] = 'disconnected'
        payload['database_error'] = str(exc)
    return JsonResponse(payload)
