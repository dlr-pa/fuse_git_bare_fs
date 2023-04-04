"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
import re
import subprocess


class ListDirCompare():
    """
    :Author: Daniel Mohr
    :Date: 2023-04-04

    use this as a mixin class
    """
    # pylint: disable = too-few-public-methods, no-member

    def _list_dir_compare(self, joinedpath, setfiles, output):
        try:
            list_files = os.listdir(joinedpath)
        except FileNotFoundError:
            list_files = []
        self.assertEqual(set(list_files), setfiles)
        cp_ls = subprocess.run(
            ['ls -g -G'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, cwd=joinedpath,
            timeout=3, check=True)
        cp_ls_stdout = cp_ls.stdout.split(sep=b'\n')
        for i, outline in enumerate(output):
            self.assertTrue(bool(re.findall(outline, cp_ls_stdout[i])))
