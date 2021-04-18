"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-17 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

from contextlib import contextmanager
import threading


class read_write_lock():
    """
    :Author: Daniel Mohr
    :Date: 2021-04-17
    """
    def __init__(self):
        self.write_lock = threading.Lock()
        self.read_lock = threading.Lock()
        self.block_read_lock = threading.Lock()
        self.value = 0

    def acquire_read(self):
        self.block_read_lock.acquire()
        self.read_lock.acquire()
        self.value += 1
        if self.value == 1:
            self.write_lock.acquire()
        self.read_lock.release()
        self.block_read_lock.release()

    def release_read(self):
        assert self.value > 0
        self.read_lock.acquire()
        self.value -= 1
        if self.value == 0:
            self.write_lock.release()
        self.read_lock.release()

    @contextmanager
    def read_locked(self):
        """
        Example::

          from .read_write_lock import read_write_lock
          lock = read_write_lock()
          locked_data = 'foo'
          with self.lock.read_locked():
              print(locked_data)
        """
        try:
            self.acquire_read()
            yield
        finally:
            self.release_read()

    def acquire_write(self):
        self.block_read_lock.acquire()
        self.write_lock.acquire()
        self.block_read_lock.release()

    def release_write(self):
        self.write_lock.release()

    @contextmanager
    def write_locked(self):
        """
        Example::

          from .read_write_lock import read_write_lock
          lock = read_write_lock()
          locked_data = 'foo'
          with self.lock.write_locked():
              locked_data = 'bar'
        """
        try:
            self.acquire_write()
            yield
        finally:
            self.release_write()
