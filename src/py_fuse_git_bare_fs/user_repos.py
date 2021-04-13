"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-13 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os.path
import subprocess

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
