"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-13 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import errno
import fusepy  # https://github.com/fusepy/fusepy
import os
import os.path
import re

from .empty_attr_mixin import _empty_attr_mixin
from .repo_class import repo_class


class _git_bare_repo_tree_mixin(_empty_attr_mixin):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to working trees of git bare repositories
    """
    # /usr/lib/python3/dist-packages/fusepy.py
    find_git_repo = re.compile('(.*.git)(.*)')

    def __init__(self, src_dir, root_object):
        self.src_dir = src_dir
        self.root_object = root_object
        self.repos = dict()

    def getattr(self, path, fh=None):
        # /foo/bar.git/baz
        pathsplitted = self.find_git_repo.findall(path)
        if pathsplitted:
            actual_repo = pathsplitted[0][0][1:][:-4]
            if not actual_repo in self.repos:
                self.repos[actual_repo] = repo_class(
                    os.path.join(self.src_dir, actual_repo) + '.git',
                    self.root_object)
            repopath = pathsplitted[0][1]
            if len(repopath) == 0:
                repopath = '/'
            return self.repos[actual_repo].getattr(repopath)
        else:
            return self._empty_dir_attr

    def read(self, path, size, offset, fh):
        # /foo/bar.git/baz
        pathsplitted = self.find_git_repo.findall(path)
        if pathsplitted:
            actual_repo = pathsplitted[0][0][1:]
            if not actual_repo in self.repos:
                self.repos[actual_repo] = repo_class(
                    os.path.join(self.src_dir, actual_repo) + '.git',
                    self.root_object)
            return self.repos[actual_repo].read(
                pathsplitted[0][1], size, offset)
        else:
            # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        # /foo/bar.git/baz
        if path == '/':
            return os.listdir(os.path.join(self.src_dir, path[1:]))
        pathsplitted = self.find_git_repo.findall(path)
        if pathsplitted:
            actual_repo = pathsplitted[0][0][1:]
            if not actual_repo in self.repos:
                self.repos[actual_repo] = repo_class(
                    os.path.join(self.src_dir, actual_repo),
                    self.root_object)
            return self.repos[actual_repo].readdir(
                '/' + pathsplitted[0][1])
        elif os.path.isdir(os.path.join(self.src_dir, path[1:])):
            return os.listdir(os.path.join(self.src_dir, path[1:]))
        else:
            # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)

    def readlink(self, path):
        # /foo/bar.git/baz
        pathsplitted = self.find_git_repo.findall(path)
        if pathsplitted:
            actual_repo = pathsplitted[0][0][1:]
            if not actual_repo in self.repos:
                self.repos[actual_repo] = repo_class(
                    os.path.join(self.src_dir, actual_repo) + '.git',
                    self.root_object)
            return self.repos[actual_repo].read(
                pathsplitted[0][1], None, 0).decode()
        else:
            # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)


class git_bare_tree_repo(
        _git_bare_repo_tree_mixin, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """


class git_bare_repo_tree_logging(
        _git_bare_repo_tree_mixin, fusepy.LoggingMixIn, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """
