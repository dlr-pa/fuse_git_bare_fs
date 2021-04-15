"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-15
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs.py tree'

You can run this file directly::

  env python3 script_fuse_git_bare_fs_tree.py

  pytest-3 script_fuse_git_bare_fs_tree.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_tree.py script_fuse_git_bare_fs_tree.test_fuse_git_bare_fs_tree

  pytest-3 -k test_fuse_git_bare_fs_tree script_fuse_git_bare_fs_tree.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


class script_fuse_git_bare_fs_tree(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-15
    """

    def test_fuse_git_bare_fs_tree(self):
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            cp = subprocess.run(
                ['git init --bare ' + reponame + '.git'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            cp = subprocess.run(
                ['git clone ../' + os.path.join(serverdir, reponame)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir),
                timeout=3, check=True)
            cp = subprocess.run(
                ['echo "a">a; echo "b">b; ln -s a l; mkdir d; echo "abc">d/c;'
                 'git add a b l d/c; git commit -m init; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # run tests
            cp = subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs.py tree ' +
                 serverdir + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir)
            t0 = time.time()
            while time.time() - t0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if len(os.listdir(os.path.join(tmpdir, mountpointdir))) > 0:
                    break
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, reponame))),
                {'a', 'b', 'd', 'l'})
            cp.terminate()
            cp.wait(timeout=3)
            cp.kill()
            cp.stdout.close()
            cp.stderr.close()

    def test_fuse_git_bare_fs_tree_daemon(self):
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            cp = subprocess.run(
                ['git init --bare ' + reponame + '.git'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            cp = subprocess.run(
                ['git clone ../' + os.path.join(serverdir, reponame)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir),
                timeout=3, check=True)
            cp = subprocess.run(
                ['echo "a">a; echo "b">b; ln -s a l; mkdir d; echo "abc">d/c;'
                 'git add a b l d/c; git commit -m init; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # run tests
            cp = subprocess.run(
                ['fuse_git_bare_fs.py tree -daemon ' +
                 serverdir + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, reponame))),
                {'a', 'b', 'd', 'l'})
            # remove mount
            cp = subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_tree_gitolite(self):
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
