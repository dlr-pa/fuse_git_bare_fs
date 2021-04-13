"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-13 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import argparse
import fusepy  # https://github.com/fusepy/fusepy
import os.path


def fuse_git_bare_fs_repo(args):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-13 (last change).
    """
    if args.daemon:  # running in foreground
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


def fuse_git_bare_fs_tree(args):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-13 (last change).
    """
    if args.daemon:  # running in foreground
        import logging
        if args.get_user_list_from_gitolite:
            from .git_bare_repo_tree_gitolite import git_bare_repo_tree_gitolite_logging
            logging.basicConfig(level=logging.DEBUG)
            fuse = fusepy.FUSE(
                git_bare_repo_tree_gitolite_logging(
                    os.path.abspath(args.src_dir),
                    args.root_object[0].encode(),
                    args.provide_htaccess),
                args.target_dir,
                foreground=args.daemon,
                nothreads=args.threads,
                allow_other=args.allow_other,
                raw_fi=args.raw_fi)
        else:
            from .git_bare_repo_tree import git_bare_repo_tree_logging
            logging.basicConfig(level=logging.DEBUG)
            fuse = fusepy.FUSE(
                git_bare_repo_tree_logging(os.path.abspath(args.src_dir),
                                           args.root_object[0].encode()),
                args.target_dir,
                foreground=args.daemon,
                nothreads=args.threads,
                allow_other=args.allow_other,
                raw_fi=args.raw_fi)
    else:
        if args.get_user_list_from_gitolite:
            from .git_bare_repo_tree_gitolite import git_bare_repo_tree_gitolite
            logging.basicConfig(level=logging.DEBUG)
            fuse = fusepy.FUSE(
                git_bare_repo_tree_gitolite(
                    os.path.abspath(args.src_dir),
                    args.root_object[0].encode(),
                    args.provide_htaccess),
                args.target_dir,
                foreground=args.daemon,
                nothreads=args.threads,
                allow_other=args.allow_other,
                raw_fi=args.raw_fi)
        else:
            from .git_bare_repo_tree import git_bare_repo_tree
            fuse = fusepy.FUSE(
                git_bare_repo_tree(os.path.abspath(args.src_dir),
                                   args.root_object[0].encode()),
                args.target_dir,
                foreground=args.daemon,
                nothreads=args.threads,
                allow_other=args.allow_other,
                raw_fi=args.raw_fi)


def my_argument_parser():
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-13 (last change).
    """
    epilog = ''
    epilog += 'Author: Daniel Mohr\n'
    epilog += 'Date: 2021-04-13\n'
    epilog += 'License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.'
    epilog += '\n\n'
    description = '"fuse_git_bare_fs.py" is a tool to mount the working '
    description += 'tree(s) of git bare repositories '
    description += 'as a filesystem in user space (fuse). '
    description += 'It gives only read access. '
    description += 'For a write access you should do a git commit and use git. '
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(
        dest='subparser_name',
        help='There are different sub-commands with there own flags.')
    # parent parser to describe common argument
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        'target_dir',
        help='This is the mountpoint.')
    common_parser.add_argument(
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
    common_parser.add_argument(
        '-daemon',
        action='store_false',
        help='If given, go to background and work as a daemon. '
        'To unmount you can do: fusermount -u target_dir')
    common_parser.add_argument(
        '-threads',
        action='store_false',
        help='If given, the fuse mount will be threaded. '
        'This is not tested.')
    common_parser.add_argument(
        '-allow_other',
        action='store_true',
        help='If given, allows other users to use the fuse mount point. '
        'Therefore you have to allow this in /etc/fuse.conf by '
        'uncommenting "user_allow_other" there.')
    common_parser.add_argument(
        '-raw_fi',
        action='store_true',
        help='If given, use fuse_file_info instead of fh filed in fusepy.')
    # subparser repo
    description = '"fuse_git_bare_fs.py repo" is a tool to mount the working '
    description += 'tree of a git bare repository '
    description += 'as a filesystem in user space (fuse). '
    description += 'It gives only read access. '
    description += 'For a write access you should do a git commit and use git. '
    description += 'This script needs about 7.6 MB of memory to run. '
    description += 'More memory is necessary for large working trees or '
    description += 'to provide file content.'
    epilog = 'Examples:\n\n'
    epilog += 'fuse_git_bare_fs.py repo a b\n\n'
    epilog += 'sudo -u www-data fuse_git_bare_fs.py repo a b\n\n'
    epilog += 'Author: Daniel Mohr\n'
    epilog += 'Date: 2021-04-13\n'
    epilog += 'License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.'
    epilog += '\n\n'
    repo_parser = argparse.ArgumentParser(add_help=False)
    repo_parser.add_argument(
        'src_dir',
        help='This is the path to a git bare repository. '
        'The working tree of its root_object (e. g. master) will be '
        'transparent available in the target_dir.')
    parser_repo = subparsers.add_parser(
        'repo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Mount the working tree of a git repository. '
        'For more help: fuse_git_bare_fs.py repo -h',
        description=description,
        epilog=epilog,
        parents=[repo_parser, common_parser])
    parser_repo.set_defaults(func=fuse_git_bare_fs_repo)
    # subparser tree
    description = '"fuse_git_bare_fs.py tree" is a tool to mount the working '
    description += 'tree of a git bare repositories in a directory tree '
    description += 'as a filesystem in user space (fuse). '
    description += 'The idea is to provide the git repositories manage by '
    description += 'a gitolite instance. Therefore parameters for this '
    description += 'purpose are available. It is assumed that the bare '
    description += 'repositories are named like "*.git". '
    description += 'It gives only read access. '
    description += 'For a write access you should do a git commit and use git. '
    epilog = 'Examples:\n\n'
    epilog += 'fuse_git_bare_fs.py tree a b\n\n'
    epilog += 'sudo -u gitolite fuse_git_bare_fs.py tree -daemon -allow_other -get_user_list_from_gitolite -provide_htaccess /var/lib/gitolite/repositories /var/www/gitolite/webdav\n\n'
    epilog += 'Author: Daniel Mohr\n'
    epilog += 'Date: 2021-04-13\n'
    epilog += 'License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.'
    epilog += '\n\n'
    tree_parser = argparse.ArgumentParser(add_help=False)
    tree_parser.add_argument(
        'src_dir',
        help='This is the path to the directory tree of git bare repositories. '
        'The working trees of their root_object (e. g. master) will be '
        'transparent available in the target_dir.')
    parser_tree = subparsers.add_parser(
        'tree',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Mount the working tree of git repositories in a directory tree. '
        'For more help: fuse_git_bare_fs.py tree -h',
        description=description,
        epilog=epilog,
        parents=[tree_parser, common_parser])
    parser_tree.set_defaults(func=fuse_git_bare_fs_tree)
    parser_tree.add_argument(
        '-get_user_list_from_gitolite',
        action='store_true',
        help='This creates subdirectories for each user. The users are extracted from the gitolite-admin repository included in the given src_dir. In every use directory only the repositories are mounted, which are accessable for the appropriate user. It is suposed that the command "gitolite" is available and that the gitolite-admin repository is called "gitolite-admin".')
    parser_tree.add_argument(
        '-provide_htaccess',
        action='store_true',
        help='This creates ".htaccess" files in the user directories. This only appears if the flag "-get_user_list_from_gitolite" is given.')
    return parser


def fuse_git_bare_fs():
    # command line arguments:
    parser = my_argument_parser()
    # parse arguments
    args = parser.parse_args()
    if args.subparser_name is not None:
        args.func(args)  # call the programs
    else:  # no sub command given
        parser.print_help()
