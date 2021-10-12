"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
import subprocess
import warnings


def get_ref(src_dir, root_object):
    """
    This use the command line program git to read/handle a git repository.

    :param src_dir: path to the git repository as str
    :param root_object: name of the branch as bytes
    :return: hash of the branch root_object of the repository src_dir as str
             or error message as bytes

    Example:

      from py_fuse_git_bare_fs.repotools_git import get_ref
      commit_hash = get_ref('.', b'master')

    :Author: Daniel Mohr
    :Date: 2021-10-08
    """
    cpi = subprocess.run(
        ["git cat-file --batch-check='%(objectname)'"],
        input=root_object,
        stdout=subprocess.PIPE,
        cwd=src_dir, shell=True, timeout=3, check=True)
    return cpi.stdout.decode().strip()


def get_blob_data(src_dir, blob_hash):
    """
    :return: the data of a blob in a git repository

    Example:

      from py_fuse_git_bare_fs.repotools_git import get_ref, get_blob_data
      get_blob_data('.', b'2e65efe2a145dda7ee51d1741299f848e5bf752e')

    :Author: Daniel Mohr
    :Date: 2021-10-11
    """
    cpi = subprocess.run(
        ["git cat-file --batch"],
        input=blob_hash,
        stdout=subprocess.PIPE,
        cwd=src_dir, shell=True, timeout=3, check=True)
    return cpi.stdout


def get_repo_data(src_dir, root_object, time_regpat):
    # pylint: disable=anomalous-backslash-in-string
    """
    :param src_dir: path to the git repository as str
    :param root_object: name of the branch as bytes
    :param time_regpat: compiled search pattern from re, e. g.
                        re.compile(r' ([0-9]+) [0-9+-]+$')
    :return: commit hash, tree hash, time of last commit

    Example:

      import re
      from py_fuse_git_bare_fs.repotools_git import get_repo_data
      get_repo_data('.', b'master', re.compile(r' ([0-9]+) [+0-9+-]+$'))

    :Author: Daniel Mohr
    :Date: 2021-10-11
    """
    cpi = subprocess.run(
        ["git cat-file --batch"], input=root_object,
        stdout=subprocess.PIPE,
        cwd=src_dir, shell=True, timeout=3, check=True)
    if cpi.stdout.startswith(root_object):
        # empty repo or root_object does not exists
        msg = \
            'root repository object "%s" in "%s" does not exists. ' % \
            (root_object, src_dir)
        msg += 'Mountpoint will be empty.'
        warnings.warn(msg)
        return False
    splittedstdout = cpi.stdout.decode().split('\n')
    commit_hash = splittedstdout[0].split()[0]
    for data in splittedstdout:
        if data.startswith('tree'):
            tree_hash = data.split()[1]
            break
    for data in splittedstdout:
        if data.startswith('committer'):
            res = time_regpat.findall(data)
            if res:
                commit_time = int(res[0])
                break
    return (commit_hash, tree_hash, commit_time)


def get_size_of_blob(src_dir, blob_hash):
    """
    :param src_dir: path to the git repository as str
    :param blob_hash: has of the blob as bytes
    :return: integer of the amount of bytes of the blob

    Example:

      from py_fuse_git_bare_fs.repotools_git import get_size_of_blob
      get_size_of_blob('.', b'2e65efe2a145dda7ee51d1741299f848e5bf752e')

    :Author: Daniel Mohr
    :Date: 2021-10-12
    """
    cpi = subprocess.run(
        ["git cat-file --batch-check='%(objectsize)'"],
        input=blob_hash,
        stdout=subprocess.PIPE,
        cwd=src_dir, shell=True, timeout=3, check=True)
    return int(cpi.stdout.decode())


def _git_cat_file(src_dir, git_object):
    cpi = subprocess.run(
        ['git cat-file -p ' + git_object],
        stdout=subprocess.PIPE,
        cwd=src_dir, shell=True, timeout=3, check=True)
    return cpi.stdout.decode()


def get_tree(src_dir, tree_hash, tree_content_regpat):
    """
    :param src_dir: path to the git repository as str
    :param tree_hash: has of the tree as str
    :param tree_content_regpat:
        compiled search pattern from re, e. g.
        re.compile(r'^([0-9]+) (commit|tree|blob|tag) ([0-9a-f]+)\t(.+)$')
    :return: tree of the repo as a dict

    Example:

      import re
      from py_fuse_git_bare_fs.repotools_git import get_tree
      get_tree(
        '.',
        'b213332fda65de4d2848a98e01f43d689cccbe6d',
        re.compile(r'^([0-9]+) (commit|tree|blob|tag) ([0-9a-f]+)\t(.+)$'))

    :Author: Daniel Mohr
    :Date: 2021-10-12
    """
    tree = dict()
    # tree[path] =
    #   {'listdir': [], 'blobs': {name: {'mode': str, 'hash': str}}}
    trees = [('/', tree_hash)]  # (name, hash)
    tree['/'] = dict()
    while bool(trees):
        act_path, act_tree_hash = trees.pop(0)
        tree[act_path]['listdir'] = []
        tree[act_path]['blobs'] = dict()
        git_objects = _git_cat_file(src_dir, act_tree_hash).split('\n')
        for line in git_objects:
            if len(line) < 8:
                continue
            res = tree_content_regpat.findall(line)
            if res:
                (obj_mode, obj_type, obj_hash, obj_name) = res[0]
                if obj_type == 'blob':
                    tree[act_path]['listdir'].append(obj_name)
                    tree[act_path]['blobs'][obj_name] = {
                        'mode': obj_mode, 'hash': obj_hash}
                elif obj_type == 'tree':
                    tree[act_path]['listdir'].append(obj_name)
                    obj_path = os.path.join(act_path, obj_name)
                    trees.append((obj_path, obj_hash))
                    tree[obj_path] = dict()
    return tree
