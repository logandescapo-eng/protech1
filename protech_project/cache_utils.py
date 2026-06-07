"""Redis caching helpers — see README.md Caching Strategy."""

import hashlib
import json
import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

WORKERS_CACHE_TTL = 300
CATEGORIES_CACHE_TTL = 600


def _filters_key(prefix, filters):
    raw = json.dumps(filters or {}, sort_keys=True, default=str)
    digest = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f'protech:{prefix}:{digest}'


def get_cached_workers(filters, loader):
    key = _filters_key('workers', filters)
    data = cache.get(key)
    if data is not None:
        logger.debug('Cache hit: %s', key)
        return data
    data = loader()
    cache.set(key, data, WORKERS_CACHE_TTL)
    logger.info('Cache set: %s (%s items)', key, len(data))
    return data


def get_cached_categories(loader):
    key = 'protech:categories'
    data = cache.get(key)
    if data is not None:
        logger.debug('Cache hit: %s', key)
        return data
    data = loader()
    cache.set(key, data, CATEGORIES_CACHE_TTL)
    logger.info('Cache set: %s', key)
    return data


def invalidate_workers_cache():
    logger.info('Invalidating worker list caches')
    try:
        cache.delete_pattern('protech:workers:*')
    except AttributeError:
        cache.clear()


def invalidate_categories_cache():
    cache.delete('protech:categories')
