"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-03-31, 2023-04-04, 2023-04-20
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

try:
    from .prepare_simple_test_environment import PrepareSimpleTestEnvironment
except (ModuleNotFoundError, ImportError):
    from prepare_simple_test_environment import PrepareSimpleTestEnvironment

try:
    from .terminate_wait_kill import _terminate_wait_kill
except (ModuleNotFoundError, ImportError):
    from terminate_wait_kill import _terminate_wait_kill

try:
    from .list_dir_compare import ListDirCompare
except (ModuleNotFoundError, ImportError):
    from list_dir_compare import ListDirCompare


class ScriptFuseGitBareFsRepo(
        unittest.TestCase, PrepareSimpleTestEnvironment, ListDirCompare):
    """
    :Author: Daniel Mohr
    :Date: 2023-03-31, 2023-04-04, 2023-04-20
    """

    def test_fuse_git_bare_fs_repo1(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31, 2023-04-04

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
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            # run tests
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                dt0 = time.time()
                while time.time() - dt0 < 3:
                    # wait up to 3 seconds for mounting
                    # typical it needs less than 0.4 seconds
                    if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                        break
                self.assertEqual(
                    set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                    {'a', 'b', 'd', 'l'})
                # read data
                joinedpath = os.path.join(tmpdir, mountpointdir, 'a')
                with open(joinedpath, encoding='utf-8') as fd:
                    data = fd.read()
                self.assertEqual(data, 'a\n')
                # clean up
                _terminate_wait_kill(cpi)

    def test_fuse_git_bare_fs_repo2(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31, 2023-04-04

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
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
            # run tests
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                dt0 = time.time()
                while time.time() - dt0 < 3:
                    # wait up to 3 seconds for mounting
                    # typical it needs less than 0.4 seconds
                    if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                        break
                self._list_dir_compare(
                    os.path.join(tmpdir, mountpointdir),
                    {'a', 'b', 'd', 'l'},
                    [b'total 0',
                     b'-rw-r--r-- 0 .+ a',
                     b'-rw-r--r-- 0 .+ b',
                     b'drwxr-xr-x 0 4096 .+ d',
                     b'lrwxrwxrwx 0 .+ l -> a'])
                _terminate_wait_kill(cpi)
                cpistdout, cpistderr = cpi.communicate()
                self.assertFalse(
                    bool(re.findall(b'error', cpistdout, flags=re.IGNORECASE)),
                    msg='stdout logs errror(s):\n' + cpistdout.decode())
                self.assertFalse(
                    bool(re.findall(b'error', cpistderr, flags=re.IGNORECASE)),
                    msg='stderr logs errror(s):\n' + cpistderr.decode())

    def test_fuse_git_bare_fs_repo3(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31, 2023-04-04

        This test creates a repo, put some files in and
        mount it to non existing directory and check the flag '-nofail'.

        env python3 script_fuse_git_bare_fs_repo.py \
          ScriptFuseGitBareFsRepo.test_fuse_git_bare_fs_repo3

        pytest-3 -k test_fuse_git_bare_fs_repo3 script_fuse_git_bare_fs_repo.py
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame,
                createdirs=[serverdir, clientdir])
            # run test: error
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                _terminate_wait_kill(cpi, sleepbefore=3)
                _, cpistderr = cpi.communicate()
                self.assertEqual(1, cpi.returncode)  # error return
                # print(f'cpistderr.decode() = "{cpistderr.decode()}"')
                self.assertTrue(
                    'fuse: bad mount point' in cpistderr.decode())
            # run test: nofail
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo -nofail ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                _terminate_wait_kill(cpi, sleepbefore=3)
                _, cpistderr = cpi.communicate()
                self.assertEqual(0, cpi.returncode)  # no error return
                self.assertTrue(bool(re.findall(
                    b'UserWarning: mount fail, try running without',
                    cpistderr)))
            # run test: no error
            for dirpath in [mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                _terminate_wait_kill(cpi, sleepbefore=3)
                self.assertEqual(0, cpi.returncode)  # no error return

    def test_fuse_git_bare_fs_repo4(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31, 2023-04-04

        This test creates a repo, put some files in and
        mount it to non existing directory and check the flag '-logfile'.

        env python3 script_fuse_git_bare_fs_repo.py \
          ScriptFuseGitBareFsRepo.test_fuse_git_bare_fs_repo4

        pytest-3 -k test_fuse_git_bare_fs_repo4 script_fuse_git_bare_fs_repo.py
        """
        # logfile
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        logfile = 'log.txt'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame,
                createdirs=[serverdir, clientdir])
            # run test: error
            self.assertFalse(os.path.isfile(os.path.join(serverdir, logfile)))
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo -logfile ' +
                 os.path.join(tmpdir, logfile) + ' ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                _terminate_wait_kill(cpi, sleepbefore=3)
                _, cpistderr = cpi.communicate()
                self.assertEqual(1, cpi.returncode)  # error return
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, logfile)))
            self.assertTrue(os.path.getsize(os.path.join(tmpdir, logfile)) > 0)
            os.remove(os.path.join(tmpdir, logfile))
            # run test: nofail
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo -nofail -logfile ' +
                 os.path.join(tmpdir, logfile) + ' ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                _terminate_wait_kill(cpi, sleepbefore=3)
                _, cpistderr = cpi.communicate()
                self.assertEqual(0, cpi.returncode)  # no error return
                self.assertTrue(bool(re.findall(
                    b'UserWarning: mount fail, try running without',
                    cpistderr)))
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, logfile)))
            self.assertTrue(os.path.getsize(os.path.join(tmpdir, logfile)) > 0)
            os.remove(os.path.join(tmpdir, logfile))
            # run test: no error
            for dirpath in [mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            with subprocess.Popen(
                ['exec ' + 'fuse_git_bare_fs repo -logfile ' +
                 os.path.join(tmpdir, logfile) + ' ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                dt0 = time.time()
                while time.time() - dt0 < 3:
                    # wait up to 3 seconds for mounting
                    # typical it needs less than 0.4 seconds
                    if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                        break
                _terminate_wait_kill(cpi)
                self.assertEqual(0, cpi.returncode)  # no error return
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, logfile)))
            self.assertTrue(os.path.getsize(os.path.join(tmpdir, logfile)) > 0)
            with open(os.path.join(tmpdir, logfile), encoding='utf-8') as fd:
                data = fd.read()
            self.assertFalse(
                bool(re.findall('error', data, flags=re.IGNORECASE)),
                msg='stdout logs errror(s):\n' + data)

    def test_fuse_git_bare_fs_repo_daemon1(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31, 2023-04-04

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
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
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
            file_status = {}
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
                joinedpath = os.path.join(tmpdir, mountpointdir, filename)
                with open(joinedpath, encoding='utf-8') as fd:
                    data = fd.read()
                self.assertEqual(data, filename + '\n')
            for filename in ['l']:
                joinedpath = os.path.join(tmpdir, mountpointdir, filename)
                with open(joinedpath, encoding='utf-8') as fd:
                    data = fd.read()
                self.assertEqual(data, 'a\n')
            for filename in ['d/c']:
                joinedpath = os.path.join(tmpdir, mountpointdir, filename)
                with open(joinedpath, encoding='utf-8') as fd:
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
            joinedpath = os.path.join(tmpdir, mountpointdir, 'bar')
            with open(joinedpath, encoding='utf-8') as fd:
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
            joinedpath = os.path.join(tmpdir, mountpointdir, 'baz')
            with open(joinedpath, encoding='utf-8') as fd:
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
        :Date: 2021-04-26, 2023-04-04

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
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame)
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

    def test_fuse_git_bare_fs_repo_daemon3(self):
        """
        :Author: Daniel Mohr
        :Date: 2022-01-13, 2023-04-04

        This test creates a repo, put some files in and
        mount it to non existing directory and check the flag '-nofail'.

        You can run this test directly::

          env python3 script_fuse_git_bare_fs_repo.py \
            ScriptFuseGitBareFsRepo.test_fuse_git_bare_fs_repo_daemon3
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame,
                createdirs=[serverdir, clientdir])
            # run test: error
            cpi = subprocess.run(
                ['fuse_git_bare_fs repo -root_object foo -daemon ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=False)
            time.sleep(1)
            self.assertEqual(1, cpi.returncode)  # error return
            # run test: nofail
            cpi = subprocess.run(
                ['fuse_git_bare_fs repo -root_object foo -daemon -nofail ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            time.sleep(3)
            # run test: no error
            for dirpath in [mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            cpi = subprocess.run(
                ['fuse_git_bare_fs repo -root_object foo -daemon -nofail ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            time.sleep(3)
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_repo_daemon4(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31, 2023-04-04, 2023-04-20

        This test creates a repo, put some files in and
        mount it to non existing directory and check the flag '-logfile'.

        You can run this test directly::

          env python3 script_fuse_git_bare_fs_repo.py \
            ScriptFuseGitBareFsRepo.test_fuse_git_bare_fs_repo_daemon4
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        logfile = 'log.txt'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            self._prepare_simple_test_environment1(
                tmpdir, serverdir, clientdir, mountpointdir, reponame,
                createdirs=[serverdir, clientdir])
            # run test: nofail
            subprocess.run(
                ['fuse_git_bare_fs repo -root_object foo ' +
                 '-daemon -nofail -logfile ' +
                 os.path.join(tmpdir, logfile) + ' ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            time.sleep(3)
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, logfile)))
            self.assertTrue(os.path.getsize(os.path.join(tmpdir, logfile)) > 0)
            os.remove(os.path.join(tmpdir, logfile))
            # run test: no error
            for dirpath in [mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            subprocess.run(
                ['fuse_git_bare_fs repo -root_object foo ' +
                 '-daemon -nofail -logfile ' +
                 os.path.join(tmpdir, logfile) + ' ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            time.sleep(3)
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, logfile)))
            self.assertTrue(os.path.getsize(os.path.join(tmpdir, logfile)) > 0)
            with open(os.path.join(tmpdir, logfile), encoding='utf-8') as fd:
                data = fd.read()
            self.assertFalse(
                bool(re.findall('error', data, flags=re.IGNORECASE)),
                msg='stdout logs errror(s):\n' + data)
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            time.sleep(0.1) # give time to unmount


if __name__ == '__main__':
    unittest.main(verbosity=2)
