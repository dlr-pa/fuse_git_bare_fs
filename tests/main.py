"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-26
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

aggregation of tests

run with:

env python3 setup.py run_unittest

or:

env python3 setup.py run_pytest
"""


import unittest


class TestModuleImport(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-14
    """

    def test_module_import(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-14

        env python3 main.py TestModuleImport.test_module_import
        """
        # pylint: disable = unused-variable, unused-import, no-self-use
        # pylint: disable = bad-option-value, import-outside-toplevel
        import py_fuse_git_bare_fs


class TestScriptsExecutable(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-26
    """

    def test_script_fuse_git_bare_fs_executable(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-26
        """
        # pylint: disable = invalid-name
        # pylint: disable = bad-option-value, import-outside-toplevel
        import subprocess
        for cmd in ["fuse_git_bare_fs -h", "fuse_git_bare_fs repo -h",
                    "fuse_git_bare_fs tree -h"]:
            cpi = subprocess.run(
                [cmd],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, timeout=3, check=True)
            # check at least minimal help output
            self.assertTrue(len(cpi.stdout) >= 775)
            # check begin of help output
            self.assertTrue(cpi.stdout.startswith(
                b'usage: fuse_git_bare_fs'))
            # check end of help output
            self.assertTrue(cpi.stdout.endswith(
                b'License: ' +
                b'GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.\n'))


def module(suite):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-14
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    add tests for the module
    """
    print('add tests for the module')
    loader = unittest.defaultTestLoader
    suite.addTest(loader.loadTestsFromTestCase(TestModuleImport))
    # py_fuse_git_bare_fs.repo_class
    suite.addTest(loader.loadTestsFromName(
        'tests.py_fuse_git_bare_fs_repo_class'))


def scripts(suite):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-26
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    add tests for the scripts
    """
    print('add tests for the scripts')
    loader = unittest.defaultTestLoader
    suite.addTest(loader.loadTestsFromTestCase(TestScriptsExecutable))
    # fuse_git_bare_fs repo
    suite.addTest(loader.loadTestsFromName(
        'tests.script_fuse_git_bare_fs_repo'))
    # fuse_git_bare_fs tree
    suite.addTest(loader.loadTestsFromName(
        'tests.script_fuse_git_bare_fs_tree'))
    # fuse_git_bare_fs tree -get_user_list_from_gitolite
    suite.addTest(loader.loadTestsFromName(
        'tests.script_fuse_git_bare_fs_tree_gitolite'))
    # with git-annex: fuse_git_bare_fs tree
    suite.addTest(loader.loadTestsFromName(
        'tests.script_fuse_git_bare_fs_tree_annex'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
