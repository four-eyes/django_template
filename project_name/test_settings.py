from .settings import *

INSTALLED_APPS = INSTALLED_APPS + (
    'test_without_migrations',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
