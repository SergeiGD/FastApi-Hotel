import os
import pathlib

# настраиваем файлы логирования
LOG_DIR = os.path.join(pathlib.Path().resolve(), 'logs')
COMMON_LOG_FILE = '/app_logs.log'
REQUESTS_LOG_FILE = '/requests.log'
EMAIL_LOG_FILE = '/emails.log'
COMMON_LOG_PATH = LOG_DIR + COMMON_LOG_FILE
REQUESTS_LOG_PATH = LOG_DIR + REQUESTS_LOG_FILE
EMAIL_LOG_PATH = LOG_DIR + EMAIL_LOG_FILE
log_files = [COMMON_LOG_FILE, REQUESTS_LOG_FILE, EMAIL_LOG_FILE]

# создаем папку логирования, если нету
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# создаем файлы логирования, если нету
for log_file in log_files:
    if not os.path.exists(log_file):
        f = open(log_file, 'w').close()


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'base_format': {
            'format': '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
        },
        'no_name_format': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'to_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': COMMON_LOG_PATH,
            'formatter': 'base_format',
        },
        'to_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'base_format',
        },
        'requests_to_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': REQUESTS_LOG_PATH,
            'formatter': 'no_name_format',
        },
        'emails_to_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': EMAIL_LOG_PATH,
            'formatter': 'no_name_format',
        }
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
        'requests_logger': {
            'handlers': ['requests_to_file', ],
            'level': 'INFO',
            'propagate': False,
        },
        'email_logger': {
            'handlers': ['emails_to_file', ],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
}
