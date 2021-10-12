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
    # pylint: disable = bad-option-value, import-outside-toplevel

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
                    b'master', re.compile(r' ([0-9]+) [0-9+-]+$'))
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            act_time = int(time.time())
            # run tests
            info = get_repo_data(
                os.path.join(tmpdir, serverdir, reponame),
                b'master', re.compile(r' ([0-9]+) [0-9+-]+$'))
            self.assertIsInstance(info, tuple)
            self.assertEqual(
                info[1], 'b213332fda65de4d2848a98e01f43d689cccbe6d')
            self.assertTrue(info[2] - 1 <= act_time)
            self.assertTrue(info[2] >= act_time - 1)
            info = True
            with self.assertWarns(UserWarning):
                info = get_repo_data(
                    os.path.join(tmpdir, serverdir, reponame),
                    b'main', re.compile(r' ([0-9]+) [0-9+-]+$'))
            self.assertFalse(info)

    def test_get_size_of_blob(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12

        It tests the tool/function get_size_of_blob from the module
        py_fuse_git_bare_fs.repotools_git

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_git.py \
            PyFuseGitBareFsRepotoolsGit.test_get_size_of_blob
        """
        from py_fuse_git_bare_fs.repotools_git import get_size_of_blob
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                get_size_of_blob(
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
        :Date: 2021-10-12

        It tests the tool/function get_tree from the module
        py_fuse_git_bare_fs.repotools_git

        you can run only one test, e. g.:

          env python3 py_fuse_git_bare_fs_repotools_git.py \
            PyFuseGitBareFsRepotoolsGit.test_get_tree
        """
        import re
        from py_fuse_git_bare_fs.repotools_git import get_tree
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_content_regpat = re.compile(
                r'^([0-9]+) (commit|tree|blob|tag) ([0-9a-f]+)\t(.+)$')
            with self.assertRaises(FileNotFoundError):
                tree = get_tree(
                    os.path.join(tmpdir, serverdir, reponame),
                    'b213332fda65de4d2848a98e01f43d689cccbe6d',
                    tree_content_regpat)
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            # run tests
            tree = get_tree(
                os.path.join(tmpdir, serverdir, reponame),
                'b213332fda65de4d2848a98e01f43d689cccbe6d',
                tree_content_regpat)
            self.assertIsInstance(tree, dict)
            self.assertEqual(set(tree.keys()), {'/', '/d'})
            self.assertIsInstance(tree['/'], dict)
            self.assertEqual(set(tree['/'].keys()), {'listdir', 'blobs'})
            self.assertIsInstance(tree['/']['listdir'], list)
            self.assertEqual(set(tree['/']['listdir']),
                             {'a', 'b', 'd', 'l'})
            self.assertIsInstance(tree['/']['blobs'], dict)
            self.assertEqual(set(tree['/']['blobs'].keys()),
                             {'a', 'b', 'l'})
            for filename, hashstr, mode in \
                [('a', '78981922613b2afb6025042ff6bd878ac1994e85', '100644'),
                 ('b', '61780798228d17af2d34fce4cfbdf35556832472', '100644'),
                 ('l', '2e65efe2a145dda7ee51d1741299f848e5bf752e', '120000')]:
                self.assertIsInstance(tree['/']['blobs'][filename], dict)
                self.assertEqual(set(tree['/']['blobs'][filename].keys()),
                                 {'hash', 'mode'})
                self.assertEqual(tree['/']['blobs'][filename]['hash'],
                                 hashstr)
                self.assertEqual(tree['/']['blobs'][filename]['mode'],
                                 mode)


if __name__ == '__main__':
    unittest.main(verbosity=2)
