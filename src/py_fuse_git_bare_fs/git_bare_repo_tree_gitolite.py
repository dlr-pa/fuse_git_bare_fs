"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-06-17 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import errno
try:
    import fusepy  # https://github.com/fusepy/fusepy
except ModuleNotFoundError:
    import fuse as fusepy
import os.path
import re

from .empty_attr_mixin import _EmptyAttrMixin
from .user_repos import UserRepos
from .simple_file_handler import SimpleFileHandlerClass


def _extract_repopath_from_path(actual_user, actual_repo, path):
    repopath = path[2+len(actual_user)+len(actual_repo):]
    if not bool(repopath):
        repopath = '/'
    return repopath


class _GitBareRepoTreeGitoliteMixin(_EmptyAttrMixin):
    """
    :Author: Daniel Mohr
    :Date: 2021-06-17

    read only access to working trees of git bare repositories
    """

    def __init__(self, src_dir, root_object, provide_htaccess,
                 htaccess_template=None,
                 gitolite_cmd='gitolite', gitolite_user_file=None,
                 max_cache_size=1073741824,
                 simple_file_handler=None):
        # pylint: disable=too-many-arguments
        self.src_dir = src_dir
        self.root_object = root_object
        self.provide_htaccess = provide_htaccess
        self.htaccess_template = b''
        if htaccess_template is not None:
            with open(htaccess_template, 'rb') as fd:
                self.htaccess_template = fd.read()
        if simple_file_handler is None:
            self.simple_file_handler = SimpleFileHandlerClass()
        else:
            self.simple_file_handler = simple_file_handler
        self.repos = UserRepos(src_dir, self.root_object,
                               gitolite_cmd, gitolite_user_file,
                               max_cache_size)

    def _extract_user_from_path(self, path):
        actual_user = None
        for user in self.repos.get_users():
            if path.startswith('/' + user):
                actual_user = user
                break
        return actual_user

    def _extract_repo_from_path(self, actual_user, path):
        actual_repo = None
        for repo in self.repos.get_repos():
            repopath = os.path.join(actual_user, repo)
            res = re.findall(r'^\/' + repopath + r'$|^\/' +
                             repopath + r'\/', path)
            if res:
                actual_repo = repo
                break
        return actual_repo

    def _get_htaccess_content(self, username):
        # this restricts access to the user username
        # for webdav on apache
        content = self.htaccess_template
        content += b'Require user ' + username.encode() + b'\n'
        return content

    def getattr(self, path, file_handler=None):
        """
        get attributes of the path

        The argument file_handler is not used, but can be given to be
        compatible to typical getattr functions.
        """
        # pylint: disable=unused-argument
        if path == '/':
            return self._empty_dir_attr
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:
            raise fusepy.FuseOSError(errno.ENOENT)
        if path == '/' + actual_user:
            return self._empty_dir_attr
        elif (self.provide_htaccess and
              (path == '/' + actual_user + '/.htaccess')):
            file_attr = self._empty_file_attr.copy()
            file_attr['st_size'] = len(self._get_htaccess_content(actual_user))
            return file_attr
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # check if path is part of repo path
            part_of_repo_path = False
            for repo in self.repos.get_repos():
                if repo.startswith(path[2+len(actual_user):]):
                    part_of_repo_path = True
                    break
            if part_of_repo_path:
                return self._empty_dir_attr
            # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].getattr(
            _extract_repopath_from_path(actual_user, actual_repo, path))

    def read(self, path, size, offset, file_handler):
        """
        read parts of path
        """
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        if (self.provide_htaccess and
              (path == '/' + actual_user + '/.htaccess')):
            startindex = offset
            stopindex = 1024  # assume no usename is longer than 1011
            if size is not None:
                stopindex = startindex + size
            return \
                self._get_htaccess_content(actual_user)[startindex:stopindex]
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].read(
            _extract_repopath_from_path(actual_user, actual_repo, path),
            size, offset, file_handler)

    def readdir(self, path, file_handler):
        """
        read the directory path

        The argument file_handler is not used, but can be given to be
        compatible to typical readdir functions.
        """
        # pylint: disable=unused-argument
        if path == '/':
            return ['.', '..'] + self.repos.get_users()
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        if path == '/' + actual_user:
            retlist = ['.', '..']
            for repo in self.repos.get_repos(user=actual_user):
                retlist.append(repo.split('/')[0])
            if self.provide_htaccess:
                retlist.append('.htaccess')
            return list(set(retlist))
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # check if path is part of repo path
            repos = []
            for repo in self.repos.get_repos():
                mypath = path[2+len(actual_user):]
                res = re.findall(
                    r'^' + mypath + r'$|^' + mypath + r'\/([^\/]+)', repo)
                if res:
                    repos.append(res[0])
            if bool(repos):  # path is part of repo path
                return ['.', '..'] + list(set(repos))
            # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].readdir(
            _extract_repopath_from_path(actual_user, actual_repo, path))

    def readlink(self, path):
        """
        read the symbolic link path
        """
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        file_handler = self.open(path, 'r')
        ret = self.repos.repos[actual_repo].read(
            _extract_repopath_from_path(actual_user, actual_repo, path),
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
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        if (self.provide_htaccess and
              (path == '/' + actual_user + '/.htaccess')):
            return self.simple_file_handler.get(self.src_dir)
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].open(
            _extract_repopath_from_path(actual_user, actual_repo, path),
            flags)

    def release(self, path, file_handler):
        """
        Releases the lock file_fandler on path.
        """
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        if (self.provide_htaccess and
              (path == '/' + actual_user + '/.htaccess')):
            return self.simple_file_handler.remove(self.src_dir, file_handler)
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].release(
            _extract_repopath_from_path(actual_user, actual_repo, path),
            file_handler)


class GitBareRepoTreeGitolite(
        _GitBareRepoTreeGitoliteMixin, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """


class GitBareRepoTreeGitoliteLogging(
        _GitBareRepoTreeGitoliteMixin,
        fusepy.LoggingMixIn, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """
