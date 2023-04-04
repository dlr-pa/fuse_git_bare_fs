"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12, 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the tools in the module py_fuse_git_bare_fs.repotools_dulwich

But theses tests only run if the python module dulwich is available;
otherwise they are skipped without an error.

You can run this file directly:

  env python3 py_fuse_git_bare_fs_repotools_dulwich.py

Or you can run only one test, e. g.:

  env python3 py_fuse_git_bare_fs_repotools_dulwich.py \
    PyFuseGitBareFsRepotoolsDulwich.test_repotools_dulwich_get_ref
"""

import unittest

try:
    from .py_fuse_git_bare_fs_repotools_dulwich_git import \
        PyFuseGitBareFsRepotoolsDulwichGitMixIn
except (ModuleNotFoundError, ImportError):
    from py_fuse_git_bare_fs_repotools_dulwich_git import \
        PyFuseGitBareFsRepotoolsDulwichGitMixIn


class PyFuseGitBareFsRepotoolsDulwich(
        unittest.TestCase, PyFuseGitBareFsRepotoolsDulwichGitMixIn):
    """
    :Author: Daniel Mohr
    :Date: 2021-10-12, 2023-04-04
    """
    # pylint: disable = bad-option-value, import-outside-toplevel

    def test_get_ref(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_ref from the module
        py_fuse_git_bare_fs.repotools_dulwich
        """
        self._test_get_ref('dulwich')

    def test_get_blob_data(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_blob_data from the module
        py_fuse_git_bare_fs.repotools_dulwich

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_dulwich.py \
            PyFuseGitBareFsRepotoolsDulwich.test_repotools_dulwich_get_blob_data
        """
        self._test_get_blob_data('dulwich')

    def test_get_repo_data(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_repo_data from the module
        py_fuse_git_bare_fs.repotools_dulwich

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_dulwich.py \
            PyFuseGitBareFsRepotoolsDulwich.test_repotools_dulwich_get_repo_data
        """
        self._test_get_repo_data('dulwich')

    def test_get_size_of_blob(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_size_of_blob from the module
        py_fuse_git_bare_fs.repotools_dulwich

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_dulwich.py \
            PyFuseGitBareFsRepotoolsDulwich.test_get_size_of_blob
        """
        self._test_get_size_of_blob('dulwich')

    def test_get_tree(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_tree from the module
        py_fuse_git_bare_fs.repotools_dulwich

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_dulwich.py \
            PyFuseGitBareFsRepotoolsDulwich.test_get_tree
        """
        self._test_get_tree('dulwich')


if __name__ == '__main__':
    unittest.main(verbosity=2)
