"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-14 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import errno
import fusepy  # https://github.com/fusepy/fusepy
import os
import os.path
import re
import subprocess
import time
import warnings


class repo_class():
    """
    :Author: Daniel Mohr
    :Date: 2021-04-14

    https://git-scm.com/book/en/v2
    https://git-scm.com/docs/git-cat-file
    """
    time_regpat = re.compile(r' ([0-9]+) [+0-9]+$')
    gitmode2st_mode = {'100644': 33204, '100755': 33277, '120000': 41471}
    st_uid_st_gid = (os.geteuid(), os.getegid())

    def __init__(self, src_dir, root_object):
        self.src_dir = src_dir
        self.root_object = root_object
        self.tree = None
        self.commit_hash = None
        self.tree_hash = None
        # we use the last commit time for everything, could be enhanced
        self.time = None
        self._read_tree()

    def _cache_up_to_date(self):
        cp = subprocess.run(
            ["git cat-file --batch-check='%(objectname)'"],
            input=self.root_object,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.src_dir, shell=True, timeout=3, check=True)
        if cp.stdout.decode().strip() == self.commit_hash:
            return True
        return False

    def _update_cache(self):
        if not self._cache_up_to_date():
            self.tree = None
            self.commit_hash = None
            self.tree_hash = None
            self.time = None
            cp = subprocess.run(
                ["git cat-file --batch"], input=self.root_object,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self.src_dir, shell=True, timeout=3, check=True)
            if cp.stdout.startswith(self.root_object):
                # empty repo or self.root_object does not exists
                msg = \
                    'root repository object "%s" in "%s" does not exists. ' % \
                    (self.root_object, self.src_dir)
                msg += 'Mountpoint will be empty.'
                warnings.warn(msg)
                return False
            splittedstdout = cp.stdout.decode().split('\n')
            self.commit_hash = splittedstdout[0].split()[0]
            for data in splittedstdout:
                if data.startswith('tree'):
                    self.tree_hash = data.split()[1]
                    break
            for data in splittedstdout:
                if data.startswith('committer'):
                    res = self.time_regpat.findall(data)
                    if res:
                        self.time = int(res[0])
                        break
        return True

    def _git_cat_file(self, git_object):
        cp = subprocess.run(
            ['git cat-file -p ' + git_object],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.src_dir, shell=True, timeout=3, check=True)
        return cp.stdout.decode()

    def _read_tree(self):
        if not self._update_cache():
            return
        self.tree = dict()
        # self.tree[path] =
        #   {'listdir': [], 'blobs': {name: {'mode': str, 'hash': str}}}
        trees = [('/', self.tree_hash)]  # (name, hash)
        self.tree['/'] = dict()
        while len(trees) > 0:
            act_path, act_tree_hash = trees.pop(0)
            self.tree[act_path]['listdir'] = []
            self.tree[act_path]['blobs'] = dict()
            git_objects = self._git_cat_file(act_tree_hash).split('\n')
            for line in git_objects:
                if len(line) < 8:
                    continue
                (obj_mode, obj_type, obj_hash, obj_name) = line.split()
                if obj_type == 'blob':
                    self.tree[act_path]['listdir'].append(obj_name)
                    self.tree[act_path]['blobs'][obj_name] = {
                        'mode': obj_mode, 'hash': obj_hash}
                elif obj_type == 'tree':
                    self.tree[act_path]['listdir'].append(obj_name)
                    obj_path = os.path.join(act_path, obj_name)
                    trees = [(obj_path, obj_hash)]
                    self.tree[obj_path] = dict()

    def _get_size_of_blob(self, head, tail):
        if not 'size' in self.tree[head]['blobs'][tail]:
            cp = subprocess.run(
                ["git cat-file --batch-check='%(objectsize)'"],
                input=self.tree[head]['blobs'][tail]['hash'].encode(),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self.src_dir, shell=True, timeout=3, check=True)
            self.tree[head]['blobs'][tail]['st_size'] = int(cp.stdout.decode())

    def readdir(self, path):
        """
        :param path: string of the path to read/list
        """
        if ((not self._cache_up_to_date()) or
                (self.tree is None) or (not path in self.tree)):
            self._read_tree()
        if (self.tree is None) or (not path in self.tree):
            return []
        else:
            return self.tree[path]['listdir']

    def getattr(self, path):
        head, tail = os.path.split(path)
        if ((not self._cache_up_to_date()) or
            (self.tree is None) or (not head in self.tree)):
            self._read_tree()
        if (self.tree is None) or (not head in self.tree):
            # file:///usr/share/doc/python3/html/library/errno.html
            # no such file or directory
            if (tail == '') and (head == '/'):
                msg = 'root repository object "%s" does not exists. ' % \
                    self.root_object
                msg += 'Mountpoint will be empty.'
                warnings.warn(msg)
                ret = {'st_mode': 16893, 'st_size': 4096}
                ret['st_uid'], ret['st_gid'] = self.st_uid_st_gid
                ret['st_atime'] = ret['st_mtime'] = ret['st_ctime'] = \
                    time.time()
                return ret
            else:
                raise fusepy.FuseOSError(errno.ENOENT)
        ret = dict()
        ret['st_uid'], ret['st_gid'] = self.st_uid_st_gid
        ret['st_atime'] = ret['st_mtime'] = ret['st_ctime'] = self.time
        if (tail == '') or (path in self.tree):  # path is dir
            ret['st_mode'] = 16893
            ret['st_size'] = 4096  # typical for ext4
        else:  # path is blob
            # https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
            # 100644 normal file
            # 100755 executable file
            # 120000 symbolic link
            if not tail in self.tree[head]['blobs']:
                # no such file or directory
                raise fusepy.FuseOSError(errno.ENOENT)
            ret['st_mode'] = self.gitmode2st_mode[
                self.tree[head]['blobs'][tail]['mode']]
            self._get_size_of_blob(head, tail)
            ret['st_size'] = self.tree[head]['blobs'][tail]['st_size']
        return ret

    def read(self, path, size, offset):
        head, tail = os.path.split(path)
        if (self.tree is None) or (not head in self.tree):
            self._read_tree()
        if (self.tree is None) or (not head in self.tree):
            # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        if not tail in self.tree[head]['blobs']:
            # no such file or directory
            raise fusepy.FuseOSError(errno.ENOENT)
        # we read the complete file instead of the required part,
        # this should be enhanced! (at least for unpacked objects)
        self._get_size_of_blob(head, tail)
        startindex = -(1 + offset + self.tree[head]['blobs'][tail]['st_size'])
        stopindex = -1
        if size is not None:
            stopindex = min(startindex + size, -1)
        cp = subprocess.run(
            ["git cat-file --batch"],
            input=self.tree[head]['blobs'][tail]['hash'].encode(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.src_dir, shell=True, timeout=3, check=True)
        return cp.stdout[startindex:stopindex]
