from .base import *

ALLOWED_HOSTS = []

""" SQLite 접속 방식 """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
