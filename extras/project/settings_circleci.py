from settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'circle',                      # Or path to database file if using sqlite3.
        'USER': 'ubuntu',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

PAYPAL_RECEIVER_EMAIL = 'john@pledge4code.com'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SOUTH_TESTS_MIGRATE = False
