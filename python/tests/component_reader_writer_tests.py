from __future__ import absolute_import, division, print_function, unicode_literals

from future.standard_library import install_aliases

install_aliases()
from builtins import *

import logging
import tempfile
import shutil
from os import path as osp
import re

from ..dldbase import componentstate
from ..dldbase import componentstate as cs
from ..dldbase.componentstate import ComponentStateReaderWriter, ComponentState

TEST_STATE_DIR = osp.join(osp.dirname(osp.realpath(__file__)), 'dld-component-states')
TEST_LOG = logging.getLogger('dld.base.tests')

def dir_patched_csrw(state_dir=TEST_STATE_DIR):
    class Patched(ComponentStateReaderWriter):
        @classmethod
        def _state_dir(cls):
            return state_dir

    return Patched


def test_get_state_succeeds_when_unlocked():
    csrw = dir_patched_csrw()('store-ready')
    csrw.get_state().should.equal('ready')

def test_get_state_fails_when_permanent_write_lock_in_place():
    csrw = dir_patched_csrw()('store-transient')
    csrw.get_state.when.called_with().should.throw(RuntimeError, re.compile('timeout after \d+ retries to read state'))

def test_write_state_succeeds_when_unlocked():
    test_name = 'test_write_state_succeeds_when_unlocked'
    state_dir_tmp = tempfile.mkdtemp(prefix="dld-csrw-test-")
    comp_state_dir = osp.join(state_dir_tmp, 'store-init')
    try:
        TEST_LOG.debug("created temp. dir {td} for {tn}".format(td=state_dir_tmp, tn=test_name))
        shutil.copytree(osp.join(TEST_STATE_DIR, 'store-init'), comp_state_dir)
        csrw = dir_patched_csrw(state_dir_tmp)('store-init')
        csrw.update_state('ready', old_state='init')
        with open(osp.join(comp_state_dir, cs.STATE_LOG)) as log_fd:
            log_lines = log_fd.readlines()
        len(log_lines).should.equal(1)
        (log_lines[-1]).should.match(r'init\s+->\s+ready')
    finally:
        print("look in: {p}".format(p=state_dir_tmp))
        shutil.rmtree(state_dir_tmp, ignore_errors=True)
