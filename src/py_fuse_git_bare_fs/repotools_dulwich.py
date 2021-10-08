"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-08 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import dulwich.errors
import dulwich.repo


def get_ref(src_dir, root_object):
    refs_root_object = b'refs/heads/' + root_object
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository:
        raise FileNotFoundError(src_dir)
    refs = repo.get_refs()
    if refs_root_object in refs:
        return repo.get_refs()[refs_root_object].decode()
    else:
        return ''
