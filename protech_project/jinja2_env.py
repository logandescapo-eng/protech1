"""Jinja2 environment with Flask-template compatibility for Django."""

from urllib.parse import urlencode

from django.contrib.messages import get_messages
from django.middleware.csrf import get_token
from django.urls import NoReverseMatch, reverse
from django.utils.html import mark_safe
from jinja2 import Environment, pass_context


QUERY_PARAM_KEYS = ('tab', 'mark_all', 'read', 'with', 'booking')


def url_for(endpoint, **values):
    """Flask-compatible url_for using Django URL names (same as Flask endpoint names)."""
    query = {}
    for key in QUERY_PARAM_KEYS:
        if key in values:
            query[key] = values.pop(key)
    try:
        path = reverse(endpoint, kwargs=values)
    except NoReverseMatch:
        return '#'
    if query:
        path = f'{path}?{urlencode(query)}'
    return path


@pass_context
def get_flashed_messages(context, with_categories=False):
    request = context.get('request')
    if request is None:
        return []
    storage = get_messages(request)
    if with_categories:
        return [(m.tags, str(m)) for m in storage]
    return [str(m) for m in storage]


@pass_context
def csrf_field(context):
    request = context.get('request')
    if request is None:
        return ''
    token = get_token(request)
    return mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'url_for': url_for,
        'get_flashed_messages': get_flashed_messages,
        'csrf_field': csrf_field,
    })
    return env
