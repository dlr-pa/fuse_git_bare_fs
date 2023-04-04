"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-03-31, 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs tree' regarding git-annex files

You can run this file directly::

  env python3 script_fuse_git_bare_fs_tree_annex.py

  pytest-3 script_fuse_git_bare_fs_tree_annex.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_tree_annex.py \
    ScriptFuseGitBareFsTreeAnnex.test_fuse_git_bare_fs_tree_annex

  pytest-3 -k test_fuse_git_bare_fs_tree_annex \
    script_fuse_git_bare_fs_tree_annex.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

try:
    from .terminate_wait_kill import _terminate_wait_kill
except (ModuleNotFoundError, ImportError):
    from terminate_wait_kill import _terminate_wait_kill


class ScriptFuseGitBareFsTreeAnnex(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2023-03-31
    """

    def test_fuse_git_bare_fs_tree_annex(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'create_git_annex_test_env')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(
                    os.path.dirname(
                        sys.modules['tests'].__file__),
                    'data', 'create_git_annex_test_env')
            shutil.copy(src_file_name,
                        os.path.join(tmpdir, 'create_git_annex_test_env'))
            subprocess.run(
                [os.path.join(tmpdir, 'create_git_annex_test_env')],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=6, check=True)
            # run tests
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs tree ' + serverdir + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                t0 = time.time()
                while time.time() - t0 < 3:
                    # wait up to 3 seconds for mounting
                    # typical it needs less than 0.4 seconds
                    if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                        break
                    time.sleep(0.1)
                self.assertEqual(
                    set(os.listdir(
                        os.path.join(tmpdir, mountpointdir))),
                    {'repo1', 'repo2', 'repo3'})
                # test content of repo1:
                repo1 = os.path.join(tmpdir, mountpointdir, 'repo1')
                self.assertEqual(set(os.listdir(repo1)), {'f1', 'f2', 'f3'})
                for filename in ['f1', 'f2']:
                    joinedpath = os.path.join(repo1, filename)
                    with open(joinedpath, encoding='utf-8') as fd:
                        data = fd.read()
                    self.assertEqual(data, filename + '\n')
                with self.assertRaises(FileNotFoundError):
                    joinedpath = os.path.join(repo1, 'f3')
                    with open(joinedpath, encoding='utf-8') as fd:
                        data = fd.read()
                # test content of repo2:
                repo2 = os.path.join(tmpdir, mountpointdir, 'repo2', 'repo2')
                self.assertEqual(set(os.listdir(repo2)), {'f1', 'f2', 'f3'})
                # check f1 is link:
                self.assertEqual(
                    os.lstat(os.path.join(repo2, 'f1')).st_mode, 16877)
                # check git annex file in subdirectory,
                # e. g.: f1 -> ../.git/annex/objects/...
                joinedpath = os.path.join(repo2, 'f1', 'f1')
                with open(joinedpath, encoding='utf-8') as fd:
                    data = fd.read()
                self.assertEqual(data, 'f1\n')
                # check f2 is executable:
                self.assertEqual(os.lstat(os.path.join(repo2, 'f2')).st_mode,
                                 33261)
                # check f3 is symbolic link:
                self.assertEqual(
                    os.lstat(os.path.join(repo2, 'f3')).st_mode, 41471)
                # clean up:
                _terminate_wait_kill(cpi, timeout=6)
            subprocess.run(
                ['chmod -R +w *'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=6, check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
