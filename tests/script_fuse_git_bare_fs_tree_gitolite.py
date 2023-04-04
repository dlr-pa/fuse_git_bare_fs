"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-03-31, 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs tree -get_user_list_from_gitolite'

You can run this file directly::

  env python3 script_fuse_git_bare_fs_tree_gitolite.py

  pytest-3 script_fuse_git_bare_fs_tree_gitolite.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_tree_gitolite.py \
    ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite1

  pytest-3 -k test_fuse_git_bare_fs_tree_gitolite1 \
    script_fuse_git_bare_fs_tree_gitolite.py
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


class ScriptFuseGitBareFsTreeGitolite(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2023-03-31
    """

    def test_fuse_git_bare_fs_tree_gitolite1(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31

        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite1

        pytest-3 -k test_fuse_git_bare_fs_tree_gitolite1 \
          script_fuse_git_bare_fs_tree_gitolite.py
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'gitolite')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data', 'gitolite')
            shutil.copy(src_file_name, os.path.join(tmpdir, 'gitolite'))
            subprocess.run(
                [os.path.join(tmpdir, 'gitolite') + ' createenv'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            call_cmd = 'exec ' + 'fuse_git_bare_fs tree'
            call_cmd += ' -get_user_list_from_gitolite -provide_htaccess '
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            with subprocess.Popen(
                    call_cmd,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                dt0 = time.time()
                while time.time() - dt0 < 3:
                    # wait up to 3 seconds for mounting
                    # typical it needs less than 0.4 seconds
                    if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                        break
                    time.sleep(0.1)
                self.assertEqual(
                    set(os.listdir(
                        os.path.join(tmpdir, mountpointdir))),
                    {'user1', 'user2'})
                _terminate_wait_kill(cpi)

    def test_fuse_git_bare_fs_tree_gitolite2(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31

        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite2

        pytest-3 -k test_fuse_git_bare_fs_tree_gitolite2 \
          script_fuse_git_bare_fs_tree_gitolite.py
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'gitolite')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data', 'gitolite')
            shutil.copy(src_file_name, os.path.join(tmpdir, 'gitolite'))
            subprocess.run(
                os.path.join(tmpdir, 'gitolite') + ' createenv',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            call_cmd = 'exec fuse_git_bare_fs tree'
            call_cmd += ' -get_user_list_from_gitolite'
            call_cmd += ' -provide_htaccess'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite')
            call_cmd += ' -gitolite_user_file ' + os.path.join(tmpdir, 'users')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            with subprocess.Popen(
                    call_cmd,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                dt0 = time.time()
                while time.time() - dt0 < 3:
                    # wait up to 3 seconds for mounting
                    # typical it needs less than 0.4 seconds
                    if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                        break
                    time.sleep(0.1)
                self.assertEqual(
                    set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                    {'user1', 'user2'})
                joinedpath = os.path.join(tmpdir, 'users')
                with open(joinedpath, mode='w', encoding='utf-8') as fd:
                    fd.write('foo\nbar\nbaz')
                self.assertEqual(
                    set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                    {'user1', 'user2', 'foo', 'bar', 'baz'})
                with open(joinedpath, mode='w', encoding='utf-8') as fd:
                    fd.write('bar\nbaz')
                self.assertEqual(
                    set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                    {'user1', 'user2', 'bar', 'baz'})
                os.remove(os.path.join(tmpdir, 'users'))
                self.assertEqual(
                    set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                    {'user1', 'user2'})
                _terminate_wait_kill(cpi)

    def test_fuse_git_bare_fs_tree_gitolite3(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31


        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite3

        pytest-3 -k test_fuse_git_bare_fs_tree_gitolite3 \
          script_fuse_git_bare_fs_tree_gitolite.py
        """
        # pylint: disable = invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'gitolite')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data', 'gitolite')
            shutil.copy(src_file_name, os.path.join(tmpdir, 'gitolite'))
            subprocess.run(
                os.path.join(tmpdir, 'gitolite') + ' createenv',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            call_cmd = 'exec fuse_git_bare_fs tree'
            call_cmd += ' -get_user_list_from_gitolite'
            call_cmd += ' -provide_htaccess'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite')
            call_cmd += ' -gitolite_user_file ' + os.path.join(tmpdir, 'users')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            with subprocess.Popen(
                    call_cmd,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir) as cpi:
                dt0 = time.time()
                while time.time() - dt0 < 3:
                    # wait up to 3 seconds for mounting
                    # typical it needs less than 0.4 seconds
                    if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                        break
                    time.sleep(0.1)
                self.assertEqual(
                    set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                    {'user1', 'user2'})
                self.assertEqual(
                    set(os.listdir(
                        os.path.join(
                            tmpdir, mountpointdir, 'user1', 'repo2'))),
                    {'c'})
                # read data
                joinedpath = os.path.join(
                    tmpdir, mountpointdir, 'user1', 'repo2', 'c')
                with open(joinedpath, encoding='utf-8') as fd:
                    data = fd.read()
                self.assertEqual(data, 'c\n')
                _terminate_wait_kill(cpi)

    def test_fuse_git_bare_fs_tree_gitolite_daemon1(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31

        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite_daemon1
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'gitolite')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data', 'gitolite')
            shutil.copy(src_file_name, os.path.join(tmpdir, 'gitolite'))
            subprocess.run(
                [os.path.join(tmpdir, 'gitolite') + ' createenv'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            call_cmd = 'fuse_git_bare_fs tree -daemon'
            call_cmd += ' -get_user_list_from_gitolite -provide_htaccess'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            subprocess.run(
                call_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            time.sleep(0.1)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir))),
                {'user1', 'user2'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1'))),
                {'.htaccess', 'repo1', 'repo2'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user2'))),
                {'.htaccess', 'repo3'})
            for username in ['user1', 'user2']:
                joinedpath = os.path.join(
                    tmpdir, mountpointdir, username, '.htaccess')
                with open(joinedpath, encoding='utf-8') as fd:
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
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_tree_gitolite_daemon2(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-23

        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite_daemon2
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'gitolite')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data', 'gitolite')
            shutil.copy(src_file_name, os.path.join(tmpdir, 'gitolite'))
            subprocess.run(
                os.path.join(tmpdir, 'gitolite') + ' createenv',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            call_cmd = 'fuse_git_bare_fs tree -daemon'
            call_cmd += ' -get_user_list_from_gitolite'
            call_cmd += ' -provide_htaccess'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite')
            call_cmd += ' -gitolite_user_file ' + os.path.join(tmpdir, 'users')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            subprocess.run(
                call_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
                time.sleep(0.1)
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'user1', 'user2'})
            joinedpath = os.path.join(tmpdir, 'users')
            with open(joinedpath, mode='w', encoding='utf-8') as fd:
                fd.write('foo\nbar\nbaz')
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'user1', 'user2', 'foo', 'bar', 'baz'})
            with open(joinedpath, mode='w', encoding='utf-8') as fd:
                fd.write('bar\nbaz')
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'user1', 'user2', 'bar', 'baz'})
            os.remove(os.path.join(tmpdir, 'users'))
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'user1', 'user2'})
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_tree_gitolite_daemon3(self):
        """
        :Author: Daniel Mohr
        :Date: 2023-03-31

        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite_daemon3
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            src_file_name = os.path.join('data', 'gitolite')
            if not os.path.isfile(src_file_name):
                src_file_name = os.path.join(os.path.dirname(
                    sys.modules['tests'].__file__), 'data', 'gitolite')
            shutil.copy(src_file_name, os.path.join(tmpdir, 'gitolite'))
            subprocess.run(
                [os.path.join(tmpdir, 'gitolite') + ' createenv'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            call_cmd = 'fuse_git_bare_fs tree -daemon'
            call_cmd += ' -get_user_list_from_gitolite -provide_htaccess'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            subprocess.run(
                call_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            time.sleep(0.1)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir))),
                {'user1', 'user2'})
            for username in ['user1', 'user2']:
                joinedpath = os.path.join(
                    tmpdir, mountpointdir, username, '.htaccess')
                with open(joinedpath, mode='r', encoding='utf-8') as fd:
                    htaccess_content = fd.read().splitlines()
                self.assertEqual(htaccess_content[0],
                                 'Require user ' + username)
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            # run tests
            joinedpath = os.path.join(tmpdir, 'htaccess_template.txt')
            with open(joinedpath, mode='w', encoding='utf-8') as fd:
                fd.write('# comment\n')
            call_cmd = 'fuse_git_bare_fs tree -daemon'
            call_cmd += ' -get_user_list_from_gitolite -provide_htaccess'
            call_cmd += ' -htaccess_template htaccess_template.txt'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            subprocess.run(
                call_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            time.sleep(0.1)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir))),
                {'user1', 'user2'})
            for username in ['user1', 'user2']:
                joinedpath = os.path.join(
                    tmpdir, mountpointdir, username, '.htaccess')
                with open(joinedpath, mode='r', encoding='utf-8') as fd:
                    htaccess_content = fd.read().splitlines()
                self.assertEqual(htaccess_content[0], '# comment')
                self.assertEqual(htaccess_content[1],
                                 'Require user ' + username)
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_tree_gitolite_daemon4(self):
        """
        :Author: Daniel Mohr
        :Date: 2022-02-24

        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite_daemon4
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for file_name in ['gitolite', 'gitolite2']:
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
            # repo1 not known by simulated gitolite command
            shutil.copy(os.path.join(tmpdir, 'gitolite2'),
                        os.path.join(tmpdir, 'gitolite1'))
            call_cmd = 'fuse_git_bare_fs tree -daemon'
            call_cmd += ' -get_user_list_from_gitolite -provide_htaccess'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite1')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            subprocess.run(
                call_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            time.sleep(0.1)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1'))),
                {'.htaccess', 'repo2', 'repo3'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user2'))),
                {'.htaccess'})
            # repo1 now known by simulated gitolite command
            shutil.copy(os.path.join(tmpdir, 'gitolite'),
                        os.path.join(tmpdir, 'gitolite1'))
            # update hash of gitolite-admin repo
            cmd = 'git commit -m foo --allow-empty ; git push'
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,
                cwd=os.path.join(tmpdir, clientdir, 'gitolite-admin'),
                timeout=3, check=False)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1'))),
                {'.htaccess', 'repo1', 'repo2'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user2'))),
                {'.htaccess', 'repo3'})
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_tree_gitolite_daemon5(self):
        """
        :Author: Daniel Mohr
        :Date: 2022-02-24

        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite_daemon5
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for file_name in ['gitolite', 'gitolite2']:
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
            # repo1 not known by simulated gitolite command
            shutil.copy(os.path.join(tmpdir, 'gitolite2'),
                        os.path.join(tmpdir, 'gitolite1'))
            call_cmd = 'fuse_git_bare_fs tree -daemon'
            call_cmd += ' -get_user_list_from_gitolite -provide_htaccess'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite1')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            subprocess.run(
                call_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            time.sleep(0.1)
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1'))),
                {'.htaccess', 'repo2', 'repo3'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user2'))),
                {'.htaccess'})
            # repo1 now known by simulated gitolite command
            shutil.copy(os.path.join(tmpdir, 'gitolite'),
                        os.path.join(tmpdir, 'gitolite1'))
            # update hash of gitolite-admin repo should not be necessary
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1'))),
                {'.htaccess', 'repo1', 'repo2'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user2'))),
                {'.htaccess', 'repo3'})
            # back to gitolite2
            shutil.copy(os.path.join(tmpdir, 'gitolite2'),
                        os.path.join(tmpdir, 'gitolite1'))
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user1'))),
                {'.htaccess', 'repo2', 'repo3'})
            self.assertEqual(
                set(os.listdir(
                    os.path.join(tmpdir, mountpointdir, 'user2'))),
                {'.htaccess'})
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_tree_gitolite_daemon6(self):
        """
        :Author: Daniel Mohr
        :Date: 2022-02-28

        env python3 script_fuse_git_bare_fs_tree_gitolite.py \
          ScriptFuseGitBareFsTreeGitolite.test_fuse_git_bare_fs_tree_gitolite_daemon6
        """
        # pylint: disable=invalid-name
        serverdir = 'server'
        mountpointdir = 'mountpoint'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for file_name in ['gitolite', 'gitolite2']:
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
            # repo1 not known by simulated gitolite command
            shutil.copy(os.path.join(tmpdir, 'gitolite'),
                        os.path.join(tmpdir, 'gitolite1'))
            call_cmd = 'fuse_git_bare_fs tree -daemon'
            call_cmd += ' -get_user_list_from_gitolite -provide_htaccess'
            call_cmd += ' -gitolite_cmd ' + os.path.join(tmpdir, 'gitolite1')
            call_cmd += ' ' + serverdir + ' ' + mountpointdir
            subprocess.run(
                call_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            dt0 = time.time()
            while time.time() - dt0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if bool(os.listdir(os.path.join(tmpdir, mountpointdir))):
                    break
            time.sleep(0.1)
            path_content = (
                (os.path.join(tmpdir, mountpointdir, 'user1'),
                 {'.htaccess', 'repo1', 'repo2'}),
                (os.path.join(tmpdir, mountpointdir, 'user1', 'repo1'),
                 {'b'}),
                (os.path.join(tmpdir, mountpointdir, 'user1', 'repo2'),
                 {'c'}),
                (os.path.join(tmpdir, mountpointdir, 'user2'),
                 {'.htaccess', 'repo3'}),
                (os.path.join(tmpdir, mountpointdir, 'user2', 'repo3'),
                 {'d'})
            )
            for (path, content) in path_content:
                self.assertEqual(set(os.listdir(path)), content)
            # change access to repos
            shutil.copy(os.path.join(tmpdir, 'gitolite2'),
                        os.path.join(tmpdir, 'gitolite1'))
            path_content = (
                (os.path.join(tmpdir, mountpointdir, 'user1'),
                 {'.htaccess', 'repo2', 'repo3'}),
                (os.path.join(tmpdir, mountpointdir, 'user1', 'repo2'),
                 {'c'}),
                (os.path.join(tmpdir, mountpointdir, 'user1', 'repo3'),
                 {'d'}),
                (os.path.join(tmpdir, mountpointdir, 'user2'),
                 {'.htaccess'}),
            )
            for (path, content) in path_content:
                self.assertEqual(set(os.listdir(path)), content)
            path_content_error = (
                (os.path.join(tmpdir, mountpointdir, 'user1', 'repo1'),
                 {'b'}),
                (os.path.join(tmpdir, mountpointdir, 'user2', 'repo3'),
                 {'d'})
            )
            for (path, content) in path_content_error:
                with self.assertRaises(FileNotFoundError):
                    self.assertEqual(set(os.listdir(path)), content)
            # remove mount
            subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
