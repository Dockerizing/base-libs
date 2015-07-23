#Python2/3 compatibility layer - write Python 3-like code executable by a Python 2.7. runtime
from __future__ import absolute_import, division, print_function, unicode_literals
from future.standard_library import install_aliases
install_aliases()
from builtins import *

DLD_NAME_SUFFIX = '_DLD_NAME'
#DLD_STATE_DIR = '/dld-component-states'
DLD_STATE_DIR = 'tests/dld-component-states'
