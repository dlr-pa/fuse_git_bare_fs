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
import os
import os.path
import re
import threading
import time

from .empty_attr_mixin import _empty_attr_mixin
from .repo_class import RepoClass
from .read_write_lock import ReadWriteLock
from .simple_file_cache import SimpleFileCache
from .simple_file_handler import simple_file_handler_class



def _extract_repopath_from_path(actual_repo, path):
    repopath = path[1+len(actual_repo):]
    if not bool(repopath):
        repopath = '/'
    return repopath

class _GitBareRepoTreeMixin(_empty_attr_mixin):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-24

    read only access to working trees of git bare repositories
    """
    # pylint: disable=too-many-instance-attributes
    # /usr/lib/python3/dist-packages/fusepy.py

    def __init__(self, src_dir, root_object, max_cache_size,
                 simple_file_handler=None):
        self.src_dir = src_dir
        self.root_object = root_object
        self.cache = SimpleFileCache(max_cache_size=max_cache_size)
        if simple_file_handler is None:
            self.simple_file_handler = simple_file_handler_class()
        else:
            self.simple_file_handler = simple_file_handler
        self.repos = dict()
        self._lock = ReadWriteLock()
        dt0 = time.time()
        with self._lock.write_locked():
            self.repos = self._get_repos()
        self._update_repos_time = time.time()
        self._update_repos_dt = max(6, (self._update_repos_time - dt0) * 100)

    def _del_(self):
        self._lock.acquire_write()
        del self.repos

    def _update_repos(self):
        if time.time() - self._update_repos_time > self._update_repos_dt:
            dt0 = time.time()
            repos = self._get_repos()
            with self._lock.write_locked():
                for reponame in repos:  # add new found repos
                    if reponame not in self.repos:
                        self.repos[reponame] = repos[reponame]
                for reponame in list(self.repos.keys()):
                    # remove obsolete repos
                    if reponame not in repos:
                        del self.repos[reponame]
            self._update_repos_time = time.time()
            self._update_repos_dt = max(
                6, (self._update_repos_time - dt0) * 100)

    def _get_repos(self):
        """
        self._lock has to have the write lock, e. g.::

          self._lock.acquire_write()
          ...
          self._lock.release_write()
        """
        repos = dict()
        for dirpath, dirnames, _ in os.walk(self.src_dir):
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
        self._lock has to have the read lock, e. g.::

          self._lock.acquire_read()
          ...
          self._lock.release_read()
        """
        actual_repo = None
        for repo in self.repos:
            res = re.findall(r'^\/' + repo + r'$|^\/' + repo + r'\/', path)
            if res:
                actual_repo = repo
                break
        return actual_repo

    def getattr(self, path, file_handler=None):
        """
        get attributes of the path

        The argument file_handler is not used, but can be given to be
        compatible to typical getattr functions.
        """
        # pylint: disable=unused-argument
        if path == '/':
            return self._empty_dir_attr
        self._update_repos()
        self._lock.acquire_read()
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # check if path is part of repo path
            part_of_repo_path = False
            for repo in self.repos:
                if repo.startswith(path[1:]):
                    part_of_repo_path = True
                    break
            if part_of_repo_path:
                self._lock.release_read()
                return self._empty_dir_attr
            else:  # no such file or directory
                self._lock.release_read()
                raise fusepy.FuseOSError(errno.ENOENT)
        actual_repo_list = self.repos[actual_repo]
        self._lock.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = RepoClass(
                os.path.join(self.src_dir, actual_repo_list[0]),
                root_object=self.root_object, cache=self.cache,
                simple_file_handler=self.simple_file_handler)
        ret = actual_repo_list[1].getattr(
            _extract_repopath_from_path(actual_repo, path))
        return ret

    def read(self, path, size, offset, file_handler):
        """
        read parts of path
        """
        self._update_repos()
        self._lock.acquire_read()
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # no such file or directory
            self._lock.release_read()
            raise fusepy.FuseOSError(errno.ENOENT)
        actual_repo_list = self.repos[actual_repo]
        self._lock.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = RepoClass(
                os.path.join(self.src_dir, actual_repo_list[0]),
                root_object=self.root_object, cache=self.cache,
                simple_file_handler=self.simple_file_handler)
        ret = actual_repo_list[1].read(
            _extract_repopath_from_path(actual_repo, path),
            size, offset, file_handler)
        return ret

    def readdir(self, path, file_handler):
        """
        read the directory path

        The argument file_handler is not used, but can be given to be
        compatible to typical readdir functions.
        """
        # pylint: disable=unused-argument
        # /foo/bar.git/baz
        self._update_repos()
        self._lock.acquire_read()
        if path == '/':
            retlist = ['.', '..']
            for repo in self.repos:
                retlist.append(repo.split('/')[0])
            self._lock.release_read()
            return list(set(retlist))
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # check if path is part of repo path
            repos = ['.', '..']
            for repo in self.repos:
                res = re.findall(
                    r'^' + path + r'$|^' + path + r'\/([^\/]+)', '/' + repo)
                if res:
                    repos.append(res[0])
            if bool(repos):  # path is part of repo path
                self._lock.release_read()
                return list(set(repos))
            else:  # no such file or directory
                self._lock.release_read()
                raise fusepy.FuseOSError(errno.ENOENT)
        actual_repo_list = self.repos[actual_repo]
        self._lock.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = RepoClass(
                os.path.join(self.src_dir, actual_repo_list[0]),
                root_object=self.root_object, cache=self.cache,
                simple_file_handler=self.simple_file_handler)
        ret = actual_repo_list[1].readdir(
            _extract_repopath_from_path(actual_repo, path))
        return ret

    def readlink(self, path):
        """
        read the symbolic link path
        """
        self._update_repos()
        self._lock.acquire_read()
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # no such file or directory
            self._lock.release_read()
            raise fusepy.FuseOSError(errno.ENOENT)
        actual_repo_list = self.repos[actual_repo]
        self._lock.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = RepoClass(
                os.path.join(self.src_dir, actual_repo_list[0]),
                root_object=self.root_object, cache=self.cache,
                simple_file_handler=self.simple_file_handler)
        file_handler = self.open(path, 'r')
        ret = actual_repo_list[1].read(
            _extract_repopath_from_path(actual_repo, path),
            None, 0, file_handler).decode()
        self.release(path, file_handler)
        return ret

    def open(self, path, flags):
        """
        Creates a lock on path and return it as a file handler.
        Only open as read is supported, but this is not checked.

        This lock will be destroyed, if the repository is changed or it is
        released.
        """
        self._update_repos()
        self._lock.acquire_read()
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # no such file or directory
            self._lock.release_read()
            raise fusepy.FuseOSError(errno.ENOENT)
        actual_repo_list = self.repos[actual_repo]
        self._lock.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = RepoClass(
                os.path.join(self.src_dir, actual_repo_list[0]),
                root_object=self.root_object, cache=self.cache,
                simple_file_handler=self.simple_file_handler)
        return actual_repo_list[1].open(
            _extract_repopath_from_path(actual_repo, path), flags)

    def release(self, path, file_handler):
        """
        Releases the lock file_fandler on path.
        """
        self._update_repos()
        self._lock.acquire_read()
        actual_repo = self._extract_repo_from_path(path)
        if actual_repo is None:  # no such file or directory
            self._lock.release_read()
            raise fusepy.FuseOSError(errno.ENOENT)
        actual_repo_list = self.repos[actual_repo]
        self._lock.release_read()
        if actual_repo_list[1] is None:
            actual_repo_list[1] = RepoClass(
                os.path.join(self.src_dir, actual_repo_list[0]),
                root_object=self.root_object, cache=self.cache,
                simple_file_handler=self.simple_file_handler)
        actual_repo_list[1].release(
            _extract_repopath_from_path(actual_repo, path), file_handler)

    def utimens(self, path, times=None):
        """
        This is not implemented at the moment.

        The arguments are not used, but can be given to be compatible to
        typical open functions.
        """
        # pylint: disable=unused-argument,no-self-use
        raise fusepy.FuseOSError(errno.EROFS)


class git_bare_repo_tree(
        _GitBareRepoTreeMixin, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """


class git_bare_repo_tree_logging(
        _GitBareRepoTreeMixin, fusepy.LoggingMixIn, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """
