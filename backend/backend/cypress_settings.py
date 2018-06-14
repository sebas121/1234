from .test_settings import *  # NOQA

IS_CYPRESS_RUN = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cypress_test_db'
    }
}

try:
    from .cypress_settings_local import *  # NOQA
except ImportError:
    pass
