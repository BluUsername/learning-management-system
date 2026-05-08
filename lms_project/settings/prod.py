"""Production settings.

Loaded automatically by `wsgi.py` / `asgi.py` so Heroku and any other
WSGI host gets the hardened config without needing to set
`DJANGO_SETTINGS_MODULE` explicitly (though doing so is still recommended).

Required environment variables: `SECRET_KEY` and `ALLOWED_HOSTS`. Both
fail fast at import time if missing — better to refuse to boot than to
serve traffic with an insecure SECRET_KEY or accept arbitrary Host
headers.

`CORS_ALLOWED_ORIGINS` is recommended but not enforced. An empty value
means the API rejects every cross-origin request, which fails visibly
the moment the frontend tries to reach it (so silent insecurity is not a
risk here).
"""

import os

from .base import *  # noqa: F401,F403
from .base import SECRET_KEY as _BASE_SECRET_KEY


if not _BASE_SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable must be set in production."
    )
SECRET_KEY = _BASE_SECRET_KEY

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise RuntimeError(
        "ALLOWED_HOSTS environment variable must be set in production."
    )

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]

# HTTPS / cookie hardening — only safe behind a TLS-terminating proxy
# like Heroku's router.
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
