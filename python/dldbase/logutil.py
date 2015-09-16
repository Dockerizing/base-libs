# Python2/3 compatibility layer - write Python 3-like code executable by a Python 2.7. runtime
from __future__ import absolute_import, division, print_function, unicode_literals
from future.standard_library import install_aliases

install_aliases()
from builtins import *

import os
from os import path as osp
import copy
import logging
import logging.config

DEV_MODE = bool(os.environ.get('DLD_DEV', ''))
LOG_SETTINGS = {
    'version': 1,
    'handlers': {
        'cli_user_console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'cli_user',
            'stream': 'ext://sys.stdout',
        },
        'dev_console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'complete.log',
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'formatters': {
        'cli_user': {
            'format': 'DLD %(levelname)-8s %(message)s'
        },
        'dev': {
            'format': '%(asctime)s %(module)s [%(levelname)s]: $(message)s'
        },
        'detailed': {
            'format': '%(asctime)s %(module)-17s line:%(lineno)-4d '
                      '%(levelname)-8s %(message)s',
        },
    },
    'loggers': {
        'dld': {
            'level': DEV_MODE and 'DEBUG' or 'INFO',
            'handlers': DEV_MODE and ['dev_console', 'file'] or ['cli_user_console'],
        }
    }
}


def logging_init(log_dir):
    def update_filename(handler_dict):
        filename = handler_dict['filename']
        handler_dict['filename'] = osp.join(log_dir, filename)

    settings = copy.deepcopy(LOG_SETTINGS)
    handlers = settings['handlers']

    [update_filename(h) for h in handlers.values() if 'filename' in h.keys()]
    logging.config.dictConfig(settings)
