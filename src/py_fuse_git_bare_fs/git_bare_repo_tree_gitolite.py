"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-16 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import errno
import fusepy  # https://github.com/fusepy/fusepy
import os.path
import re

from .empty_attr_mixin import _empty_attr_mixin
from .user_repos import user_repos


class _git_bare_repo_tree_gitolite_mixin(_empty_attr_mixin):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-16

    read only access to working trees of git bare repositories
    """

    def __init__(self, src_dir, root_object, provide_htaccess,
                 gitolite_cmd='gitolite'):
        self.src_dir = src_dir
        self.root_object = root_object
        self.provide_htaccess = provide_htaccess
        self.repos = user_repos(src_dir, self.root_object, gitolite_cmd)

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
            res = re.findall('^\/' + repopath + '$|^\/' +
                             repopath + '\/', path)
            if res:
                actual_repo = repo
                break
        return actual_repo

    def _extract_repopath_from_path(self, actual_user, actual_repo, path):
        repopath = path[2+len(actual_user)+len(actual_repo):]
        if len(repopath) == 0:
            repopath = '/'
        return repopath

    def _get_htaccess_content(self, username):
        # this restricts access to the user username
        # for webdav on apache
        content = b'Require user ' + username.encode() + b'\n'
        return content

    def getattr(self, path, fh=None):
        if path == '/':
            return self._empty_dir_attr
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:
            raise fusepy.FuseOSError(errno.ENOENT)
        elif path == '/' + actual_user:
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
            else:  # no such file or directory
                raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].getattr(
            self._extract_repopath_from_path(actual_user, actual_repo, path))

    def read(self, path, size, offset, fh):
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        elif (self.provide_htaccess and
              (path == '/' + actual_user + '/.htaccess')):
            startindex = offset
            stopindex = 1024  # assume no usename is longer than 1011
            if size is not None:
                stopindex = startindex + size
            print('content', self._get_htaccess_content(
                actual_user)[startindex:stopindex])
            return self._get_htaccess_content(actual_user)[startindex:stopindex]
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].read(
            self._extract_repopath_from_path(actual_user, actual_repo, path),
            size, offset)

    def readdir(self, path, fh):
        if path == '/':
            return self.repos.get_users()
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        elif path == '/' + actual_user:
            retlist = []
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
                    '^' + mypath + '$|^' + mypath + '\/([^\/]+)', repo)
                if res:
                    repos.append(res[0])
            if len(repos) > 0:  # path is part of repo path
                return list(set(repos))
            else:  # no such file or directory
                raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].readdir(
            self._extract_repopath_from_path(actual_user, actual_repo, path))

    def readlink(self, path):
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        return self.repos.repos[actual_repo].read(
            self._extract_repopath_from_path(actual_user, actual_repo, path),
            None, 0).decode()


class git_bare_repo_tree_gitolite(
        _git_bare_repo_tree_gitolite_mixin, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """


class git_bare_repo_tree_gitolite_logging(
        _git_bare_repo_tree_gitolite_mixin,
        fusepy.LoggingMixIn, fusepy.Operations):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to the working tree of a git bare repository
    """
