"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12, 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the tools in the module py_fuse_git_bare_fs.repotools_git

You can run this file directly:

  env python3 py_fuse_git_bare_fs_repotools_git.py

Or you can run only one test, e. g.:

  env python3 py_fuse_git_bare_fs_repotools_git.py \
    PyFuseGitBareFsRepotoolsGit.test_repotools_git_get_ref
"""

import unittest

try:
    from .py_fuse_git_bare_fs_repotools_dulwich_git import \
        PyFuseGitBareFsRepotoolsDulwichGitMixIn
except ModuleNotFoundError:
    from py_fuse_git_bare_fs_repotools_dulwich_git import \
        PyFuseGitBareFsRepotoolsDulwichGitMixIn


class PyFuseGitBareFsRepotoolsGit(
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

        It tests the tool/function get_ref from the module
        py_fuse_git_bare_fs.repotools_git
        """
        self._test_get_ref('git')

    def test_get_blob_data(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        It tests the tool/function get_blob_data from the module
        py_fuse_git_bare_fs.repotools_git

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_git.py \
            PyFuseGitBareFsRepotoolsGit.test_repotools_git_get_blob_data
        """
        self._test_get_blob_data('git')

    def test_get_repo_data(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        It tests the tool/function get_repo_data from the module
        py_fuse_git_bare_fs.repotools_git

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_git.py \
            PyFuseGitBareFsRepotoolsGit.test_repotools_git_get_repo_data
        """
        self._test_get_repo_data('git')

    def test_get_size_of_blob(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        It tests the tool/function get_size_of_blob from the module
        py_fuse_git_bare_fs.repotools_git

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_git.py \
            PyFuseGitBareFsRepotoolsGit.test_get_size_of_blob
        """
        self._test_get_size_of_blob('git')

    def test_get_tree(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        It tests the tool/function get_tree from the module
        py_fuse_git_bare_fs.repotools_git

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_git.py \
            PyFuseGitBareFsRepotoolsGit.test_get_tree
        """
        self._test_get_tree('git')


if __name__ == '__main__':
    unittest.main(verbosity=2)
