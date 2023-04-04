"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12, 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
import subprocess


class PrepareSimpleTestEnvironment():
    """
    :Author: Daniel Mohr
    :Date: 2021-10-12, 2023-04-04

    use this as a mixin class
    """
    # pylint: disable=too-few-public-methods

    def _prepare_simple_test_environment1(
            self, tmpdir, serverdir, clientdir, mountpointdir, reponame,
            createdirs=None, add_git=False):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12, 2023-04-04
        """
        # pylint: disable=too-many-arguments,no-self-use
        if createdirs is None:
            createdirs = [serverdir, clientdir, mountpointdir]
        for dirpath in createdirs:
            os.mkdir(os.path.join(tmpdir, dirpath))
        reponamegit = reponame
        if add_git:
            reponamegit = reponame + '.git'
        subprocess.run(
            ['git init --bare ' + reponamegit],
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
