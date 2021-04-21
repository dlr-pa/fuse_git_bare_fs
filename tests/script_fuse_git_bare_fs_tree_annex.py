"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-21
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs.py tree -get_user_list_from_annex'

You can run this file directly::

  env python3 script_fuse_git_bare_fs_tree_annex.py

  pytest-3 script_fuse_git_bare_fs_tree_annex.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_tree_annex.py script_fuse_git_bare_fs_tree_annex.test_fuse_git_bare_fs_tree_annex

  pytest-3 -k test_fuse_git_bare_fs_tree_annex script_fuse_git_bare_fs_tree_annex.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


class script_fuse_git_bare_fs_tree_annex(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-21
    """

    def test_fuse_git_bare_fs_tree_annex(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-21
        """
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'create_git_annex_test_env')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data',
                    'create_git_annex_test_env')
            shutil.copy(src_file_name,
                        os.path.join(tmpdir, 'create_git_annex_test_env'))
            cp = subprocess.run(
                [os.path.join(tmpdir, 'create_git_annex_test_env')],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            cp = subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs.py tree ' + serverdir + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir)
            t0 = time.time()
            while time.time() - t0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if len(os.listdir(os.path.join(tmpdir, mountpointdir))) > 0:
                    break
                time.sleep(0.1)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir))),
                {'repo1', 'repo2', 'repo3'})
            repo3 = os.path.join(tmpdir, mountpointdir, 'repo3')
            self.assertEqual(set(os.listdir(repo3)), {'f1', 'f2', 'f3'})
            with open(os.path.join(repo3, 'f1')) as fd:
                data = fd.read()
            self.assertEqual(data, 'f1\n')
            with open(os.path.join(repo3, 'f2')) as fd:
                data = fd.read()
            self.assertEqual(data, 'f2\n')
            with self.assertRaises(FileNotFoundError):
                with open(os.path.join(repo3, 'f3')) as fd:
                    data = fd.read()
            # clean up
            cp.terminate()
            cp.wait(timeout=3)
            cp.kill()
            cp.stdout.close()
            cp.stderr.close()
            cp = subprocess.run(
                ['chmod -R +w *'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=3, check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
