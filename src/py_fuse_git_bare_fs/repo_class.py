"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import errno
try:
    import fusepy  # https://github.com/fusepy/fusepy
except ModuleNotFoundError:
    import fuse as fusepy
import hashlib
import os
import os.path
import re
import subprocess
import time
import warnings

from .empty_attr_mixin import _EmptyAttrMixin
from .read_write_lock import ReadWriteLock
from .simple_file_cache import SimpleFileCache
from .simple_file_handler import SimpleFileHandlerClass
try:
    from .repotools_dulwich import get_ref, get_repo_data, get_size_of_blob
except (ModuleNotFoundError, ImportError):
    from .repotools_git import get_ref, get_repo_data, get_size_of_blob


class RepoClass(_EmptyAttrMixin):
    """
    :Author: Daniel Mohr
    :Date: 2021-10-12

    https://git-scm.com/book/en/v2
    https://git-scm.com/docs/git-cat-file
    """
    # pylint: disable=too-many-instance-attributes
    time_regpat = re.compile(r' ([0-9]+) [0-9+-]+$')
    tree_content_regpat = re.compile(
        r'^([0-9]+) (commit|tree|blob|tag) ([0-9a-f]+)\t(.+)$')
    annex_object_regpat = re.compile(
        r'([.\/]*.git/annex/objects/)(.*)$')
    # https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
    # 100644 normal file
    # 100755 executable file
    # 120000 symbolic link
    gitmode2st_mode = {'100644': 33204, '100755': 33277, '120000': 41471}
    st_uid_st_gid = (os.geteuid(), os.getegid())

    def __init__(self, src_dir, root_object=b'master',
                 max_cache_size=1073741824, cache=None,
                 simple_file_handler=None, file_st_modes=None):
        # pylint: disable=too-many-arguments
        self.src_dir = src_dir
        self.root_object = root_object
        self.tree = None
        self.commit_hash = None
        self.tree_hash = None
        # we use the last commit time for everything, could be enhanced
        self.time = None
        if cache is None:
            self.cache = SimpleFileCache(max_cache_size=max_cache_size)
        else:
            self.cache = cache
        self.content_cache = dict()
        self.content_cache_size = 0
        if simple_file_handler is None:
            self.simple_file_handler = SimpleFileHandlerClass()
        else:
            self.simple_file_handler = simple_file_handler
        if file_st_modes is not None:
            self.gitmode2st_mode['100644'] = file_st_modes[0]  # normal file
            self.gitmode2st_mode['100755'] = file_st_modes[1]  # executable
            self.gitmode2st_mode['120000'] = file_st_modes[2]  # symbolic link
            self._empty_dir_attr['st_mode'] = file_st_modes[3]
            self._empty_file_attr['st_mode'] = file_st_modes[0]
        self.lock = ReadWriteLock()
        with self.lock.write_locked():
            self._read_tree()

    def __del__(self):
        self.simple_file_handler.remove_repo(self.src_dir)
        self.cache.clear_repo_old(self.src_dir)
        self.lock.acquire_write()

    def _cache_up_to_date(self):
        if get_ref(self.src_dir, self.root_object) == self.commit_hash:
            return True
        self.simple_file_handler.remove_repo(self.src_dir)
        return False

    def _update_cache(self, update_cache=None):
        if (update_cache) or (not self._cache_up_to_date()):
            self.tree = None
            self.commit_hash = None
            self.tree_hash = None
            self.time = None
            self.content_cache = dict()
            self.cache.clear_repo_old(self.src_dir)
            repo_data = get_repo_data(
                self.src_dir,
                self.root_object,
                self.time_regpat)
            if isinstance(repo_data, tuple):
                (self.commit_hash, self.tree_hash, self.time) = repo_data
            else:
                return repo_data
        return True

    def _git_cat_file(self, git_object):
        cpi = subprocess.run(
            ['git cat-file -p ' + git_object],
            stdout=subprocess.PIPE,
            cwd=self.src_dir, shell=True, timeout=3, check=True)
        return cpi.stdout.decode()

    def _read_tree(self, update_cache=None):
        if not self._update_cache(update_cache=update_cache):
            return
        self.tree = dict()
        # self.tree[path] =
        #   {'listdir': [], 'blobs': {name: {'mode': str, 'hash': str}}}
        trees = [('/', self.tree_hash)]  # (name, hash)
        self.tree['/'] = dict()
        while bool(trees):
            act_path, act_tree_hash = trees.pop(0)
            self.tree[act_path]['listdir'] = []
            self.tree[act_path]['blobs'] = dict()
            git_objects = self._git_cat_file(act_tree_hash).split('\n')
            for line in git_objects:
                if len(line) < 8:
                    continue
                res = self.tree_content_regpat.findall(line)
                if res:
                    (obj_mode, obj_type, obj_hash, obj_name) = res[0]
                    if obj_type == 'blob':
                        self.tree[act_path]['listdir'].append(obj_name)
                        self.tree[act_path]['blobs'][obj_name] = {
                            'mode': obj_mode, 'hash': obj_hash}
                    elif obj_type == 'tree':
                        self.tree[act_path]['listdir'].append(obj_name)
                        obj_path = os.path.join(act_path, obj_name)
                        trees.append((obj_path, obj_hash))
                        self.tree[obj_path] = dict()

    def _get_size_of_blob(self, head, tail):
        if 'st_size' not in self.tree[head]['blobs'][tail]:
            self.tree[head]['blobs'][tail]['st_size'] = get_size_of_blob(
                self.src_dir,
                self.tree[head]['blobs'][tail]['hash'].encode())

    def readdir(self, path):
        """
        :param path: string of the path to read/list
        """
        if not self._cache_up_to_date():
            with self.lock.write_locked():
                self._read_tree(update_cache=True)
        else:
            # remove old cached files
            self.cache.clear_repo_old(self.src_dir)
        self.lock.acquire_read()
        ret = None
        if (self.tree is None) or (path not in self.tree):
            ret = ['.', '..']
        else:
            ret = ['.', '..'] + self.tree[path]['listdir']
        self.lock.release_read()
        return ret

    def _get_annex_path_bare_repo(self, path):
        # https://git-annex.branchable.com/internals/hashing/
        _, tail = os.path.split(path)  # tail is the hash
        md5hash = hashlib.new('md5',
                              os.path.split(path)[1].encode()).hexdigest()
        return os.path.join(
            self.src_dir, 'annex/objects',
            md5hash[:3], md5hash[3:6], tail, tail)

    def _get_annex_path_non_bare_repo(self, path):
        # https://git-annex.branchable.com/internals/hashing/
        return os.path.join(self.src_dir, path)

    def _get_annex_path(self, link_path):
        apath = None
        apath_bare = self._get_annex_path_bare_repo(link_path)
        if os.path.isfile(apath_bare):
            apath = apath_bare
        else:
            apath_non_bare = self._get_annex_path_non_bare_repo(
                link_path)
            if os.path.isfile(apath_non_bare):
                apath = apath_non_bare
        return apath

    def getattr(self, path):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-06

        get attributes of the path
        """
        updated_cache = False
        if not self._cache_up_to_date():
            updated_cache = True
            with self.lock.write_locked():
                self._read_tree(update_cache=True)
        head, tail = os.path.split(path)
        self.lock.acquire_read()
        if ((updated_cache) or
                (self.tree is None) or (head not in self.tree)):
            if not updated_cache:
                with self.lock.write_locked():
                    self._read_tree()
            if (self.tree is None) or (head not in self.tree):
                # file:///usr/share/doc/python3/html/library/errno.html
                # no such file or directory
                if (tail == '') and (head == '/'):
                    msg = 'root repository object "%s" does not exists. ' % \
                        self.root_object
                    msg += 'Mountpoint will be empty.'
                    warnings.warn(msg)
                    ret = self._empty_dir_attr.copy()
                    ret['st_atime'] = ret['st_mtime'] = ret['st_ctime'] = \
                        time.time()
                    self.lock.release_read()
                    return ret
                self.lock.release_read()
                raise fusepy.FuseOSError(errno.ENOENT)
        ret = dict()
        ret['st_uid'], ret['st_gid'] = self.st_uid_st_gid
        ret['st_atime'] = ret['st_mtime'] = ret['st_ctime'] = self.time
        if (tail == '') or (path in self.tree):  # path is dir
            ret['st_mode'] = self._empty_dir_attr['st_mode']
            ret['st_size'] = 4096  # typical for ext4
        else:  # path is blob
            # https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
            # 100644 normal file
            # 100755 executable file
            # 120000 symbolic link
            if tail not in self.tree[head]['blobs']:
                # no such file or directory
                self.lock.release_read()
                raise fusepy.FuseOSError(errno.ENOENT)
            st_mode = self.gitmode2st_mode[
                self.tree[head]['blobs'][tail]['mode']]
            self._get_size_of_blob(head, tail)
            st_size = self.tree[head]['blobs'][tail]['st_size']
            if st_mode == 41471:  # 120000 symbolic link
                # check if it is an accessable git-annex file
                blob_hash = self.tree[head]['blobs'][tail]['hash'].encode()
                link_path = self.cache.get(
                    self.src_dir, path,
                    blob_hash, st_size, st_size, 0).decode()
                #      self._get_annex_path_bare_repo(link_path))
                #      self._get_annex_path_non_bare_repo(link_path))
                annex_object = self.annex_object_regpat.findall(link_path)
                if annex_object:
                    apath = self._get_annex_path(link_path)
                    if apath is not None:
                        # git annex file stored locally
                        stat = os.lstat(apath)
                        st_mode = stat.st_mode
                        st_size = stat.st_size
            ret['st_mode'] = st_mode
            ret['st_size'] = st_size
        self.lock.release_read()
        return ret

    def read(self, path, size, offset, file_fandler):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        read parts of path
        """
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        if not self.simple_file_handler.is_file_handler(self.src_dir,
                                                        file_fandler):
            raise fusepy.FuseOSError(errno.EBADF)
        is_maybe_annex = False  # no git-annex file
        ret = self.cache.get_cached(self.src_dir, path, size, offset, 0.5)
        # check if it is an accessable git-annex file
        head, tail = os.path.split(path)
        st_mode = None
        with self.lock.read_locked():
            try:
                st_mode = self.gitmode2st_mode[
                    self.tree[head]['blobs'][tail]['mode']]
            except (KeyError, TypeError):
                pass
        link_buf = None
        if st_mode == 41471:  # 120000 symbolic link
            # ret is only the complete link path, if size is None
            # therefor we do our own check
            # read file is link, but it is not completly read
            link_buf = self.cache.get_cached(
                self.src_dir, path, None, 0, 0.5)
            if link_buf is not None:
                is_maybe_annex = True  # maybe git-annex file
                link_path = link_buf.decode()
                annex_object = self.annex_object_regpat.findall(link_path)
                if annex_object:
                    apath = self._get_annex_path(link_path)
                    if apath is not None:
                        # git-annex file, return content of linked file
                        # normally a git annex file should be found here;
                        # the annex if clause some lines below is normally
                        # needless
                        with open(apath, 'rb') as fd:
                            fd.seek(offset, 0)
                            buf = fd.read(size)
                        return buf
        if ret is not None:
            return ret
        updated_cache = False
        if not self._cache_up_to_date():
            updated_cache = True
            with self.lock.write_locked():
                self._read_tree(update_cache=True)
        else:
            # remove old cached files
            self.cache.clear_repo_old(self.src_dir)
        head, tail = os.path.split(path)
        self.lock.acquire_read()
        if ((updated_cache) or
                (self.tree is None) or (head not in self.tree)):
            if not updated_cache:
                with self.lock.write_locked():
                    self._read_tree()
            if (self.tree is None) or (head not in self.tree):
                # no such file or directory
                self.lock.release_read()
                raise fusepy.FuseOSError(errno.ENOENT)
        if tail not in self.tree[head]['blobs']:
            # no such file or directory
            self.lock.release_read()
            raise fusepy.FuseOSError(errno.ENOENT)
        blob_hash = self.tree[head]['blobs'][tail]['hash'].encode()
        self._get_size_of_blob(head, tail)
        st_size = self.tree[head]['blobs'][tail]['st_size']
        if st_mode is None:
            st_mode = self.gitmode2st_mode[
                self.tree[head]['blobs'][tail]['mode']]
        if (is_maybe_annex) or (st_mode == 41471):  # could be git-annex file
            if link_buf is None:
                link_buf = self.cache.get(
                    self.src_dir, path, blob_hash, st_size, None, 0)
            link_path = link_buf.decode()
            annex_object = self.annex_object_regpat.findall(link_path)
            if annex_object:
                apath = self._get_annex_path(link_path)
                if apath is not None:
                    # git-annex file, return content of linked file
                    with open(apath, 'rb') as fd:
                        fd.seek(offset, 0)
                        buf = fd.read(size)
                    self.lock.release_read()
                    return buf
        # we read the complete file instead of the required part,
        # this should be enhanced! (at least for unpacked objects)
        self.lock.release_read()
        return self.cache.get(
            self.src_dir, path, blob_hash, st_size, size, offset)

    def open(self, path, flags):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        Creates a lock on path and return it as a file handler.
        Only open as read is supported, but this is not checked.

        This lock will be destroyed, if the repository is changed or it is
        released.

        The arguments are not used, but can be given to be compatible to
        typical open functions.
        """
        # pylint: disable=unused-argument
        if not self._cache_up_to_date():
            with self.lock.write_locked():
                self._read_tree(update_cache=True)
        return self.simple_file_handler.get(self.src_dir)

    def release(self, path, file_fandler):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        Releases the lock file_fandler on path.

        The argument path is not used, but can be given to be compatible to
        typical release functions.
        """
        # pylint: disable=unused-argument
        self.simple_file_handler.remove(self.src_dir, file_fandler)

    def utimens(self, path, times=None):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-24

        This is not implemented at the moment.

        The arguments are not used, but can be given to be compatible to
        typical open functions.
        """
        # pylint: disable=unused-argument,no-self-use
        raise fusepy.FuseOSError(errno.EROFS)
