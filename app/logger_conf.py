import os
import pathlib

LOG_DIR = os.path.join(pathlib.Path().resolve(), 'logs')
LOG_FILE = '/app_logs.log'
LOG_PATH = LOG_DIR + LOG_FILE

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

if not os.path.exists(LOG_PATH):
    f = open(LOG_PATH, 'w').close()


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'base_format': {
            'format': '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'to_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': LOG_PATH,
            'formatter': 'base_format',
        },
        'to_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'base_format',
        },
    },
    'loggers': {
        '': {
            'handlers': ['to_file', 'to_console', ],
            'level': 'INFO',
            'propagate': True,
        },
        'routers.auth': {
            'handlers': ['to_file', 'to_console', ],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
