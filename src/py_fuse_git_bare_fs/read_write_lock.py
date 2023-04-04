"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-17, 2023-04-03 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

from contextlib import contextmanager
import threading


class ReadWriteLock():
    """
    :Author: Daniel Mohr
    :Date: 2021-04-17, 2023-04-03
    """

    def __init__(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-17

        ReadWriteLock is a class to provide combined lock mechanism for
        a read and a write.

        The write is only possible for one thread and only if no read is
        locked.

        The read is only possible, when no write is locked. It is possbile
        to read from many threads parallel.
        """
        self.write_lock = threading.Lock()
        self.read_lock = threading.Lock()
        self.block_read_lock = threading.Lock()
        self.value = 0

    def acquire_read(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-17, 2023-04-03

        Locks a read.
        """
        with self.block_read_lock:
            with self.read_lock:
                self.value += 1
                if self.value == 1:
                    # pylint: disable=consider-using-with
                    self.write_lock.acquire()

    def release_read(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-17, 2023-04-03

        Release a read.
        """
        assert self.value > 0
        with self.read_lock:
            self.value -= 1
            if self.value == 0:
                self.write_lock.release()

    @contextmanager
    def read_locked(self):
        """
        Example::

          from .read_write_lock import ReadWriteLock
          lock = ReadWriteLock()
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
        """
        :Author: Daniel Mohr
        :Date: 2021-04-17, 2023-04-03

        Locks a write.
        """
        with self.block_read_lock:
            # pylint: disable=consider-using-with
            self.write_lock.acquire()

    def release_write(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-17

        Release a write.
        """
        self.write_lock.release()

    @contextmanager
    def write_locked(self):
        """
        Example::

          from .read_write_lock import ReadWriteLock
          lock = ReadWriteLock()
          locked_data = 'foo'
          with self.lock.write_locked():
              locked_data = 'bar'
        """
        try:
            self.acquire_write()
            yield
        finally:
            self.release_write()
