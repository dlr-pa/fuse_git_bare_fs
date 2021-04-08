#!/usr/bin/env python3

import logging

import os
import os.path

import fusepy

# for ubuntu 18.04
#  apt install python3-fusepy
# ./test_a2b.py a b
# sudo -u www-data ./test_a2b.py a b


class a2b(fusepy.LoggingMixIn, fusepy.Operations):
    """
    simply mirror a directory
    """
    # /usr/lib/python3/dist-packages/fusepy.py

    def __init__(self, src_dir):
        self.src_dir = src_dir

    def getattr(self, path, fh=None):
        # file:///usr/share/doc/python3/html/library/os.html#os.lstat
        stat = os.lstat(os.path.join(self.src_dir, path[1:]))
        #return dict((key, getattr(stat, key)) for key in (
        #    'st_atime', 'st_gid', 'st_mode', 'st_mtime', 'st_size', 'st_uid'))
        return dict((key, getattr(stat, key)) for key in (
            'st_mode', 'st_uid', 'st_gid', 'st_size',
            'st_atime', 'st_mtime', 'st_ctime'))

    def read(self, path, size, offset, fh):
        with open(os.path.join(self.src_dir, path[1:])) as fd:
            fd.seek(offset, 0)
            buf = fd.read(size)
        return buf

    def readdir(self, path, fh):
        return os.listdir(os.path.join(self.src_dir, path[1:]))

    def readlink(self, path):
        return os.readlink(os.path.join(self.src_dir, path[1:]))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('src_dir')
    parser.add_argument('target_dir')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    fuse = fusepy.FUSE(
        a2b(args.src_dir),
        args.target_dir,
        foreground=True,
        nothreads=True,
        allow_other=False)
