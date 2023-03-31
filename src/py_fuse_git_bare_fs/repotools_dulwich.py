"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12, 2023-03-31 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
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
    :Date: 2021-10-12, 2023-03-31
    """
    refs_root_object = b'refs/heads/' + root_object
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository as errmsg:
        raise FileNotFoundError(src_dir) from errmsg
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
    :Date: 2021-10-12, 2023-03-31
    """
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository as errmsg:
        raise FileNotFoundError(src_dir) from errmsg
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
    :Date: 2021-10-11, 2023-03-31
    """
    # to be compatible to py_fuse_git_bare_fs.repotools_git.get_repo_data
    # we need the parameter/argument time_regpat:
    # pylint: disable=unused-argument
    refs_root_object = b'refs/heads/' + root_object
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository as errmsg:
        raise FileNotFoundError(src_dir) from errmsg
    refs = repo.get_refs()
    if refs_root_object not in refs:
        # empty repo or root_object does not exists
        msg = f'root repository object "{root_object}" in "{src_dir}" ' + \
            'does not exists.'
        msg += 'Mountpoint will be empty.'
        warnings.warn(msg)
        return False
    commit_hash = repo.get_refs()[refs_root_object].decode()
    gitobj = repo.get_object(repo.get_refs()[refs_root_object])
    tree_hash = gitobj.tree.decode()
    commit_time = gitobj.commit_time
    return (commit_hash, tree_hash, commit_time)


def get_size_of_blob(src_dir, blob_hash):
    """
    :param src_dir: path to the git repository as str
    :param blob_hash: has of the blob as bytes
    :return: integer of the amount of bytes of the blob

    Example:

      from py_fuse_git_bare_fs.repotools_dulwich import get_size_of_blob
      get_size_of_blob('.', b'2e65efe2a145dda7ee51d1741299f848e5bf752e')

    :Author: Daniel Mohr
    :Date: 2021-10-12, 2023-03-31
    """
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository as errmsg:
        raise FileNotFoundError(src_dir) from errmsg
    return repo.get_object(blob_hash).raw_length()


def get_tree(src_dir, tree_hash, tree_content_regpat=None):
    """
    :param src_dir: path to the git repository as str
    :param tree_hash: has of the tree as str
    :param tree_content_regpat:
        compiled search pattern from re, e. g.
        re.compile(r'^([0-9]+) (commit|tree|blob|tag) ([0-9a-f]+)\t(.+)$')
    :return: tree of the repo as a dict

    Example:

      from py_fuse_git_bare_fs.repotools_git import get_tree
      get_tree(
        '.',
        'b213332fda65de4d2848a98e01f43d689cccbe6d')

    :Author: Daniel Mohr
    :Date: 2021-10-12, 2023-03-31
    """
    # to be compatible to py_fuse_git_bare_fs.repotools_git.get_repo_data
    # we need the parameter/argument tree_content_regpat:
    # pylint: disable=unused-argument
    # pylint: disable=too-many-locals
    try:
        repo = dulwich.repo.Repo(src_dir)
    except dulwich.errors.NotGitRepository as errmsg:
        raise FileNotFoundError(src_dir) from errmsg
    tree = {}
    # tree[path] =
    #   {'listdir': [], 'blobs': {name: {'mode': str, 'hash': str}}}
    dulwichmode2gitmode = {0o100644: '100644',
                           0o100755: '100755',
                           0o120000: '120000'}
    trees = [('/', tree_hash.encode())]  # (name, hash)
    tree['/'] = {}
    while bool(trees):
        act_path, act_tree_hash = trees.pop(0)
        tree[act_path]['listdir'] = []
        tree[act_path]['blobs'] = {}
        treelist = repo.get_object(act_tree_hash).items()
        for entry in treelist:
            obj_type = repo.get_object(entry.sha).type_name
            obj_hash = entry.sha
            obj_name = entry.path.decode()
            if obj_type == b'blob':
                obj_mode = dulwichmode2gitmode[entry.mode]
                tree[act_path]['listdir'].append(obj_name)
                tree[act_path]['blobs'][obj_name] = {
                    'mode': obj_mode, 'hash': obj_hash.decode()}
            elif obj_type == b'tree':
                tree[act_path]['listdir'].append(obj_name)
                obj_path = os.path.join(act_path, obj_name)
                trees.append((obj_path, obj_hash))
                tree[obj_path] = {}
    return tree
