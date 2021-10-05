"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-05 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import errno
import sys
import warnings

from .repo_class import RepoClass
from .simple_file_handler import SimpleFileHandlerClass

try:
    import fusepy  # https://github.com/fusepy/fusepy
except ModuleNotFoundError:
    import fuse as fusepy


class _GitBareRepoMixin():
    """
    :Author: Daniel Mohr
    :Date: 2021-10-05

    read only access to the working tree of a git bare repository
    """
    # pylint: disable=too-many-arguments
    # /usr/lib/python3/dist-packages/fusepy.py

    # disable unused operations to avoid unnecessary errors:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    opendir = None
    releasedir = None
    statfs = None
    # we only use/provide:
    #  getattr
    #  read
    #  readdir
    #  readlink
    #  open
    #  release
    #  utimens

    def __init__(self, src_dir, root_object, max_cache_size,
                 simple_file_handler=None, nofail=False):
        self.src_dir = src_dir
        self.root_object = root_object
        if simple_file_handler is None:
            self.simple_file_handler = SimpleFileHandlerClass()
        else:
            self.simple_file_handler = simple_file_handler
        self.nofail = nofail
        if self.nofail:
            # pylint: disable=broad-except
            try:
                self.repo = RepoClass(
                    self.src_dir, self.root_object,
                    max_cache_size=max_cache_size,
                    simple_file_handler=self.simple_file_handler)
            except Exception:
                msg = 'mount fail, '
                msg += 'try running without "-nofail" to get precise error'
                warnings.warn(msg)
                sys.exit(0)
        else:
            self.repo = RepoClass(
                self.src_dir, self.root_object, max_cache_size=max_cache_size,
                simple_file_handler=self.simple_file_handler)

    def __del__(self):
        if hasattr(self, 'simple_file_handler'):
            self.simple_file_handler.remove_repo(self.src_dir)

    def getattr(self, path, file_handler=None):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        get attributes of the path

        The argument file_handler is not used, but can be given to be
        compatible to typical getattr functions.
        """
        # pylint: disable=unused-argument
        return self.repo.getattr(path)

    def read(self, path, size, offset, file_handler):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        read parts of path
        """
        if not self.simple_file_handler.is_file_handler(self.src_dir,
                                                        file_handler):
            raise fusepy.FuseOSError(errno.EBADF)
        return self.repo.read(path, size, offset, file_handler)

    def readdir(self, path, file_handler):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        read the directory path

        The argument file_handler is not used, but can be given to be
        compatible to typical readdir functions.
        """
        # pylint: disable=unused-argument
        return self.repo.readdir(path)

    def readlink(self, path):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        read the symbolic link path
        """
        file_handler = self.open(path, 'r')
        ret = self.repo.read(path, None, 0, file_handler).decode()
        self.release(path, file_handler)
        return ret

    def open(self, path, flags):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        Creates a lock on path and return it as a file handler.
        Only open as read is supported, but this is not checked.

        This lock will be destroyed, if the repository is changed or it is
        released.

        The arguments are not used, but can be given to be compatible to
        typical open functions.
        """
        # pylint: disable=unused-argument
        return self.simple_file_handler.get(self.src_dir)

    def release(self, path, file_handler):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        Releases the lock file_fandler on path.

        The argument path is not used, but can be given to be compatible to
        typical release functions.
        """
        # pylint: disable=unused-argument
        self.simple_file_handler.remove(self.src_dir, file_handler)

    def utimens(self, path, times=None):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        This is not implemented at the moment.

        The arguments are not used, but can be given to be compatible to
        typical open functions.
        """
        # pylint: disable=unused-argument,no-self-use
        raise fusepy.FuseOSError(errno.EROFS)


class GitBareRepo(
        _GitBareRepoMixin, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """


class GitBareRepoLogging(
        _GitBareRepoMixin, fusepy.LoggingMixIn, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository

    The fusepy.LoggingMixIn is used to provide verbose output.
    """
