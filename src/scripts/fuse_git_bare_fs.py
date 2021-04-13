#!/usr/bin/env python3
"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-12 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import py_fuse_git_bare_fs

# for ubuntu 18.04
#  apt install python3-fusepy
# ./fuse_git_bare_fs.py a b
# sudo -u www-data ./fuse_git_bare_fs.py a b


if __name__ == '__main__':
    py_fuse_git_bare_fs.fuse_git_bare_fs()
