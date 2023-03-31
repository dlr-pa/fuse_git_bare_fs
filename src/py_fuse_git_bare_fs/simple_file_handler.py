"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-29 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import errno
try:
    import fusepy  # https://github.com/fusepy/fusepy
except ModuleNotFoundError:
    import fuse as fusepy

from .read_write_lock import ReadWriteLock


class SimpleFileHandlerClass():
    """
    :Author: Daniel Mohr
    :Date: 2021-04-24
    """

    def __init__(self, max_file_handlers=1024):
        """
        :param max_file_handlers: maximum number of file handlers
        """
        if max_file_handlers >= 2147483647:
            raise ValueError
        self.max_file_handlers = max_file_handlers
        self.lock = ReadWriteLock()
        with self.lock.write_locked():
            self.next_file_handler_number = 0
            self.file_handler = []
            self.file_handler_repo = {}

    def get(self, repo):
        """
        Use this method to get a file handler.

        It is used in an open command.
        """
        if len(self.file_handler) >= self.max_file_handlers:
            raise fusepy.FuseOSError(errno.EMFILE)
        i = None
        with self.lock.write_locked():
            if repo in self.file_handler_repo:
                pass
            else:
                self.file_handler_repo[repo] = []
            i = self.next_file_handler_number
            while i in self.file_handler:
                i += 1
                if i >= 2147483646:
                    i = 0
            self.file_handler_repo[repo].append(i)
            self.file_handler.append(i)
            self.next_file_handler_number = i + 1
        return i

    def remove(self, repo, i):
        """
        Use this method to remove a file handler.

        It is used in a release/close command.
        """
        with self.lock.write_locked():
            if ((repo in self.file_handler_repo) and
                    (i in self.file_handler_repo[repo])):
                self.file_handler_repo[repo].pop(
                    self.file_handler_repo[repo].index(i))
            if i in self.file_handler:
                self.file_handler.pop(
                    self.file_handler.index(i))
            else:
                raise fusepy.FuseOSError(errno.EBADF)

    def is_file_handler(self, repo, i):
        """
        This method allows to check if the file handler i is still valid.
        """
        ret = False
        with self.lock.read_locked():
            if ((repo in self.file_handler_repo) and
                    (i in self.file_handler_repo[repo])):
                ret = True
        return ret

    def remove_repo(self, repo):
        """
        This method removes all file handlers belonging to the repository repo.
        """
        with self.lock.write_locked():
            if repo in self.file_handler_repo:
                for i in self.file_handler_repo[repo]:
                    if i in self.file_handler:
                        self.file_handler.pop(
                            self.file_handler.index(i))
                del self.file_handler_repo[repo]
