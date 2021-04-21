"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-21
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs.py tree -get_user_list_from_gitolite'

You can run this file directly::

  env python3 script_fuse_git_bare_fs_tree_gitolite.py

  pytest-3 script_fuse_git_bare_fs_tree_gitolite.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_tree_gitolite.py script_fuse_git_bare_fs_tree_gitolite.test_fuse_git_bare_fs_tree_gitolite

  pytest-3 -k test_fuse_git_bare_fs_tree_gitolite script_fuse_git_bare_fs_tree_gitolite.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


class script_fuse_git_bare_fs_tree_gitolite(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-21
    """

    def test_fuse_git_bare_fs_tree_gitolite(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-18
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'gitolite')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data', 'gitolite')
            shutil.copy(src_file_name, os.path.join(tmpdir, 'gitolite'))
            cp = subprocess.run(
                [os.path.join(tmpdir, 'gitolite') + ' createenv'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            cp = subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs.py tree -get_user_list_from_gitolite -provide_htaccess -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite') + ' ' +
                 serverdir + ' ' +
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
                {'user1', 'user2'})
            cp.terminate()
            cp.wait(timeout=3)
            cp.kill()
            cp.stdout.close()
            cp.stderr.close()

    def test_fuse_git_bare_fs_tree_gitolite_daemon(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-18
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'gitolite')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data', 'gitolite')
            shutil.copy(src_file_name, os.path.join(tmpdir, 'gitolite'))
            cp = subprocess.run(
                [os.path.join(tmpdir, 'gitolite') + ' createenv'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            cp = subprocess.run(
                ['fuse_git_bare_fs.py tree -daemon -get_user_list_from_gitolite -provide_htaccess -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite') + ' ' +
                 serverdir + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir))),
                {'user1', 'user2'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1'))),
                {'.htaccess', 'repo1', 'repo2', 'repo3'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user2'))),
                {'.htaccess', 'repo3'})
            for username in ['user1', 'user2']:
                with open(os.path.join(
                        tmpdir,
                        mountpointdir,
                        username,
                        '.htaccess')) as fd:
                    data = fd.read()
                self.assertEqual(data, 'Require user ' + username + '\n')
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1', 'repo1'))),
                {'b', })
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1', 'repo2'))),
                {'c', })
            # remove mount
            cp = subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
