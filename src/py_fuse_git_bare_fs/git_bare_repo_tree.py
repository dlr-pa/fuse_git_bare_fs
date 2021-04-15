"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-15 (last change).
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
        # list
        self.repos = self._get_repos()

    def _get_repos(self):
        repos = dict()
        for dirpath, dirnames, filenames in os.walk(self.src_dir):
            for dirname in dirnames:
                if dirname.endswith('.git'):
                    if dirname == '.git':
                        reposrcname = dirpath[1 + len(self.src_dir):]
                        repos[reposrcname] = [reposrcname, None]
                        break
                    else:
                        reposrcname = os.path.join(
                            dirpath, dirname)[1 + len(self.src_dir):]
                        reponame = reposrcname[:-4]
                        repos[reponame] = [reposrcname, None]
        return repos

    def _extract_repo_from_path(self, path):
        actual_repo = None
        for repo in self.repos.keys():
            if path.startswith('/' + repo):
                actual_repo = repo
                break
        return actual_repo

    def _extract_repopath_from_path(self, actual_repo, path):
        repopath = path[1+len(actual_repo):]
        if len(repopath) == 0:
            repopath = '/'
        return repopath

    def getattr(self, path, fh=None):
        if path == '/':
            return self._empty_dir_attr
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # check if path is part of repo path
            part_of_repo_path = False
            for repo in self.repos.keys():
                if repo.startswith(path[1:]):
                    part_of_repo_path = True
                    break
            if part_of_repo_path:
                return self._empty_dir_attr
            else:  # no such file or directory
                raise fusepy.FuseOSError(errno.ENOENT)
        if self.repos[actual_repo][1] is None:
            self.repos[actual_repo][1] = repo_class(
                os.path.join(self.src_dir, self.repos[actual_repo][0]),
                self.root_object)
        return self.repos[actual_repo][1].getattr(
            self._extract_repopath_from_path(actual_repo, path))

    def read(self, path, size, offset, fh):
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        if self.repos[actual_repo][1] is None:
            self.repos[actual_repo][1] = repo_class(
                os.path.join(self.src_dir, self.repos[actual_repo][0]),
                self.root_object)
        return self.repos[actual_repo][1].read(
            self._extract_repopath_from_path(actual_repo, path),
            size, offset)

    def readdir(self, path, fh):
        # /foo/bar.git/baz
        if path == '/':
            retlist = []
            for repo in self.repos.keys():
                retlist.append(repo.split('/')[0])
            return list(set(retlist))
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # check if path is part of repo path
            repos = []
            for repo in self.repos.keys():
                if repo.startswith(path[1:]):
                    repos.append(repo[1+len(path[1:]):].split('/')[0])
            if len(repos) > 0:  # path is part of repo path
                return list(set(repos))
            else:  # no such file or directory
                raise fusepy.FuseOSError(errno.ENOENT)
        if self.repos[actual_repo][1] is None:
            self.repos[actual_repo][1] = repo_class(
                os.path.join(self.src_dir, self.repos[actual_repo][0]),
                self.root_object)
        return self.repos[actual_repo][1].readdir(
            self._extract_repopath_from_path(actual_repo, path))

    def readlink(self, path):
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        if self.repos[actual_repo][1] is None:
            self.repos[actual_repo][1] = repo_class(
                os.path.join(self.src_dir, self.repos[actual_repo][0]),
                self.root_object)
        return self.repos[actual_repo][1].read(
            self._extract_repopath_from_path(actual_repo, path),
            None, 0).decode()


class git_bare_repo_tree(
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
