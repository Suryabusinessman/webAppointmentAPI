import logging
from logging.config import dictConfig

def setup_logging():
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': logging.INFO,
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'app.log',
                'formatter': 'default',
                'level': logging.INFO,
            },
        },
        'loggers': {
            'uvicorn': {
                'handlers': ['console', 'file'],
                'level': logging.INFO,
                'propagate': True,
            },
            'app': {
                'handlers': ['console', 'file'],
                'level': logging.INFO,
                'propagate': True,
            },
        }
    })