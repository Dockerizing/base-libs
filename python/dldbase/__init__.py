import os

DEV_MODE = bool(os.environ.get('DLD_DEV', ''))
DLD_NAME_SUFFIX = '_DLD_NAME'
DLD_STATE_DIR = '/dld-component-states'
