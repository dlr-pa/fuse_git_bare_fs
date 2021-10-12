"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the tools in the module py_fuse_git_bare_fs.repotools_git

You can run this file directly:

  env python3 py_fuse_git_bare_fs_repotools_git.py

Or you can run only one test, e. g.:

  env python3 py_fuse_git_bare_fs_repotools_git.py \
    PyFuseGitBareFsRepotoolsGit.test_repotools_git_get_ref
"""

import os
import tempfile
import unittest

try:
    from .prepare_simple_test_environment import PrepareSimpleTestEnvironment
except ModuleNotFoundError:
    from prepare_simple_test_environment import PrepareSimpleTestEnvironment


class PyFuseGitBareFsRepotoolsGit(
        unittest.TestCase, PrepareSimpleTestEnvironment):
    """
    :Author: Daniel Mohr
    :Date: 2021-10-12
    """

    def test_get_ref(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12

        It tests the tool/function get_ref from the module
        py_fuse_git_bare_fs.repotools_git
        """
        from py_fuse_git_bare_fs.repotools_git import get_ref
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

        It tests the tool/function get_blob_data from the module
        py_fuse_git_bare_fs.repotools_git

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_git.py \
            PyFuseGitBareFsRepotoolsGit.test_repotools_git_get_blob_data
        """
        from py_fuse_git_bare_fs.repotools_git import get_blob_data
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                commit_hash = get_blob_data(
                    os.path.join(tmpdir, serverdir, reponame),
                    b'2e65efe2a145dda7ee51d1741299f848e5bf752e')
                print('\n\n', commit_hash, '\n\n')
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

        It tests the tool/function get_repo_data from the module
        py_fuse_git_bare_fs.repotools_git

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_git.py \
            PyFuseGitBareFsRepotoolsGit.test_repotools_git_get_repo_data
        """
        import re
        import time
        from py_fuse_git_bare_fs.repotools_git import get_repo_data
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                info = get_repo_data(
                    os.path.join(tmpdir, serverdir, reponame),
                    b'master', re.compile(r' ([0-9]+) [+\-0-9]+$'))
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            act_time = int(time.time())
            # run tests
            info = get_repo_data(
                os.path.join(tmpdir, serverdir, reponame),
                b'master', re.compile(r' ([0-9]+) [+\-0-9]+$'))
            self.assertIsInstance(info, tuple)
            self.assertEqual(
                info[1], 'b213332fda65de4d2848a98e01f43d689cccbe6d')
            self.assertTrue(info[2] - 1 <= act_time)
            self.assertTrue(info[2] >= act_time - 1)
            info = True
            with self.assertWarns(UserWarning):
                info = get_repo_data(
                    os.path.join(tmpdir, serverdir, reponame),
                    b'main', re.compile(r' ([0-9]+) [+\-0-9]+$'))
            self.assertFalse(info)


if __name__ == '__main__':
    unittest.main(verbosity=2)
