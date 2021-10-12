"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import warnings

import dulwich.errors
import dulwich.repo


def get_ref(src_dir, root_object):
    """
    This use the python module dulwich to read/handle a git repository.

    :param src_dir: path to the git repository as str
    :param root_object: name of the branch as bytes
    :return: hash of the branch root_object of the repository src_dir as str
             or error message as bytes

    You can dynamically choose using dulwich or git, e. g.:

      try:
          from py_fuse_git_bare_fs.repotools_dulwich import get_ref
      except (ModuleNotFoundError, ImportError):
          from py_fuse_git_bare_fs.repotools_git import get_ref
      commit_hash = get_ref('.', b'master')

    :Author: Daniel Mohr
    :Date: 2021-10-12
    """
    refs_root_object = b'refs/heads/' + root_object
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository:
        raise FileNotFoundError(src_dir)
    refs = repo.get_refs()
    if refs_root_object in refs:
        return repo.get_refs()[refs_root_object].decode()
    return (root_object + b' missing').decode()


def get_blob_data(src_dir, blob_hash):
    """
    :param src_dir: path to the git repository as str
    :param blob_hash: hash of the blob as bytes
    :return: the data of a blob in a git repository

    Example:

      from py_fuse_git_bare_fs.repotools_dulwich import get_ref, get_blob_data
      get_blob_data('.', b'2e65efe2a145dda7ee51d1741299f848e5bf752e')

    :Author: Daniel Mohr
    :Date: 2021-10-12
    """
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository:
        raise FileNotFoundError(src_dir)
    # repo.get_object(blob_hash).type_name == b'blob'
    data = repo.get_object(blob_hash).data
    return blob_hash + b' ' + b'blob' + b' ' + str(len(data)).encode() + \
        b'\n' + repo.get_object(blob_hash).data + b'\n'


def get_repo_data(src_dir, root_object, time_regpat=None):
    """
    :param src_dir: path to the git repository as str
    :param root_object: name of the branch as bytes
    :return: commit hash, tree hash, time of last commit

    Example:

      import re
      from py_fuse_git_bare_fs.repotools_dulwich import get_repo_data
      get_repo_data('.', b'master')

    :Author: Daniel Mohr
    :Date: 2021-10-11
    """
    # to be compatible to py_fuse_git_bare_fs.repotools_git.get_repo_data
    # we need the parameter/argument time_regpat:
    # pylint: disable=unused-argument
    refs_root_object = b'refs/heads/' + root_object
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository:
        raise FileNotFoundError(src_dir)
    refs = repo.get_refs()
    if refs_root_object not in refs:
        # empty repo or root_object does not exists
        msg = \
            'root repository object "%s" in "%s" does not exists. ' % \
            (root_object, src_dir)
        msg += 'Mountpoint will be empty.'
        warnings.warn(msg)
        return False
    commit_hash = repo.get_refs()[refs_root_object].decode()
    gitobj = repo.get_object(repo.get_refs()[refs_root_object])
    tree_hash = gitobj.tree.decode()
    commit_time = gitobj.commit_time
    return (commit_hash, tree_hash, commit_time)
