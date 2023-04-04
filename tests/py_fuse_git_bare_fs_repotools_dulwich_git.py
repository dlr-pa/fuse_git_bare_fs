"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
import tempfile


class PyFuseGitBareFsRepotoolsDulwichGitMixIn():
    """
    :Author: Daniel Mohr
    :Date: 2023-04-04
    """
    # * since this is unittesting import outside toplevel is OK
    # * since this is a mixin class no-member and too-few-public-methods is OK
    # pylint: disable = import-outside-toplevel
    # pylint: disable = no-member, too-few-public-methods

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
