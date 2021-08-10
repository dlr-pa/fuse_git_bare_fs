"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-26
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs tree'

You can run this file directly::

  env python3 script_fuse_git_bare_fs_tree.py

  pytest-3 script_fuse_git_bare_fs_tree.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_tree.py \
    ScriptFuseGitBareFsTree.test_fuse_git_bare_fs_tree

  pytest-3 -k test_fuse_git_bare_fs_tree script_fuse_git_bare_fs_tree.py
"""

import os
import subprocess
import tempfile
import time
import unittest


class ScriptFuseGitBareFsTree(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-26
    """

    def test_fuse_git_bare_fs_tree(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-26
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame1 = 'repo1'
        reponame2 = 'foo/repo2'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir,
                            os.path.join(serverdir, 'foo'),
                            os.path.join(clientdir, 'foo')]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            subprocess.run(
                ['git init --bare ' + reponame1 + '.git'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            subprocess.run(
                ['git clone ../' + os.path.join(serverdir, reponame1)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir),
                timeout=3, check=True)
            subprocess.run(
                ['echo "a">a; echo "b">b; ln -s a l; mkdir d; echo "abc">d/c;'
                 'git add a b l d/c; git commit -m init; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame1),
                timeout=3, check=True)
            subprocess.run(
                ['git init --bare ' + reponame2 + '.git'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            subprocess.run(
                ['git clone ../../' + os.path.join(serverdir, reponame2)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, 'foo'),
                timeout=3, check=True)
            subprocess.run(
                ['echo "2">2;'
                 'git add 2; git commit -m init; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame2),
                timeout=3, check=True)
            # run tests (bare repositories)
            cpi = subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs tree ' +
                 serverdir + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, reponame1))),
                {'a', 'b', 'd', 'l'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, reponame2))),
                {'2'})
            cpi.terminate()
            cpi.wait(timeout=3)
            cpi.kill()
            cpi.stdout.close()
            cpi.stderr.close()
            # run tests (non bare repositories)
            cpi = subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs tree ' +
                 clientdir + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, reponame1))),
                {'a', 'b', 'd', 'l'})
            cpi.terminate()
            cpi.wait(timeout=3)
            cpi.kill()
            cpi.stdout.close()
            cpi.stderr.close()

    def test_fuse_git_bare_fs_tree_daemon(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-26
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            subprocess.run(
                ['git init --bare ' + reponame + '.git'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            subprocess.run(
                ['git clone ../' + os.path.join(serverdir, reponame)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir),
                timeout=3, check=True)
            subprocess.run(
                ['echo "a">a; echo "b">b; ln -s a l; mkdir d; echo "abc">d/c;'
                 'git add a b l d/c; git commit -m init; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # run tests
            subprocess.run(
                ['fuse_git_bare_fs tree -daemon ' +
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
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
