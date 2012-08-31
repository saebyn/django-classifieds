from settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'circle_test',                      # Or path to database file if using sqlite3.
        'USER': 'ubuntu',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '/var/run/mysqld/mysqld.sock',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'TEST_NAME': 'circle_test',
    }
}

PAYPAL_RECEIVER_EMAIL = 'john@pledge4code.com'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SOUTH_TESTS_MIGRATE = False

SECRET_KEY = 'n&#xnm25j6wb1cw5e#7bp5ok1ti*rf9vi51e)h0&dnt8(+076n'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
