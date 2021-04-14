"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-14
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

aggregation of tests

run with: env python3 setup.py run_unittest
"""


import unittest


class test_scripts_executable(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-14
    """

    def test_script_fuse_git_bare_fs_executable(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-14
        """
        import subprocess
        for cmd in ["fuse_git_bare_fs.py -h", "fuse_git_bare_fs.py repo -h",
                    "fuse_git_bare_fs.py tree -h"]:
            cp = subprocess.run(
                [cmd],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, timeout=3, check=True)
            # check at least minimal help output
            self.assertTrue(len(cp.stdout) >= 775)
            # check begin of help output
            self.assertTrue(cp.stdout.startswith(b'usage: fuse_git_bare_fs.py'))
            # check end of help output
            self.assertTrue(cp.stdout.endswith(
                b'License: ' + \
                b'GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.\n'))

def scripts(suite):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-03-04
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    add tests for the scripts
    """
    print('add tests for the scripts')
    loader = unittest.defaultTestLoader
    suite.addTest(loader.loadTestsFromTestCase(test_scripts_executable))
