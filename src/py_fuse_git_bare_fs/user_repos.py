"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-06-16 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os.path
import subprocess
import warnings

from .repo_class import repo_class
from .read_write_lock import read_write_lock
from .simple_file_cache import simple_file_cache
from .simple_file_handler import simple_file_handler_class


class user_repos():
    """
    :Author: Daniel Mohr
    :Date: 2021-06-16
    """

    def __init__(self, repopath, root_object,
                 gitolite_cmd='gitolite', gitolite_user_file=None,
                 max_cache_size=1073741824,
                 simple_file_handler=None):
        self.repopath = repopath
        self.root_object = root_object  # not used for gitolite-admin
        self.gitolite_cmd = gitolite_cmd
        self.gitolite_user_file = gitolite_user_file
        self.adminrepo = os.path.join(self.repopath, 'gitolite-admin.git')
        self.cache = simple_file_cache(max_cache_size=max_cache_size)
        if simple_file_handler is None:
            self.simple_file_handler = simple_file_handler_class()
        else:
            self.simple_file_handler = simple_file_handler
        self.lock = read_write_lock()
        with self.lock.write_locked():
            self.commit_hash = None
            self.mtime_gitolite_user_file = None
            self.users_from_file = None
            self.users = None
            self.repos = None
            self.userrepoaccess = None

    def _del_(self):
        self._lock.acquire_write()
        del self.repos

    def _cache_up_to_date(self):
        with self.lock.read_locked():
            commit_hash = self.commit_hash
            mtime_gitolite_user_file = self.mtime_gitolite_user_file
        if commit_hash is None:
            return False
        if ((self.gitolite_user_file is not None) and
                os.path.isfile(self.gitolite_user_file)):
            # if self.gitolite_user_file does not exist, we ignore it
            if ((mtime_gitolite_user_file is None) or
                (mtime_gitolite_user_file <
                 os.path.getmtime(self.gitolite_user_file))):
                return False
        elif self.gitolite_user_file is not None:
            # self.gitolite_user_file is not a file anymore
            # (maybe it is deleted)
            return False
        cp = subprocess.run(
            ["git cat-file --batch-check='%(objectname)'"],
            input=b"master",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.adminrepo, shell=True, timeout=3, check=True)
        if cp.stdout.decode().strip() == commit_hash:
            return True
        return False

    def _update_cache(self, update_cache=None):
        """
        self.lock has to have the write lock, e. g.::

          self.lock.acquire_write()
          ...
          self.lock.release_write()
        """
        if (update_cache) or (not self._cache_up_to_date()):
            self.commit_hash = None
            self.mtime_gitolite_user_file = None
            self.users = None
            self.users_from_file = None
            self.repos = None
            self.userrepoaccess = dict()
            if ((self.gitolite_user_file is not None) and
                    os.path.isfile(self.gitolite_user_file)):
                self.mtime_gitolite_user_file = \
                    os.path.getmtime(self.gitolite_user_file)
                with open(self.gitolite_user_file, 'r') as fd:
                    self.users_from_file = set(fd.read().splitlines())
            cp = subprocess.run(
                ["git cat-file --batch"], input=b"master",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self.adminrepo, shell=True, timeout=3, check=True)
            if cp.stdout.startswith(b"master"):
                # empty repo or "master" does not exists
                msg = 'root repository object "master" does not exists.'
                warnings.warn(msg)
                return False
            splittedstdout = cp.stdout.decode().split('\n')
            self.commit_hash = splittedstdout[0].split()[0]
        return True

    def get_users(self):
        # userlist=$(gitolite list-users | grep -v @ | sort -u)
        if (not self._cache_up_to_date()) or (self.users is None):
            with self.lock.write_locked():
                self._update_cache(update_cache=True)
                cp = subprocess.run(
                    [self.gitolite_cmd + ' list-users'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    cwd=self.adminrepo, shell=True, timeout=3, check=True)
                self.users = []
                for line in cp.stdout.split(b'\n'):
                    username = line.strip().decode()
                    if ((username != 'admin') and (len(username) > 0) and
                            (not username.startswith('@'))):
                        self.users.append(username)
                if self.users_from_file is not None:
                    self.users = list(self.users_from_file.union(self.users))
        with self.lock.read_locked():
            ret = self.users
        return ret

    def get_repos(self, user=None):
        # repolist=$(gitolite list-phy-repos)
        if (not self._cache_up_to_date()) or (self.repos is None):
            with self.lock.write_locked():
                self._update_cache(update_cache=True)
                cp = subprocess.run(
                    [self.gitolite_cmd + ' list-phy-repos'],
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
                            root_object=self.root_object, cache=self.cache,
                            simple_file_handler=self.simple_file_handler)
                else:
                    for reponame in repos:
                        if reponame not in self.repos.keys():
                            self.repos[reponame] = repo_class(
                                os.path.join(self.repopath, reponame) + '.git',
                                root_object=self.root_object, cache=self.cache,
                                simple_file_handler=self.simple_file_handler)
                    for reponame in list(self.repos.keys()):
                        if reponame not in repos:
                            del self.repos[reponame]
        if user is None:
            with self.lock.read_locked():
                ret = list(self.repos.keys())
            return ret
        else:  # return repos with access for the given user
            with self.lock.read_locked():
                if user not in self.userrepoaccess:
                    self.userrepoaccess[user] = []
                    for reponame in self.repos:
                        cp = subprocess.run(
                            [self.gitolite_cmd + ' access -q ' +
                             reponame + ' ' + user],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            cwd=self.adminrepo, shell=True,
                            timeout=3, check=False)
                        if cp.returncode == 0:  # access
                            self.userrepoaccess[user].append(reponame)
                ret = self.userrepoaccess[user]
            return ret
