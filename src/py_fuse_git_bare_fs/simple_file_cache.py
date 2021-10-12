"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-11 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import time

from .read_write_lock import ReadWriteLock

try:
    from .repotools_dulwich import get_blob_data
except (ModuleNotFoundError, ImportError):
    from .repotools_git import get_blob_data


class SimpleFileCache():
    """
    :Author: Daniel Mohr
    :Date: 2021-10-11
    """

    def __init__(self,
                 min_file_size=131072, max_cache_size=1073741824, maxage=1):
        """
        :param min_file_size: minimum file size to store file in cache
        :param cache_size: maximal cache size
        :param maxage: files after this time are removed from the cache
        """
        self.lock = ReadWriteLock()
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
        # pylint: disable=too-many-arguments
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
        # pylint: disable=too-many-arguments
        self.clear_old()
        ret = self.get_cached(
            repopath, path, size, offset, maxage=2*self.maxage)
        if ret is None:
            data = get_blob_data(repopath, blob_hash)
            lendata = len(data)
            if self.min_file_size <= st_size:
                self.lock.acquire_read()
                if self.actual_cache_size + lendata < self.max_cache_size:
                    self.lock.release_read()
                    with self.lock.write_locked():
                        if repopath not in self.cache:
                            self.cache[repopath] = dict()
                        self.cache[repopath][path] = [time.time(),
                                                      data,
                                                      lendata,
                                                      st_size]
                        self.actual_cache_size += self.cache[repopath][path][2]
                else:
                    self.lock.release_read()
            startindex = lendata - 1 - st_size + offset
            stopindex = lendata - 1
            if size is not None:
                stopindex = min(startindex + size, lendata - 1)
            return data[startindex:stopindex]
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
        """
        This method removes the cache for old data/repositories.
        """
        with self.lock.write_locked():
            for repopath in list(self.cache.keys()):
                self._clear_repo_old(repopath)

    def clear_repo_old(self, repopath):
        """
        This method removes the cache for the given data/repositories,
        if the cache is not up to date.
        """
        with self.lock.write_locked():
            if repopath in self.cache:
                self._clear_repo_old(repopath)

    def clear_repo_all(self, repopath):
        """
        This method removes the complete cache.
        """
        with self.lock.write_locked():
            if repopath in self.cache:
                del self.cache[repopath]
