"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-04-04 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""


class _UsedFsOperationsMixin():
    # pylint: disable=too-few-public-methods
    # disable unused operations to avoid unnecessary errors:
    access = None
    flush = None
    getxattr = None
    ioctl = None
    listxattr = None
    opendir = None
    releasedir = None
    statfs = None
    # we only use/provide:
    #  getattr
    #  read
    #  readdir
    #  readlink
    #  open
    #  release
    #  utimens
