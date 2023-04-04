"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
import tempfile

try:
    from .prepare_simple_test_environment import PrepareSimpleTestEnvironment
except ModuleNotFoundError:
    from prepare_simple_test_environment import PrepareSimpleTestEnvironment


class PyFuseGitBareFsRepotoolsDulwichGitMixIn(PrepareSimpleTestEnvironment):
    """
    :Author: Daniel Mohr
    :Date: 2023-04-04
    """
    # * since this is unittesting import outside toplevel is OK
    # * since this is a mixin class no-member and too-few-public-methods is OK
    # pylint: disable = import-outside-toplevel
    # pylint: disable = no-member, too-few-public-methods

    def _test_get_ref(self, backend):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        It tests the tool/function get_ref from the module
        py_fuse_git_bare_fs.repotools_dulwich or from the module
        py_fuse_git_bare_fs.repotools_git depending on the choosen backend.

        It is used from `py_fuse_git_bare_fs_repotools_dulwich.py` and from
        `py_fuse_git_bare_fs_repotools_git.py`.
        """
        if backend == 'dulwich':
            # pylint: disable = unused-variable, unused-import
            try:
                import dulwich
            except ModuleNotFoundError:
                self.skipTest('python module dulwich not available')
                return
            from py_fuse_git_bare_fs.repotools_dulwich import get_ref
        elif backend == 'git':
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

    def _test_get_blob_data(self, backend):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12

        It tests the tool/function get_blob_data from the module
        py_fuse_git_bare_fs.repotools_dulwich or from the module
        py_fuse_git_bare_fs.repotools_git depending on the choosen backend.

        It is used from `py_fuse_git_bare_fs_repotools_dulwich.py` and from
        `py_fuse_git_bare_fs_repotools_git.py`.
        """
        if backend == 'dulwich':
            # pylint: disable = unused-variable, unused-import
            try:
                import dulwich
            except ModuleNotFoundError:
                self.skipTest('python module dulwich not available')
                return
            import re
            from py_fuse_git_bare_fs.repotools_dulwich import get_blob_data
        elif backend == 'git':
            import re
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

    def _test_get_repo_data(self, backend):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        It tests the tool/function get_repo_data from the module
        py_fuse_git_bare_fs.repotools_dulwich or from the module
        py_fuse_git_bare_fs.repotools_git depending on the choosen backend.

        It is used from `py_fuse_git_bare_fs_repotools_dulwich.py` and from
        `py_fuse_git_bare_fs_repotools_git.py`.
        """
        if backend == 'dulwich':
            # pylint: disable = unused-variable, unused-import
            try:
                import dulwich
            except ModuleNotFoundError:
                self.skipTest('python module dulwich not available')
                return
            import re
            import time
            from py_fuse_git_bare_fs.repotools_dulwich import get_repo_data
        elif backend == 'git':
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

    def _test_get_size_of_blob(self, backend):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        It tests the tool/function get_size_of_blob from the module
        py_fuse_git_bare_fs.repotools_dulwich or from the module
        py_fuse_git_bare_fs.repotools_git depending on the choosen backend.

        It is used from `py_fuse_git_bare_fs_repotools_dulwich.py` and from
        `py_fuse_git_bare_fs_repotools_git.py`.
        """
        if backend == 'dulwich':
            # pylint: disable = unused-variable, unused-import
            try:
                import dulwich
            except ModuleNotFoundError:
                self.skipTest('python module dulwich not available')
                return
            from py_fuse_git_bare_fs.repotools_dulwich import get_size_of_blob
        elif backend == 'git':
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

    def _test_get_tree(self, backend):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04

        It tests the tool/function get_tree from the module
        py_fuse_git_bare_fs.repotools_dulwich or from the module
        py_fuse_git_bare_fs.repotools_git depending on the choosen backend.

        It is used from `py_fuse_git_bare_fs_repotools_dulwich.py` and from
        `py_fuse_git_bare_fs_repotools_git.py`.
        """
        if backend == 'dulwich':
            # pylint: disable = unused-variable, unused-import
            try:
                import dulwich
            except ModuleNotFoundError:
                self.skipTest('python module dulwich not available')
                return
            import re
            from py_fuse_git_bare_fs.repotools_dulwich import get_tree
        elif backend == 'git':
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
