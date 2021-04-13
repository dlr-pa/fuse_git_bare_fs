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
import subprocess
import time

from .repo_class import repo_class


class user_repos():
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13
    """

    def __init__(self, repopath, root_object):
        self.repopath = repopath
        self.root_object = root_object  # not used for gitolite-admin
        self.adminrepo = os.path.join(self.repopath, 'gitolite-admin.git')
        self.commit_hash = None
        self.users = None
        self.repos = None
        self.userrepoaccess = None

    def _cache_up_to_date(self):
        cp = subprocess.run(
            ["git cat-file --batch-check='%(objectname)'"],
            input=b"master",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.adminrepo, shell=True, timeout=3, check=True)
        if cp.stdout.decode().strip() == self.commit_hash:
            return True
        return False

    def _update_cache(self):
        if not self._cache_up_to_date():
            self.commit_hash = None
            self.users = None
            #self.repos = None
            self.userrepoaccess = dict()
            cp = subprocess.run(
                ["git cat-file --batch"], input=b"master",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self.adminrepo, shell=True, timeout=3, check=True)
            if cp.stdout.startswith(b"master"):
                # empty repo or "master" does not exists
                msg = 'root repository object "maser" does not exists.'
                warnings.warn(msg)
                return False
            splittedstdout = cp.stdout.decode().split('\n')
            self.commit_hash = splittedstdout[0].split()[0]
        return True

    def get_users(self):
        # userlist=$(gitolite list-users | grep -v @ | sort -u)
        if (not self._cache_up_to_date()) or (self.users is None):
            self._update_cache()
            cp = subprocess.run(
                ["gitolite list-users"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self.adminrepo, shell=True, timeout=3, check=True)
            self.users = []
            for line in cp.stdout.split(b'\n'):
                username = line.strip().decode()
                if ((username != 'admin') and (len(username) > 0) and
                        (not username.startswith('@'))):
                    self.users.append(username)
        return self.users

    def get_repos(self, user=None):
        # repolist=$(gitolite list-phy-repos)
        if (not self._cache_up_to_date()) or (self.repos is None):
            self._update_cache()
            cp = subprocess.run(
                ["gitolite list-phy-repos"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self.adminrepo, shell=True, timeout=3, check=True)
            repos = []
            for line in cp.stdout.split(b'\n'):
                reponame = line.strip().decode()
                if (reponame != 'gitolite-admin') and (len(reponame) > 0):
                    repos.append(reponame)
            if self.repos is None:
                self.repos = dict()
                for reponame in repos:
                    self.repos[reponame] = repo_class(
                        os.path.join(self.repopath, reponame) + '.git',
                        self.root_object)
            else:
                for reponame in repos:
                    if reponame not in self.repos.keys():
                        self.repos[reponame] = repo_class(
                            os.path.join(self.repopath, reponame) + '.git',
                            self.root_object)
                for reponame in self.repos.keys():
                    if reponame not in repos:
                        del self.repos[reponame]
        if user is None:
            return list(self.repos.keys())
        else:  # return repos with access for the given user
            if not user in self.userrepoaccess:
                self.userrepoaccess[user] = []
                for reponame in self.repos:
                    cp = subprocess.run(
                        ['gitolite access -q ' + reponame + ' ' + user],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        cwd=self.adminrepo, shell=True, timeout=3, check=False)
                    if cp.returncode == 0:  # access
                        self.userrepoaccess[user].append(reponame)
            return self.userrepoaccess[user]


class _my_mixin():
    _empty_attr = {'st_mode': 16893, 'st_size': 4096}
    _empty_attr['st_uid'], _empty_attr['st_gid'], _ = fusepy.fuse_get_context()
    _empty_attr['st_atime'] = _empty_attr['st_mtime'] = \
        _empty_attr['st_ctime'] = time.time()


class _git_bare_repo_tree_gitolite_mixin(_my_mixin):
    def __init__(self, src_dir, root_object, provide_htaccess):
        self.src_dir = src_dir
        self.root_object = root_object
        self.provide_htaccess = provide_htaccess
        self.repos = user_repos(src_dir, self.root_object)

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
            if path.startswith('/' + os.path.join(actual_user, repo)):
                actual_repo = repo
                break
        return actual_repo

    def _extract_repopath_from_path(self, actual_user, actual_repo, path):
        repopath = path[2+len(actual_user)+len(actual_repo):]
        if len(repopath) == 0:
            repopath = '/'
        return repopath

    def getattr(self, path, fh=None):
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:
            return self._empty_attr
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:
            return self._empty_attr
        return self.repos.repos[actual_repo].getattr(
            self._extract_repopath_from_path(actual_user, actual_repo, path))

    def read(self, path, size, offset, fh):
        actual_user = self._extract_user_from_path(path)
        if actual_user is None:  # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
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
        if path == '/' + actual_user:
            retlist = []
            for repo in self.repos.get_repos(user=actual_user):
                retlist.append(repo.split('/')[0])
            return retlist
        actual_repo = self._extract_repo_from_path(actual_user, path)
        if actual_repo is None:  # check if path is part of repo path
            repos = []
            for repo in self.repos.get_repos():
                if repo.startswith(path[2+len(actual_user):]):
                    repos.append(repo[1+len(path[2+len(actual_user):]):])
            if len(repos) > 0:  # path is part of repo path
                return repos
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


class _git_bare_repo_tree_mixin(_my_mixin):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-13

    read only access to working trees of a git bare repositories
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
            return self._empty_attr

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


class git_bare_tree_gitolite_repo(
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
