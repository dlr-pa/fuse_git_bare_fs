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

import os
import tempfile
import unittest

try:
    from .prepare_simple_test_environment import PrepareSimpleTestEnvironment
except ModuleNotFoundError:
    from prepare_simple_test_environment import PrepareSimpleTestEnvironment

try:
    from .py_fuse_git_bare_fs_repotools_dulwich_git import \
        PyFuseGitBareFsRepotoolsDulwichGitMixIn
except ModuleNotFoundError:
    from py_fuse_git_bare_fs_repotools_dulwich_git import \
        PyFuseGitBareFsRepotoolsDulwichGitMixIn


class PyFuseGitBareFsRepotoolsDulwich(
        unittest.TestCase, PrepareSimpleTestEnvironment,
        PyFuseGitBareFsRepotoolsDulwichGitMixIn):
    """
    :Author: Daniel Mohr
    :Date: 2021-10-12, 2023-04-04
    """
    # pylint: disable = bad-option-value, import-outside-toplevel

    def test_get_ref(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_ref from the module
        py_fuse_git_bare_fs.repotools_dulwich
        """
        # pylint: disable = unused-variable, unused-import
        try:
            import dulwich
        except ModuleNotFoundError:
            self.skipTest('python module dulwich not available')
            return
        from py_fuse_git_bare_fs.repotools_dulwich import get_ref
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                commit_hash = get_ref(
                    os.path.join(tmpdir, serverdir, reponame), b'master')
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            # run tests
            commit_hash = get_ref(
                os.path.join(tmpdir, serverdir, reponame), b'master')
            self.assertIsInstance(commit_hash, str)
            commit_hash = get_ref(
                os.path.join(tmpdir, serverdir, reponame), b'main')
            self.assertIsInstance(commit_hash, str)
            self.assertEqual(commit_hash, 'main missing')

    def test_get_blob_data(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_blob_data from the module
        py_fuse_git_bare_fs.repotools_dulwich

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_dulwich.py \
            PyFuseGitBareFsRepotoolsDulwich.test_repotools_dulwich_get_blob_data
        """
        # pylint: disable = unused-variable, unused-import
        try:
            import dulwich
        except ModuleNotFoundError:
            self.skipTest('python module dulwich not available')
            return
        from py_fuse_git_bare_fs.repotools_dulwich import get_blob_data
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                data = get_blob_data(
                    os.path.join(tmpdir, serverdir, reponame),
                    b'2e65efe2a145dda7ee51d1741299f848e5bf752e')
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            # run tests
            data = get_blob_data(
                os.path.join(tmpdir, serverdir, reponame),
                b'2e65efe2a145dda7ee51d1741299f848e5bf752e')
            self.assertEqual(
                data,
                b'2e65efe2a145dda7ee51d1741299f848e5bf752e blob 1\na\n')

    def test_get_repo_data(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_repo_data from the module
        py_fuse_git_bare_fs.repotools_dulwich

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_dulwich.py \
            PyFuseGitBareFsRepotoolsDulwich.test_repotools_dulwich_get_repo_data
        """
        # pylint: disable = unused-variable, unused-import
        try:
            import dulwich
        except ModuleNotFoundError:
            self.skipTest('python module dulwich not available')
            return
        import time
        from py_fuse_git_bare_fs.repotools_dulwich import get_repo_data
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                info = get_repo_data(
                    os.path.join(tmpdir, serverdir, reponame), b'master')
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            act_time = int(time.time())
            # run tests
            info = get_repo_data(
                os.path.join(tmpdir, serverdir, reponame), b'master')
            self.assertIsInstance(info, tuple)
            self.assertEqual(
                info[1], 'b213332fda65de4d2848a98e01f43d689cccbe6d')
            self.assertTrue(info[2] - 1 <= act_time)
            self.assertTrue(info[2] >= act_time - 1)
            info = True
            with self.assertWarns(UserWarning):
                info = get_repo_data(
                    os.path.join(tmpdir, serverdir, reponame), b'main')
            self.assertFalse(info)

    def test_get_size_of_blob(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12

        This tests runs only if the python module dulwich is available.
        It tests the tool/function get_size_of_blob from the module
        py_fuse_git_bare_fs.repotools_dulwich

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_dulwich.py \
            PyFuseGitBareFsRepotoolsDulwich.test_get_size_of_blob
        """
        # pylint: disable = unused-variable, unused-import
        try:
            import dulwich
        except ModuleNotFoundError:
            self.skipTest('python module dulwich not available')
            return
        from py_fuse_git_bare_fs.repotools_dulwich import get_size_of_blob
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                info = get_size_of_blob(
                    os.path.join(tmpdir, serverdir, reponame),
                    b'2e65efe2a145dda7ee51d1741299f848e5bf752e')
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            # run tests
            self.assertEqual(
                get_size_of_blob(os.path.join(tmpdir, serverdir, reponame),
                                 b'2e65efe2a145dda7ee51d1741299f848e5bf752e'),
                1)

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
