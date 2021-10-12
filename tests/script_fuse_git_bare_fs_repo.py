"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs repo'

You can run this file directly::

  env python3 script_fuse_git_bare_fs_repo.py

  pytest-3 script_fuse_git_bare_fs_repo.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_repo.py \
    ScriptFuseGitBareFsRepo.test_fuse_git_bare_fs_repo1

  pytest-3 -k test_fuse_git_bare_fs_repo1 script_fuse_git_bare_fs_repo.py
"""

import os
import re
import subprocess
import tempfile
import time
import unittest


class ScriptFuseGitBareFsRepo(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-10-12
    """

    def test_fuse_git_bare_fs_repo1(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-05

        This test creates a repo, put some files in and
        mount it, check for files.

        env python3 script_fuse_git_bare_fs_repo.py \
          ScriptFuseGitBareFsRepo.test_fuse_git_bare_fs_repo1

        pytest-3 -k test_fuse_git_bare_fs_repo1 script_fuse_git_bare_fs_repo.py
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            subprocess.run(
                ['git init --bare ' + reponame],
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
            cpi = subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'a', 'b', 'd', 'l'})
            # read data
            with open(os.path.join(tmpdir, mountpointdir, 'a')) as fd:
                data = fd.read()
            self.assertEqual(data, 'a\n')
            # clean up
            cpi.terminate()
            cpi.wait(timeout=3)
            cpi.kill()
            cpi.stdout.close()
            cpi.stderr.close()

    def test_fuse_git_bare_fs_repo2(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12

        This test creates a repo, put some files in and
        mount it, check for files.

        env python3 script_fuse_git_bare_fs_repo.py \
          ScriptFuseGitBareFsRepo.test_fuse_git_bare_fs_repo2

        pytest-3 -k test_fuse_git_bare_fs_repo2 script_fuse_git_bare_fs_repo.py
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            subprocess.run(
                ['git init --bare ' + reponame],
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
            cpi = subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            cp_ls = subprocess.run(
                ['ls -g -G'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, mountpointdir),
                timeout=3, check=True)
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'a', 'b', 'd', 'l'})
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

    def test_fuse_git_bare_fs_repo_daemon1(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-26

        This test creates a repo, put some files in and
        mount it, check for fiels.
        """
        # pylint: disable=invalid-name,too-many-statements
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            subprocess.run(
                ['git init --bare ' + reponame],
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
                ['fuse_git_bare_fs repo -daemon ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.2 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
                time.sleep(0.1)
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'a', 'b', 'd', 'l'})
            file_status = dict()
            for filename in ['.', 'a', 'b', 'l', 'd', 'd/c']:
                file_status[filename] = os.lstat(
                    os.path.join(tmpdir, mountpointdir, filename))
            for filename in ['.', 'd']:
                self.assertEqual(file_status[filename].st_mode, 16877)
                self.assertEqual(file_status[filename].st_size, 4096)
            for filename in ['a', 'b']:
                self.assertEqual(file_status[filename].st_mode, 33188)
                self.assertEqual(file_status[filename].st_size, 2)
            for filename in ['l']:
                self.assertEqual(file_status[filename].st_mode, 41471)
                self.assertEqual(file_status[filename].st_size, 1)
            for filename in ['d/c']:
                self.assertEqual(file_status[filename].st_mode, 33188)
                self.assertEqual(file_status[filename].st_size, 4)
            for filename in ['.', 'a', 'b', 'l', 'd', 'd/c']:
                self.assertEqual(file_status[filename].st_uid, os.geteuid())
                self.assertEqual(file_status[filename].st_gid, os.getegid())
            for filename in ['a', 'b']:
                with open(os.path.join(tmpdir, mountpointdir, filename)) as fd:
                    data = fd.read()
                self.assertEqual(data, filename + '\n')
            for filename in ['l']:
                with open(os.path.join(tmpdir, mountpointdir, filename)) as fd:
                    data = fd.read()
                self.assertEqual(data, 'a\n')
            for filename in ['d/c']:
                with open(os.path.join(tmpdir, mountpointdir, filename)) as fd:
                    data = fd.read()
                self.assertEqual(data, 'abc\n')
            with self.assertRaises(FileNotFoundError):
                file_status = os.lstat(
                    os.path.join(tmpdir, mountpointdir, 'foo'))
            # adapt data
            subprocess.run(
                ['ln -s d/c foo; git add foo; git commit -m foo; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # further tests: readdir
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'a', 'b', 'd', 'l', 'foo'})
            # adapt data
            subprocess.run(
                ['ln -s d/c bar; git add bar; git commit -m bar; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # further tests: getattr
            file_status = os.lstat(
                os.path.join(tmpdir, mountpointdir, 'bar'))
            self.assertEqual(file_status.st_mode, 41471)
            self.assertEqual(file_status.st_size, 3)
            self.assertEqual(file_status.st_uid, os.geteuid())
            self.assertEqual(file_status.st_gid, os.getegid())
            with open(os.path.join(tmpdir, mountpointdir, 'bar')) as fd:
                data = fd.read()
            self.assertEqual(data, 'abc\n')
            # adapt data
            subprocess.run(
                ['echo abc..xyz>baz; '
                 'git add baz; git commit -m baz; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # further tests:
            # read (but did getattr before; should be tested on module)
            with open(os.path.join(tmpdir, mountpointdir, 'baz')) as fd:
                data = fd.read()
            self.assertEqual(data, 'abc..xyz\n')
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_repo_daemon2(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-26

        This test creates a repo, put some files in and
        mount it, check for files.

        You can run this test directly::

          env python3 script_fuse_git_bare_fs_repo.py \
            ScriptFuseGitBareFsRepo.test_fuse_git_bare_fs_repo_daemon2
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
                ['git init --bare ' + reponame],
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
                ['fuse_git_bare_fs repo -root_object foo -daemon ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            time.sleep(0.3)
            # adapt data
            subprocess.run(
                ['git branch foo; git checkout foo; echo "f">f;'
                 'git rm -r a b l d; git add f; git commit -m f; '
                 'git push --set-upstream origin foo'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # run tests
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                set(['f']))
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
