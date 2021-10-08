"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-08 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os.path
import subprocess
import warnings

from .repo_class import RepoClass
from .read_write_lock import ReadWriteLock
from .simple_file_cache import SimpleFileCache
from .simple_file_handler import SimpleFileHandlerClass
try:
    from .repotools_git import get_ref
except ModuleNotFoundError:
    from .repotools_dulwich import get_ref


class UserRepos():
    """
    :Author: Daniel Mohr
    :Date: 2021-10-08
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, repopath, root_object,
                 gitolite_cmd='gitolite', gitolite_user_file=None,
                 max_cache_size=1073741824,
                 simple_file_handler=None,
                 file_st_modes=None):
        # pylint: disable=too-many-arguments
        self.repopath = repopath
        self.root_object = root_object  # not used for gitolite-admin
        self.gitolite_cmd = gitolite_cmd
        self.gitolite_user_file = gitolite_user_file
        self.adminrepo = os.path.join(self.repopath, 'gitolite-admin.git')
        self.cache = SimpleFileCache(max_cache_size=max_cache_size)
        if simple_file_handler is None:
            self.simple_file_handler = SimpleFileHandlerClass()
        else:
            self.simple_file_handler = simple_file_handler
        self.file_st_modes = file_st_modes
        self.lock = ReadWriteLock()
        with self.lock.write_locked():
            self.commit_hash = None
            self.mtime_gitolite_user_file = None
            self.users_from_file = None
            self.users = None
            self.repos = None
            self.userrepoaccess = None

    def _del_(self):
        self.lock.acquire_write()
        del self.repos
        del self.lock

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
        if get_ref(self.adminrepo, b'master') == commit_hash:
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
            cpi = subprocess.run(
                ["git cat-file --batch"], input=b"master",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self.adminrepo, shell=True, timeout=3, check=True)
            if cpi.stdout.startswith(b"master"):
                # empty repo or "master" does not exists
                msg = 'root repository object "master" does not exists.'
                warnings.warn(msg)
                self.commit_hash = None
                self.mtime_gitolite_user_file = None
                self.users = None
                self.users_from_file = None
                self.repos = None
                self.userrepoaccess = dict()
                return False
            splittedstdout = cpi.stdout.decode().split('\n')
            commit_hash = splittedstdout[0].split()[0]
            if commit_hash != self.commit_hash:
                self.commit_hash = commit_hash
                self.users = None
                self.repos = None
                self.userrepoaccess = dict()
            if ((self.gitolite_user_file is not None) and
                    os.path.isfile(self.gitolite_user_file)):
                mtime_gitolite_user_file = \
                    os.path.getmtime(self.gitolite_user_file)
                with open(self.gitolite_user_file, 'r') as fd:
                    users_from_file = set(fd.read().splitlines())
                if self.mtime_gitolite_user_file != mtime_gitolite_user_file:
                    self.mtime_gitolite_user_file = mtime_gitolite_user_file
                if ((self.users_from_file is None) or
                        bool(users_from_file.symmetric_difference(
                            self.users_from_file))):
                    self.users_from_file = users_from_file
                    self.users = None
                    self.repos = None
                    self.userrepoaccess = dict()
            else:
                self.mtime_gitolite_user_file = None
                self.users_from_file = None
                self.users = None
                self.repos = None
                self.userrepoaccess = dict()
        return True

    def get_users(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-06-16
        """
        # userlist=$(gitolite list-users | grep -v @ | sort -u)
        if (not self._cache_up_to_date()) or (self.users is None):
            with self.lock.write_locked():
                self._update_cache(update_cache=True)
                cpi = subprocess.run(
                    [self.gitolite_cmd + ' list-users'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    cwd=self.adminrepo, shell=True, timeout=3, check=True)
                self.users = []
                for line in cpi.stdout.split(b'\n'):
                    username = line.strip().decode()
                    if ((username != 'admin') and bool(username) and
                            (not username.startswith('@'))):
                        self.users.append(username)
                if self.users_from_file is not None:
                    self.users = list(self.users_from_file.union(self.users))
        with self.lock.read_locked():
            ret = self.users
        return ret

    def get_repos(self, user=None):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-06
        """
        # pylint: disable=too-many-branches
        if (not self._cache_up_to_date()) or (self.repos is None):
            with self.lock.write_locked():
                self._update_cache(update_cache=True)
                cpi = subprocess.run(
                    [self.gitolite_cmd + ' list-phy-repos'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    cwd=self.adminrepo, shell=True, timeout=3, check=True)
                repos = []
                for line in cpi.stdout.split(b'\n'):
                    reponame = line.strip().decode()
                    if (reponame != 'gitolite-admin') and bool(reponame):
                        repos.append(reponame)
                if self.repos is None:
                    self.repos = dict()
                    for reponame in repos:
                        self.repos[reponame] = RepoClass(
                            os.path.join(self.repopath, reponame) + '.git',
                            root_object=self.root_object, cache=self.cache,
                            simple_file_handler=self.simple_file_handler,
                            file_st_modes=self.file_st_modes)
                else:
                    for reponame in repos:
                        if reponame not in self.repos.keys():
                            self.repos[reponame] = RepoClass(
                                os.path.join(self.repopath, reponame) + '.git',
                                root_object=self.root_object, cache=self.cache,
                                simple_file_handler=self.simple_file_handler,
                                file_st_modes=self.file_st_modes)
                    for reponame in list(self.repos.keys()):
                        if reponame not in repos:
                            del self.repos[reponame]
        if user is None:
            with self.lock.read_locked():
                ret = list(self.repos.keys())
            return ret
        # else:  # return repos with access for the given user
        with self.lock.read_locked():
            if user not in self.userrepoaccess:
                self.userrepoaccess[user] = []
                for reponame in self.repos:
                    cpi = subprocess.run(
                        [self.gitolite_cmd + ' access -q ' +
                         reponame + ' ' + user],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        cwd=self.adminrepo, shell=True,
                        timeout=3, check=False)
                    if cpi.returncode == 0:  # access
                        self.userrepoaccess[user].append(reponame)
            ret = self.userrepoaccess[user]
        return ret
