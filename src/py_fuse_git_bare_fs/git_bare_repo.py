"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-13 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import fusepy  # https://github.com/fusepy/fusepy

from .repo_class import repo_class


class _git_bare_repo_mixin():
    """
    :Author: Daniel Mohr
    :Date: 2021-04-08

    read only access to the working tree of a git bare repository
    """
    # /usr/lib/python3/dist-packages/fusepy.py

    def __init__(self, src_dir, root_object):
        self.src_dir = src_dir
        self.root_object = root_object
        self.repo = repo_class(self.src_dir, self.root_object)

    def getattr(self, path, fh=None):
        return self.repo.getattr(path)

    def read(self, path, size, offset, fh):
        return self.repo.read(path, size, offset)

    def readdir(self, path, fh):
        return ['.', '..'] + self.repo.readdir(path)

    def readlink(self, path):
        return self.repo.read(path, None, 0).decode()


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
