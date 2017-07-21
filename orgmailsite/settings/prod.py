from .common import *

ADMINS = (
    ('Mathias Rav', 'rav@cs.au.dk'),
)

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False

STATIC_ROOT = os.path.join(BASE_DIR, 'prodekanus/static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'prodekanus/uploads')

ALLOWED_HOSTS = ['orgmail.tket.dk']

# Update database configuration with $DATABASE_URL.
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
    DATABASES['default'].setdefault('OPTIONS', {})['init_command'] = (
        "SET sql_mode='STRICT_TRANS_TABLES'")

EMAIL_HOST = 'smtp01.uni.au.dk'
SERVER_EMAIL = 'mailhole@prodekanus.studorg.au.dk'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': ('[%(asctime)s %(name)s %(levelname)s] ' +
                       '%(message)s'),
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(BASE_DIR, 'prodekanus/django.log'),
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
        },
        'mailhole': {
            'handlers': ['file', 'mail_admins'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}
