"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-23 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import subprocess
import time

from .read_write_lock import read_write_lock


class simple_file_cache():
    """
    :Author: Daniel Mohr
    :Date: 2021-04-23
    """

    def __init__(self,
                 min_file_size=131072, max_cache_size=1073741824, maxage=1):
        """
        :param min_file_size: minimum file size to store file in cache
        :param cache_size: maximal cache size
        :param maxage: files after this time are removed from the cache
        """
        self.lock = read_write_lock()
        self.min_file_size = min_file_size
        self.max_cache_size = max_cache_size
        self.maxage = maxage
        self.actual_cache_size = 0
        with self.lock.write_locked():
            self.cache = dict()

    def get_cached(self, repopath, path, size, offset, maxage=0.5):
        """
        :param repopath: path to the actual repository
        :param path: path in the actual repository to the blob
        :param size: size to read
        :param offset: offset from where to read
        """
        ret = None
        with self.lock.read_locked():
            if ((repopath in self.cache) and (path in self.cache[repopath]) and
                    (time.time() - self.cache[repopath][path][0] < maxage)):
                startindex = self.cache[repopath][path][2] - 1 - \
                    self.cache[repopath][path][3] + offset
                stopindex = self.cache[repopath][path][2] - 1
                if size is not None:
                    stopindex = min(startindex + size,
                                    self.cache[repopath][path][2] - 1)
                ret = self.cache[repopath][path][1][startindex:stopindex]
                self.cache[repopath][path][0] = time.time()
        return ret

    def get(self, repopath, path, blob_hash, st_size, size, offset):
        """
        :param repopath: path to the actual repository
        :param path: path in the actual repository to the blob
        :param blob_hash: hash of the blob as bytes
        :param st_size: size of the blob
        :param size: size to read
        :param offset: offset from where to read
        """
        self.clear_old()
        ret = self.get_cached(
            repopath, path, size, offset, maxage=2*self.maxage)
        if ret is None:
            cp = subprocess.run(
                ["git cat-file --batch"],
                input=blob_hash,
                stdout=subprocess.PIPE,
                cwd=repopath, shell=True, timeout=3, check=True)
            lcp = len(cp.stdout)
            if self.min_file_size <= st_size:
                self.lock.acquire_read()
                if self.actual_cache_size + lcp < self.max_cache_size:
                    self.lock.release_read()
                    with self.lock.write_locked():
                        if repopath not in self.cache:
                            self.cache[repopath] = dict()
                        self.cache[repopath][path] = [time.time(),
                                                      cp.stdout,
                                                      lcp,
                                                      st_size]
                        self.actual_cache_size += self.cache[repopath][path][2]
                else:
                    self.lock.release_read()
            startindex = lcp - 1 - st_size + offset
            stopindex = lcp - 1
            if size is not None:
                stopindex = min(startindex + size, len(cp.stdout) - 1)
            return cp.stdout[startindex:stopindex]
        else:
            return ret

    def _clear_repo_old(self, repopath):
        """
        write lock has to be locked
        """
        now = time.time()
        for key in list(self.cache[repopath].keys()):
            if now - self.cache[repopath][key][0] > self.maxage:
                self.actual_cache_size -= self.cache[repopath][key][2]
                del self.cache[repopath][key]

    def clear_old(self):
        now = time.time()
        with self.lock.write_locked():
            for repopath in list(self.cache.keys()):
                self._clear_repo_old(repopath)

    def clear_repo_old(self, repopath):
        with self.lock.write_locked():
            if repopath in self.cache:
                self._clear_repo_old(repopath)

    def clear_repo_all(self, repopath):
        with self.lock.write_locked():
            if repopath in self.cache:
                del self.cache[repopath]
