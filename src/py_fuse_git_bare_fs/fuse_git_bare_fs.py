"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-13 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import argparse
import fusepy  # https://github.com/fusepy/fusepy
import os.path


def fuse_git_bare_fs():
    epilog = 'Examples:\n\n'
    epilog += 'fuse_git_bare_fs.py a b\n\n'
    epilog += 'sudo -u www-data fuse_git_bare_fs.py a b\n\n'
    epilog += 'Author: Daniel Mohr\n'
    epilog += 'Date: 2021-04-13\n'
    epilog += 'License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.'
    epilog += '\n\n'
    description = '"fuse_git_bare_fs.py" is a tool to mount the working tree '
    description += 'of a git bare repository '
    description += 'as a filesystem in user space (fuse). '
    description += 'It gives only read access. '
    description += 'For a write access you should do a git commit and use git. '
    description += 'This script needs about 7.6 MB of memory to run. '
    description += 'More memory is necessary for large working trees or '
    description += 'to provide file content.'
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'src_dir',
        help='This is the path to a git bare repository. '
        'The working tree of its root_object (e. g. master) will be '
        'transparent available in the target_dir.')
    parser.add_argument(
        'target_dir',
        help='This is the mountpoint.')
    parser.add_argument(
        '-root_object',
        nargs=1,
        type=str,
        required=False,
        default=['master'],
        dest='root_object',
        help='Defines the root repository object of the working tree. '
        'This will be given as a parameter to "git cat-file"; '
        'hence you can look in the relevant man page of "git cat-file" '
        'to understand how to specify the branch and or revision. '
        'default: master')
    parser.add_argument(
        '-daemon',
        action='store_false',
        help='If given, go to background and work as a daemon. '
        'To unmount you can do: fusermount -u target_dir')
    parser.add_argument(
        '-threads',
        action='store_false',
        help='If given, the fuse mount will be threaded. '
        'This is not tested.')
    parser.add_argument(
        '-allow_other',
        action='store_true',
        help='If given, allows other users to use the fuse mount point. '
        'Therefore you have to allow this in /etc/fuse.conf by '
        'uncommenting "user_allow_other" there.')
    parser.add_argument(
        '-raw_fi',
        action='store_true',
        help='If given, use fuse_file_info instead of fh filed in fusepy.')
    args = parser.parse_args()

    if args.daemon: # running in foreground
        import logging
        from .git_bare_repo import git_bare_repo_logging
        logging.basicConfig(level=logging.DEBUG)
        fuse = fusepy.FUSE(
            git_bare_repo_logging(os.path.abspath(args.src_dir),
                                  args.root_object[0].encode()),
            args.target_dir,
            foreground=args.daemon,
            nothreads=args.threads,
            allow_other=args.allow_other,
            raw_fi=args.raw_fi)
    else:
        from .git_bare_repo import git_bare_repo
        fuse = fusepy.FUSE(
            git_bare_repo(os.path.abspath(args.src_dir),
                          args.root_object[0].encode()),
            args.target_dir,
            foreground=args.daemon,
            nothreads=args.threads,
            allow_other=args.allow_other,
            raw_fi=args.raw_fi)
