"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-29
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os

from distutils.core import setup, Command


class TestWithPytest(Command):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-14
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    running automatic tests with pytest
    """
    description = "running automatic tests with pytest"
    user_options = [
        ('src=',
         None,
         'Choose what should be tested; installed: ' +
         'test installed package and scripts (default); ' +
         'local: test package direct from sources ' +
         '(installing is not necessary). ' +
         'The command line scripts are not tested for local. ' +
         'default: installed'),
        ('coverage', None, 'use pytest-cov to generate a coverage report'),
        ('pylint', None, 'if given, run pylint'),
        ('pytestverbose', None, 'increase verbosity of pytest'),
        ('parallel', None, 'run tests in parallel')]

    def initialize_options(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-02-18
        """
        self.src = 'installed'
        self.coverage = False
        self.pylint = False
        self.pytestverbose = False
        self.parallel = False

    def finalize_options(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-02-04
        """
        pass

    def run(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-21
        """
        # env python3 setup.py run_pytest
        import sys
        import os.path
        if self.src == 'installed':
            pass
        elif self.src == 'local':
            sys.path.insert(0, os.path.abspath('src'))
        else:
            raise distutils.core.DistutilsArgError(
                "error in command line: " +
                "value for option 'src' is not 'installed' or 'local'")
        sys.path.append(os.path.abspath('.'))
        # https://docs.pytest.org/en/stable/contents.html
        # https://pytest-cov.readthedocs.io/en/latest/
        import pytest
        pyargs = []
        if self.parallel:
            try:
                # if available, using parallel test run
                import xdist
                import sys
                if os.name == 'posix':
                    # since we are only running seconds,
                    # we use the load of the last minute:
                    nthreads = int(os.cpu_count() - os.getloadavg()[0])
                    # since we have only a few tests, limit overhead:
                    nthreads = min(4, nthreads)
                    nthreads = max(1, nthreads)  # at least one thread
                else:
                    nthreads = max(1, int(0.5 * os.cpu_count()))
                pyargs += ['-n %i' % nthreads]
            except:
                pass
        if self.coverage:
            # env python3 setup.py run_pytest --coverage
            coverage_dir = 'coverage_report/'
            # first we need to clean the target directory
            if os.path.isdir(coverage_dir):
                files = os.listdir(coverage_dir)
                for f in files:
                    os.remove(os.path.join(coverage_dir, f))
            pyargs += ['--cov=py_fuse_git_bare_fs', '--no-cov-on-fail',
                       '--cov-report=html:' + coverage_dir,
                       '--cov-report=term:skip-covered']
        if self.pylint:
            pyargs += ['--pylint']
        if self.pytestverbose:
            pyargs += ['--verbose']
        pyargs += ['tests/py_fuse_git_bare_fs_repo_class.py']
        pyargs += ['tests/script_fuse_git_bare_fs_repo.py']
        pyargs += ['tests/script_fuse_git_bare_fs_tree.py']
        pyargs += ['tests/script_fuse_git_bare_fs_tree_gitolite.py']
        pyargs += ['tests/script_fuse_git_bare_fs_tree_annex.py']
        if self.src == 'installed':
            pyargs += ['tests/main.py']
        pyplugins = []
        print('call: pytest', ' '.join(pyargs))
        pytest.main(pyargs, pyplugins)


class TestWithUnittest(Command):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-14
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    running automatic tests with unittest
    """
    description = "running automatic tests with unittest"
    user_options = [
        ("src=",
         None,
         'Choose what should be tested; installed: ' +
         'test installed package and scripts (default); ' +
         'local: test package direct from sources ' +
         '(installing is not necessary). ' +
         'The command line scripts are not tested for local. ' +
         'default: installed')]

    def initialize_options(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-02-04
        """
        self.src = 'installed'

    def finalize_options(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-02-04
        """
        pass

    def run(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-14
        """
        # env python3 setup.py run_unittest
        import sys
        import os.path
        if self.src == 'installed':
            pass
        elif self.src == 'local':
            sys.path.insert(0, os.path.abspath('src'))
        else:
            raise distutils.core.DistutilsArgError(
                "error in command line: " +
                "value for option 'src' is not 'installed' or 'local'")
        sys.path.append(os.path.abspath('.'))
        import unittest
        suite = unittest.TestSuite()
        import tests
        tests.module(suite)
        setup_self = self

        class test_required_module_import(unittest.TestCase):
            def test_required_module_import(self):
                import importlib
                for module in setup_self.distribution.metadata.get_requires():
                    if module == 'fusepy':
                        try:
                            importlib.import_module(module)
                        except ModuleNotFoundError:
                            import fuse as fusepy
                    else:
                        importlib.import_module(module)
        loader = unittest.defaultTestLoader
        suite.addTest(loader.loadTestsFromTestCase(
            test_required_module_import))
        if self.src == 'installed':
            tests.scripts(suite)
        unittest.TextTestRunner(verbosity=2).run(suite)


class CheckModules(Command):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@gmx.de
    :Date: 2017-01-08
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    checking for modules need to run the software
    """
    description = "checking for modules need to run the software"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import importlib
        summary = ""
        i = 0
        print("checking for modules need to run the software (scripts and")
        print("modules/packages) of this package:\n")
        print("checking for the modules mentioned in the 'setup.py':")
        for module in self.distribution.metadata.get_requires():
            if self.verbose:
                print("try to load %s" % module)
            try:
                importlib.import_module(module)
                if self.verbose:
                    print("  loaded.")
            except ImportError:
                i += 1
                summary += "module '%s' is not available\n" % module
                print("module '%s' is not available <---WARNING---" % module)
        print(
            "\nSummary\n%d modules are not available (not unique)\n%s\n" % (
                i, summary))


class CheckModulesModulefinder(Command):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@gmx.de
    :Date: 2017-01-08
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    checking for modules need to run the scripts (modulefinder)
    """
    description = "checking for modules need to run the scripts (modulefinder)"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import modulefinder
        for script in self.distribution.scripts:
            print("\nchecking for modules used in '%s':" % script)
            finder = modulefinder.ModuleFinder()
            finder.run_script(script)
            finder.report()


# necessary modules
required_modules = ['argparse',
                    'errno',
                    'fusepy',
                    'grp',
                    'hashlib',
                    'logging',
                    'os',
                    'os.path',
                    'pwd',
                    're',
                    'subprocess',
                    'sys',
                    'threading',
                    'time',
                    'warnings']
# optional modules for python3 setup.py check_modules
required_modules += ['importlib']
# optional modules for python3 setup.py check_modules_modulefinder
required_modules += ['modulefinder']
# modules to build doc
required_modules += ['sphinx', 'sphinxarg', 'recommonmark']
# modules to run tests with unittest
required_modules += ['shutil', 'tempfile', 'unittest']
# modules to run tests with pytest
required_modules += ['pytest']
# optional modules to run tests with pytest in parallel
required_modules += ['xdist']

setup(
    name='fuse_git_bare_fs',
    version='2021-04-29',
    cmdclass={
        'check_modules': CheckModules,
        'check_modules_modulefinder': CheckModulesModulefinder,
        'run_unittest': TestWithUnittest,
        'run_pytest': TestWithPytest},
    description='Tool to mount the working tree '
    'of a git bare repository as a filesystem in user space (fuse).',
    long_description='',
    keywords='mount fuse git bare repository working tree',
    author='Daniel Mohr',
    author_email='daniel.mohr@dlr.de',
    maintainer='Daniel Mohr',
    maintainer_email='daniel.mohr@dlr.de',
    url='',
    download_url='',
    package_dir={'': 'src'},
    packages=['py_fuse_git_bare_fs'],
    scripts=['src/scripts/fuse_git_bare_fs'],
    license='GNU GENERAL PUBLIC LICENSE, Version 2, June 1991',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: BSD :: OpenBSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'],
    # cat $(find | grep "py$") | egrep -i "^[ \t]*import .*$" | egrep -i --only-matching "import .*$" | sort -u
    requires=required_modules
)
