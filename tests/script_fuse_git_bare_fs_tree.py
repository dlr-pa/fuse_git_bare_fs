"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-03-31
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs tree'

You can run this file directly::

  env python3 script_fuse_git_bare_fs_tree.py

  pytest-3 script_fuse_git_bare_fs_tree.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_tree.py \
    ScriptFuseGitBareFsTree.test_fuse_git_bare_fs_tree1

  pytest-3 -k test_fuse_git_bare_fs_tree1 script_fuse_git_bare_fs_tree.py
"""

import os
import shutil
import re
import subprocess
import sys
import tempfile
import time
import unittest


def _prepare_test_environment(serverdir, clientdir, mountpointdir,
                              reponame1, reponame2, tmpdir):
    # pylint: disable=too-many-arguments
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


class ScriptFuseGitBareFsTree(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2023-03-31
    """

    def test_fuse_git_bare_fs_tree1(self):
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
            _prepare_test_environment(serverdir, clientdir, mountpointdir,
                                      reponame1, reponame2, tmpdir)
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
            # read data
            with open(os.path.join(
                    tmpdir, mountpointdir, reponame1, 'a')) as fd:
                data = fd.read()
            self.assertEqual(data, 'a\n')
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

    def test_fuse_git_bare_fs_tree2(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12
        """
        # pylint: disable=too-many-statements
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame1 = 'repo1'
        reponame2 = 'foo/repo2'
        with tempfile.TemporaryDirectory() as tmpdir:
            _prepare_test_environment(serverdir, clientdir, mountpointdir,
                                      reponame1, reponame2, tmpdir)
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
            cp_ls = subprocess.run(
                ['ls -g -G'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, mountpointdir, reponame1),
                timeout=3, check=True)
            cp_ls_stdout = cp_ls.stdout.split(sep=b'\n')
            self.assertEqual(cp_ls_stdout[0], b'total 0')
            self.assertTrue(
                bool(re.findall(b'-rw-r--r-- 0 .+ a', cp_ls_stdout[1])))
            self.assertTrue(
                bool(re.findall(b'-rw-r--r-- 0 .+ b', cp_ls_stdout[2])))
            self.assertTrue(
                bool(re.findall(b'drwxr-xr-x 0 4096 .+ d', cp_ls_stdout[3])))
            self.assertTrue(
                bool(re.findall(b'lrwxrwxrwx 0 .+ l -> a', cp_ls_stdout[4])))
            # read data
            with open(os.path.join(
                    tmpdir, mountpointdir, reponame1, 'a')) as fd:
                data = fd.read()
            self.assertEqual(data, 'a\n')
            cpi.terminate()
            cpi.wait(timeout=3)
            cpi.kill()
            cpistdout, cpistderr = cpi.communicate()
            self.assertFalse(
                bool(re.findall(b'error', cpistdout, flags=re.IGNORECASE)),
                msg='stdout logs errror(s):\n' + cpistdout.decode())
            self.assertFalse(
                bool(re.findall(b'error', cpistderr, flags=re.IGNORECASE)),
                msg='stderr logs errror(s):\n' + cpistderr.decode())
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
            cp_ls = subprocess.run(
                ['ls -g -G'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, mountpointdir, reponame1),
                timeout=3, check=True)
            cp_ls_stdout = cp_ls.stdout.split(sep=b'\n')
            self.assertEqual(cp_ls_stdout[0], b'total 0')
            self.assertTrue(
                bool(re.findall(b'-rw-r--r-- 0 .+ a', cp_ls_stdout[1])))
            self.assertTrue(
                bool(re.findall(b'-rw-r--r-- 0 .+ b', cp_ls_stdout[2])))
            self.assertTrue(
                bool(re.findall(b'drwxr-xr-x 0 4096 .+ d', cp_ls_stdout[3])))
            self.assertTrue(
                bool(re.findall(b'lrwxrwxrwx 0 .+ l -> a', cp_ls_stdout[4])))
            # read data
            with open(os.path.join(
                    tmpdir, mountpointdir, reponame1, 'a')) as fd:
                data = fd.read()
            self.assertEqual(data, 'a\n')
            cpi.terminate()
            cpi.wait(timeout=3)
            cpi.kill()
            cpistdout, cpistderr = cpi.communicate()
            self.assertFalse(
                bool(re.findall(b'error', cpistdout, flags=re.IGNORECASE)),
                msg='stdout logs errror(s):\n' + cpistdout.decode())
            self.assertFalse(
                bool(re.findall(b'error', cpistderr, flags=re.IGNORECASE)),
                msg='stderr logs errror(s):\n' + cpistderr.decode())
            cpi.stdout.close()
            cpi.stderr.close()

    def test_fuse_git_bare_fs_tree_daemon1(self):
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

    def test_fuse_git_bare_fs_tree_daemon2(self):
        """
        :Author: Daniel Mohr
        :Date: 2022-01-13

        env python3 script_fuse_git_bare_fs_tree.py \
          ScriptFuseGitBareFsTree.test_fuse_git_bare_fs_tree_daemon2
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        logfile = 'log.txt'
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
                ['fuse_git_bare_fs tree -daemon -logfile ' +
                 os.path.join(tmpdir, logfile) + ' ' +
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
            # check log
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, logfile)))
            self.assertTrue(os.path.getsize(os.path.join(tmpdir, logfile)) > 0)
            with open(os.path.join(tmpdir, logfile)) as fd:
                data = fd.read()
            self.assertFalse(
                bool(re.findall('error', data, flags=re.IGNORECASE)),
                msg='stdout logs errror(s):\n' + data)

    def test_fuse_git_bare_fs_tree_daemon3(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31

        env python3 script_fuse_git_bare_fs_tree.py \
          ScriptFuseGitBareFsTree.test_fuse_git_bare_fs_tree_daemon3

        pytest-3 -k test_fuse_git_bare_fs_tree_daemon3 script_fuse_git_bare_fs_tree.py
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        logfile = 'log.txt'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for file_name in ['gitolite']:
                src_file_name = os.path.join('data', file_name)
                if not os.path.isfile(src_file_name):
                    src_file_name = os.path.join(os.path.dirname(
                        sys.modules['tests'].__file__), 'data', file_name)
                shutil.copy(src_file_name, os.path.join(tmpdir, file_name))
            subprocess.run(
                [os.path.join(tmpdir, 'gitolite') + ' createenv'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            subprocess.run(
                ['fuse_git_bare_fs tree -daemon -logfile ' +
                 os.path.join(tmpdir, logfile) + ' ' +
                 serverdir + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, serverdir))),
                {'repo1.git', 'repo2.git', 'repo3.git', 'gitolite-admin.git'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir))),
                {'repo1', 'repo2', 'repo3'})
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # check log
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, logfile)))
            self.assertTrue(os.path.getsize(os.path.join(tmpdir, logfile)) > 0)
            with open(os.path.join(tmpdir, logfile), encoding='utf-8') as fd:
                data = fd.read()
            self.assertFalse(
                bool(re.findall('error', data, flags=re.IGNORECASE)),
                msg='stdout logs errror(s):\n' + data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
