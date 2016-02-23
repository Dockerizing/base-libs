import sys
import os
import shutil
from os import environ as env
from os import path as osp
from collections import namedtuple
import functools
import datetime
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, Future


from . import DLD_NAME_SUFFIX, DLD_STATE_DIR

_RETRY_NEEDED = object()
COMPONENT_LOG = logging.getLogger('dld.componentstate')
STATE_CURRENT = 'state.current'
STATE_NEXT = 'state.next'
STATE_READ = 'state.read'
STATE_LOG = 'state.log'

class LockFile(object):
    def __init__(self, path, content=None, ignore_exists=True, ignore_removed=True):
        self.path = path
        self.content = content
        self.ignore_exists = ignore_exists
        self.ignore_removed = ignore_removed

    def __enter__(self):
        if osp.isfile(self.path):
            if self.ignore_exists:
                return self.path
            else:
                raise RuntimeError("requested lock file already exists: {p}".format(p=self.path))

        with open(self.path, 'w') as fd:
            os.utime(self.path, None)
            if self.content:
                fd.write(self.content.strip())
                fd.write('\n')
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            os.remove(self.path)
        except OSError as ose:
            if ose.errno != 2 or (not self.ignore_removed):
                raise ose

class ComponentStateReaderWriter(object):
    def __init__(self, component_name):
        self.component_name = component_name
        self.state_dir = osp.join(self._state_dir(), component_name)

    @staticmethod
    def known_components():
        names = [e[1] for e in env.items() if e[0].endswith(DLD_NAME_SUFFIX)]
        return frozenset(names)

    @classmethod
    def _state_dir(cls):
        return DLD_STATE_DIR

    def _ensure_state_dir(self):
        if not osp.isdir(self.state_dir):
            raise RuntimeError("missing component state dir: {d}".format(d=self.state_dir))

    def _new_state_pending(self):
        return STATE_NEXT in os.listdir(self.state_dir)

    def _state_reading(self):
        return STATE_READ in os.listdir(self.state_dir)

    def _read_current_state(self):
        try:
            with open(osp.join(self.state_dir, STATE_CURRENT)) as fd:
                return fd.readline().strip()
        except OSError:
            return None


    def get_state(self):
        def attempt():
            self._ensure_state_dir()
            if self._new_state_pending():
                return _RETRY_NEEDED
            else:
                with LockFile(osp.join(self.state_dir, STATE_READ)):
                    if self._new_state_pending():
                        return _RETRY_NEEDED
                    else:
                        return self._read_current_state()

        for retry in range(0,41):
            if retry > 0 and (retry % 4) == 1:
                COMPONENT_LOG.debug("retry {n} for reading state for {c}".format(n=retry, c=self.component_name))
                time.sleep(0.01)
            state_result = attempt()
            if state_result is _RETRY_NEEDED:
                continue
            else:
                return state_result

        raise RuntimeError("timeout after {n} retries to read state of component '{c}'"
                           .format(n=retry, c= self.component_name))

    def update_state(self, new_state, old_state=None):
        current_path = osp.join(self.state_dir, STATE_CURRENT)
        next_path = osp.join(self.state_dir, STATE_NEXT)
        log_path = osp.join(self.state_dir, STATE_LOG)

        def attempt():
            self._ensure_state_dir()
            current_state = self._read_current_state() or '[[NA]]]'
            if self._state_reading() or self._new_state_pending():
                return _RETRY_NEEDED
            elif old_state is not None:
                 if current_state != old_state.strip():
                        raise RuntimeError("concurrent state modification")

            with LockFile(next_path, content=new_state, ignore_exists=False):
                with open(log_path, 'a') as log_fd:
                    os.rename(next_path, current_path)
                    log_fd.writelines(["{t} {prev} -> {new}"
                                      .format(t=datetime.datetime.now(), prev=current_state, new=new_state)])


        for retry in range(0,41):
            if retry > 0 and (retry % 4) == 1:
                COMPONENT_LOG.debug("retry {n} for writing state for {c}".format(n=retry, c=self.component_name))
                time.sleep(0.01)
            if attempt() is not _RETRY_NEEDED:
                return

        raise RuntimeError("timeout after {n} retries to write state of component '{c}'"
                           .format(n=retry, c= self.component_name))


    


class ComponentState(namedtuple('ComponentState', 'component_name state_str access_time')):
    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        return namedtuple.__new__(cls, *args + (datetime.datetime.now(), ), **kwargs)

