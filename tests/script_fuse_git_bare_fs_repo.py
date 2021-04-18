"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-18
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the script 'fuse_git_bare_fs.py repo'

You can run this file directly::

  env python3 script_fuse_git_bare_fs_repo.py

  pytest-3 script_fuse_git_bare_fs_repo.py

Or you can run only one test, e. g.::

  env python3 script_fuse_git_bare_fs_repo.py script_fuse_git_bare_fs_repo.test_fuse_git_bare_fs_repo

  pytest-3 -k test_fuse_git_bare_fs_repo script_fuse_git_bare_fs_repo.py
"""

import os
import subprocess
import tempfile
import time
import unittest


class script_fuse_git_bare_fs_repo(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-18
    """

    def test_fuse_git_bare_fs_repo(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-14

        This test creates a repo, put some files in and 
        mount it, check for files.
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            cp = subprocess.run(
                ['git init --bare ' + reponame],
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
                ['exec ' + 'fuse_git_bare_fs.py repo ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir)
            t0 = time.time()
            while time.time() - t0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.4 seconds
                if len(os.listdir(os.path.join(tmpdir, mountpointdir))) > 0:
                    break
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'a', 'b', 'd', 'l'})
            cp.terminate()
            cp.wait(timeout=3)
            cp.kill()
            cp.stdout.close()
            cp.stderr.close()

    def test_fuse_git_bare_fs_repo_daemon1(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-18

        This test creates a repo, put some files in and 
        mount it, check for fiels.
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            cp = subprocess.run(
                ['git init --bare ' + reponame],
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
                ['fuse_git_bare_fs.py repo -daemon ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            t0 = time.time()
            while time.time() - t0 < 3:  # wait up to 3 seconds for mounting
                # typical it needs less than 0.2 seconds
                if len(os.listdir(os.path.join(tmpdir, mountpointdir))) > 0:
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
                self.assertEqual(file_status[filename].st_mode, 16893)
                self.assertEqual(file_status[filename].st_size, 4096)
            for filename in ['a', 'b']:
                self.assertEqual(file_status[filename].st_mode, 33204)
                self.assertEqual(file_status[filename].st_size, 2)
            for filename in ['l']:
                self.assertEqual(file_status[filename].st_mode, 41471)
                self.assertEqual(file_status[filename].st_size, 1)
            for filename in ['d/c']:
                self.assertEqual(file_status[filename].st_mode, 33204)
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
            cp = subprocess.run(
                ['ln -s d/c foo; git add foo; git commit -m foo; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # further tests: readdir
            self.assertEqual(
                set(os.listdir(os.path.join(tmpdir, mountpointdir))),
                {'a', 'b', 'd', 'l', 'foo'})
            # adapt data
            cp = subprocess.run(
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
            cp = subprocess.run(
                ['echo abc..xyz>baz; git add baz; git commit -m baz; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # further tests:
            # read (but did getattr before; should be tested on module)
            with open(os.path.join(tmpdir, mountpointdir, 'baz')) as fd:
                data = fd.read()
            self.assertEqual(data, 'abc..xyz\n')
            # remove mount
            cp = subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)

    def test_fuse_git_bare_fs_repo_daemon2(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-18

        This test creates a repo, put some files in and 
        mount it, check for files.
        """
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            cp = subprocess.run(
                ['git init --bare ' + reponame],
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
                ['fuse_git_bare_fs.py repo -root_object foo -daemon ' +
                 os.path.join(serverdir, reponame) + ' ' +
                 mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)
            time.sleep(0.3)
            # adapt data
            cp = subprocess.run(
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
            cp = subprocess.run(
                ['fusermount -u ' + mountpointdir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir,
                timeout=3, check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
