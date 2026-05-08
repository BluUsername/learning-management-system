"""Local development settings.

Loaded by default via `manage.py` (so `python manage.py runserver` works
out of the box). Permissive defaults — never use these in production.
"""

import os

from .base import *  # noqa: F401,F403
from .base import SECRET_KEY as _BASE_SECRET_KEY

DEBUG = True

# Insecure fallback so a brand-new clone runs without any setup. Real
# secrets only matter in prod.
SECRET_KEY = _BASE_SECRET_KEY or 'django-insecure-dev-only-key-do-not-use-in-production'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1,backend,testserver',
    ).split(',')
    if host.strip()
]

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:3000,http://localhost:80',
    ).split(',')
    if origin.strip()
]
