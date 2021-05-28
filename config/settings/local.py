from .base import *

ALLOWED_HOSTS = []

""" SQLite 접속 방식 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

""" MySQL 접속 방식 ROOT : cjfv2021@@ """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 사용하려는 DB 이름
        'NAME': 'cjfv_oneexp',
        # 여기부터 connection 정보
        'USER' : 'cjfv_oneexp',
        'PASSWORD' : 'cjfv2021@@',
        'HOST' : '127.0.0.1',
        'PORT' : '3306',
    }
}