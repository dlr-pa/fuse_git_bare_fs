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

from .repo_class import repo_class
from .simple_file_handler import simple_file_handler_class


class _git_bare_repo_mixin():
    """
    :Author: Daniel Mohr
    :Date: 2021-04-24

    read only access to the working tree of a git bare repository
    """
    # /usr/lib/python3/dist-packages/fusepy.py

    def __init__(self, src_dir, root_object, max_cache_size,
                 simple_file_handler=None):
        self.src_dir = src_dir
        self.root_object = root_object
        if simple_file_handler is None:
            self.simple_file_handler = simple_file_handler_class()
        else:
            self.simple_file_handler = simple_file_handler
        self.repo = repo_class(
            self.src_dir, self.root_object, max_cache_size=max_cache_size,
            simple_file_handler=self.simple_file_handler)

    def __del__(self):
        if hasattr(self, 'simple_file_handler'):
            self.simple_file_handler.remove_repo(self.src_dir)

    def getattr(self, path, fh=None):
        return self.repo.getattr(path)

    def read(self, path, size, offset, fh):
        if not self.simple_file_handler.is_file_handler(self.src_dir, fh):
            raise fusepy.FuseOSError(errno.EBADF)
        return self.repo.read(path, size, offset, fh)

    def readdir(self, path, fh):
        return self.repo.readdir(path)

    def readlink(self, path):
        fh = self.open(path, 'r')
        ret = self.repo.read(path, None, 0, fh).decode()
        self.release(path, fh)
        return ret

    def open(self, path, flags):
        return self.simple_file_handler.get(self.src_dir)

    def release(self, path, fh):
        self.simple_file_handler.remove(self.src_dir, fh)

    def utimens(self, path, times=None):
        raise fusepy.FuseOSError(errno.EROFS)


class git_bare_repo(
        _git_bare_repo_mixin, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """


class git_bare_repo_logging(
        _git_bare_repo_mixin, fusepy.LoggingMixIn, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """
