"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-08 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import subprocess


def get_ref(src_dir, root_object):
    cpi = subprocess.run(
        ["git cat-file --batch-check='%(objectname)'"],
        input=root_object,
        stdout=subprocess.PIPE,
        cwd=src_dir, shell=True, timeout=3, check=True)
    return cpi.stdout.decode().strip()
