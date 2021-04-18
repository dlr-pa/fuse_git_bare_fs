"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-18 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import errno
import fusepy  # https://github.com/fusepy/fusepy
import os
import os.path
import re

from .empty_attr_mixin import _empty_attr_mixin
from .repo_class import repo_class
from .read_write_lock import read_write_lock


class _git_bare_repo_tree_mixin(_empty_attr_mixin):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-18

    read only access to working trees of git bare repositories
    """
    # /usr/lib/python3/dist-packages/fusepy.py

    def __init__(self, src_dir, root_object):
        self.src_dir = src_dir
        self.root_object = root_object
        # list
        self.locks = read_write_lock()
        with self.locks.write_locked():
            self.repos = self._get_repos()

    def _get_repos(self):
        """
        self.locks has to have the write lock, e. g.::

          self.locks.acquire_write()
          ...
          self.locks.release_write()
        """
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
        """
        self.locks has to have the read lock, e. g.::

          self.locks.acquire_read()
          ...
          self.locks.release_read()
        """
        actual_repo = None
        for repo in self.repos.keys():
            res = re.findall('^\/' + repo + '$|^\/' + repo + '\/', path)
            if res:
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
        self.locks.acquire_read()
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # check if path is part of repo path
            part_of_repo_path = False
            for repo in self.repos.keys():
                if repo.startswith(path[1:]):
                    part_of_repo_path = True
                    break
            if part_of_repo_path:
                self.locks.release_read()
                return self._empty_dir_attr
            else:  # no such file or directory
                self.locks.release_read()
                raise fusepy.FuseOSError(errno.ENOENT)
        # from here on we only need self.repos[actual_repo]
        # and not self.repos

        # if self.repos[actual_repo][1] is None:
        #    self.repos[actual_repo][1] = repo_class(
        #        os.path.join(self.src_dir, self.repos[actual_repo][0]),
        #        self.root_object)
        # ret = self.repos[actual_repo][1].getattr(
        #    self._extract_repopath_from_path(actual_repo, path))
        # self.locks.release_read()

        actual_repo_list = self.repos[actual_repo]
        self.locks.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = repo_class(
                os.path.join(self.src_dir, actual_repo_list[0]),
                self.root_object)
        ret = actual_repo_list[1].getattr(
            self._extract_repopath_from_path(actual_repo, path))
        return ret

    def read(self, path, size, offset, fh):
        self.locks.acquire_read()
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # no such file or directory
            self.locks.release_read()
            raise fusepy.FuseOSError(errno.ENOENT)

        # from here on we only need self.repos[actual_repo]
        # and not self.repos

        # if self.repos[actual_repo][1] is None:
        #    self.repos[actual_repo][1] = repo_class(
        #        os.path.join(self.src_dir, self.repos[actual_repo][0]),
        #        self.root_object)
        # ret = self.repos[actual_repo][1].read(
        #    self._extract_repopath_from_path(actual_repo, path),
        #    size, offset)
        # self.locks.release_read()

        actual_repo_list = self.repos[actual_repo]
        self.locks.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = repo_class(
                os.path.join(self.src_dir, actual_repo_list[0]),
                self.root_object)
        ret = actual_repo_list[1].read(
            self._extract_repopath_from_path(actual_repo, path),
            size, offset)
        return ret

    def readdir(self, path, fh):
        # /foo/bar.git/baz
        self.locks.acquire_read()
        if path == '/':
            retlist = []
            for repo in self.repos.keys():
                retlist.append(repo.split('/')[0])
            self.locks.release_read()
            return list(set(retlist))
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # check if path is part of repo path
            repos = []
            for repo in self.repos.keys():
                res = re.findall(
                    '^' + path + '$|^' + path + '\/([^\/]+)', '/' + repo)
                if res:
                    repos.append(res[0])
            if len(repos) > 0:  # path is part of repo path
                self.locks.release_read()
                return list(set(repos))
            else:  # no such file or directory
                self.locks.release_read()
                raise fusepy.FuseOSError(errno.ENOENT)
        # from here on we only need self.repos[actual_repo]
        # and not self.repos

        # if self.repos[actual_repo][1] is None:
        #    self.repos[actual_repo][1] = repo_class(
        #        os.path.join(self.src_dir, self.repos[actual_repo][0]),
        #        self.root_object)
        # ret = self.repos[actual_repo][1].readdir(
        #    self._extract_repopath_from_path(actual_repo, path))
        # self.locks.release_read()

        actual_repo_list = self.repos[actual_repo]
        self.locks.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = repo_class(
                os.path.join(self.src_dir, actual_repo_list[0]),
                self.root_object)
        ret = actual_repo_list[1].readdir(
            self._extract_repopath_from_path(actual_repo, path))
        return ret

    def readlink(self, path):
        self.locks.acquire_read()
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # no such file or directory
            self.locks.release_read()
            raise fusepy.FuseOSError(errno.ENOENT)

        # from here on we only need self.repos[actual_repo]
        # and not self.repos

        # if self.repos[actual_repo][1] is None:
        #    self.repos[actual_repo][1] = repo_class(
        #        os.path.join(self.src_dir, self.repos[actual_repo][0]),
        #        self.root_object)
        # ret = self.repos[actual_repo][1].read(
        #    self._extract_repopath_from_path(actual_repo, path),
        #    None, 0).decode()
        # self.locks.release_read()

        actual_repo_list = self.repos[actual_repo]
        self.locks.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = repo_class(
                os.path.join(self.src_dir, actual_repo_list[0]),
                self.root_object)
        ret = actual_repo_list[1].read(
            self._extract_repopath_from_path(actual_repo, path),
            None, 0).decode()
        return ret


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
