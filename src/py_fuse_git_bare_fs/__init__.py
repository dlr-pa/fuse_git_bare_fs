"""
py_fuse_git_bare_fs
===================

.. contents::

description
===========
"fuse_git_bare_fs" is a tool to mount the working tree of a git bare repository
as a filesystem in user space (fuse). It gives only read access.
For a write access you should do a git commit and use git.

copyright + license
===================
Author: Daniel Mohr

Date: 2021-04-26 (last change).

License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

Copyright (C) 2021 Daniel Mohr
 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

 see http://www.gnu.org/licenses/
"""

try:
    # try to get version from package metadata
    import pkg_resources
    __version__ = pkg_resources.require('py_fuse_git_bare_fs')[0].version
except (ModuleNotFoundError, ImportError, pkg_resources.DistributionNotFound):
    pass

from .fuse_git_bare_fs import fuse_git_bare_fs
