"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
import subprocess


class PrepareSimpleTestEnvironment():
    """
    :Author: Daniel Mohr
    :Date: 2021-10-12

    use this as a mixin class
    """
    # pylint: disable=too-few-public-methods

    def _prepare_simple_test_environment1(
            self, tmpdir, serverdir, clientdir, mountpointdir, reponame):
        """
        :Author: Daniel Mohr
        :Date: 2021-10-12
        """
        # pylint: disable=too-many-arguments,no-self-use
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
