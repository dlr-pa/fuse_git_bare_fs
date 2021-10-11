"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-11 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import dulwich.errors
import dulwich.repo


def get_ref(src_dir, root_object):
    """
    This use the python module dulwich to read/handle a git repository.

    You can dynamically choose using dulwich or git, e. g.:

      try:
          from py_fuse_git_bare_fs.repotools_dulwich import get_ref
      except ModuleNotFoundError:
          from py_fuse_git_bare_fs.repotools_git import get_ref

    :param src_dir: path to the git repository as str
    :param root_object: name of the branch as bytes
    :return: hash of the branch root_object of the repository src_dir as str
             or error message as bytes

    :Author: Daniel Mohr
    :Date: 2021-10-11
    """
    refs_root_object = b'refs/heads/' + root_object
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository:
        raise FileNotFoundError(src_dir)
    refs = repo.get_refs()
    if refs_root_object in refs:
        return repo.get_refs()[refs_root_object].decode()
    else:
        return root_object + b' missing'
