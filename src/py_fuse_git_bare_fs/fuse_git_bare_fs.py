"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-06-15 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import argparse
try:
    import fusepy  # https://github.com/fusepy/fusepy
except ModuleNotFoundError:
    import fuse as fusepy
import os.path
import sys


def fuse_git_bare_fs_repo(args):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-06-10 (last change).
    """
    operations_instance = None
    if args.daemon:  # running in foreground
        import logging
        from .git_bare_repo import git_bare_repo_logging
        logging.basicConfig(level=logging.DEBUG)
        operations_instance = git_bare_repo_logging(
            os.path.abspath(args.src_dir),
            args.root_object[0].encode(),
            args.max_cache_size[0])
    else:
        from .git_bare_repo import git_bare_repo
        operations_instance = git_bare_repo(
            os.path.abspath(args.src_dir),
            args.root_object[0].encode(),
            args.max_cache_size[0])
    fuse = fusepy.FUSE(
        operations_instance,
        args.target_dir,
        foreground=args.daemon,
        nothreads=args.threads,
        allow_other=args.allow_other)


def fuse_git_bare_fs_tree(args):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-06-15 (last change).
    """
    operations_instance = None
    if args.daemon:  # running in foreground
        import logging
        if args.get_user_list_from_gitolite:
            from .git_bare_repo_tree_gitolite import \
                git_bare_repo_tree_gitolite_logging
            logging.basicConfig(level=logging.DEBUG)
            operations_instance = git_bare_repo_tree_gitolite_logging(
                os.path.abspath(args.src_dir),
                args.root_object[0].encode(),
                args.provide_htaccess,
                args.htaccess_template[0],
                args.gitolite_cmd[0],
                args.gitolite_user_file[0],
                args.max_cache_size[0])
        else:
            from .git_bare_repo_tree import git_bare_repo_tree_logging
            logging.basicConfig(level=logging.DEBUG)
            operations_instance = git_bare_repo_tree_logging(
                os.path.abspath(args.src_dir),
                args.root_object[0].encode(),
                args.max_cache_size[0])
    else:
        if args.get_user_list_from_gitolite:
            from .git_bare_repo_tree_gitolite \
                import git_bare_repo_tree_gitolite
            operations_instance = git_bare_repo_tree_gitolite(
                os.path.abspath(args.src_dir),
                args.root_object[0].encode(),
                args.provide_htaccess,
                args.htaccess_template[0],
                args.gitolite_cmd[0],
                args.gitolite_user_file[0],
                args.max_cache_size[0])
        else:
            from .git_bare_repo_tree import git_bare_repo_tree
            operations_instance = git_bare_repo_tree(
                os.path.abspath(args.src_dir),
                args.root_object[0].encode(),
                args.max_cache_size[0])
    fuse = fusepy.FUSE(
        operations_instance,
        args.target_dir,
        foreground=args.daemon,
        nothreads=args.threads,
        allow_other=args.allow_other)


def my_argument_parser():
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-06-15 (last change).
    """
    epilog = ''
    epilog += 'Author: Daniel Mohr\n'
    epilog += 'Date: 2021-06-15\n'
    epilog += 'License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.'
    epilog += '\n\n'
    description = '"fuse_git_bare_fs" is a tool to mount the working '
    description += 'tree(s) of git bare repositories '
    description += 'as a filesystem in user space (fuse). '
    description += 'It gives only read access. '
    description += 'For a write access you should do a git commit and use git.'
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
    parser.add_argument(
        '-o',
        nargs=1,
        type=str,
        required=False,
        default=[None],
        dest='opt',
        help='These options are splitted at "," and used as seperated options.'
        ' The sub-commands are extracted as well. '
        'The flag "-daemon" is used in any case. '
        'This allows to use this program as mount program e. g. in /etc/fstab.'
        ' Example: "a,b=c" will become "-a -b c"; "a,tree,b=c" will'
        ' become "tree -a -b c"')
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
        '-cache_size',
        nargs=1,
        type=int,
        required=False,
        default=[1073741824],
        dest='max_cache_size',
        help='Defines the maximal used cache size. '
        'default: 1073741824 (1 GB)')
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
        '-uid',
        nargs=1,
        type=str,
        required=False,
        default=[None],
        dest='uid',
        help='The program is run under this uid. The current direcotry and '
        'the home directory are set appropriate. This allows to use this '
        'program as mount program e. g. in /etc/fstab. '
        'On default nothing is done (the calling user is used).')
    common_parser.add_argument(
        '-gid',
        nargs=1,
        type=str,
        required=False,
        default=[None],
        dest='gid',
        help='The program is run under this gid. On default nothing is done. '
        'This allows to use this program as mount program '
        'e. g. in /etc/fstab.')
    common_parser.add_argument(
        '-ro',
        action='store_true',
        help='Make a read only mountpoint. This is always the case! '
        'This allows to use this program as mount program '
        'e. g. in /etc/fstab.')
    common_parser.add_argument(
        '-dev',
        action='store_true',
        help='This is ignored. '
        'This allows to use this program as mount program '
        'e. g. in /etc/fstab.')
    common_parser.add_argument(
        '-suid',
        action='store_true',
        help='This is ignored. '
        'This allows to use this program as mount program '
        'e. g. in /etc/fstab.')
    # subparser repo
    description = '"fuse_git_bare_fs repo" is a tool to mount the working '
    description += 'tree of a git bare repository '
    description += 'as a filesystem in user space (fuse). '
    description += 'It gives only read access. '
    description += 'For a write access you should do a git commit and use git.'
    description += ' This script needs about 7.6 MB of memory to run. '
    description += 'More memory is necessary for large working trees or '
    description += 'to provide file content.'
    epilog = 'Examples:\n\n'
    epilog += 'fuse_git_bare_fs repo a b\n\n'
    epilog += 'sudo -u www-data fuse_git_bare_fs repo a b\n\n'
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
        'For more help: fuse_git_bare_fs repo -h',
        description=description,
        epilog=epilog,
        parents=[repo_parser, common_parser])
    parser_repo.set_defaults(func=fuse_git_bare_fs_repo)
    # subparser tree
    description = '"fuse_git_bare_fs tree" is a tool to mount the working '
    description += 'tree of git bare repositories in a directory tree '
    description += 'as a filesystem in user space (fuse). '
    description += 'The idea is to provide the git repositories manage by '
    description += 'a gitolite instance. Therefore parameters for this '
    description += 'purpose are available. It is assumed that the bare '
    description += 'repositories are named like "*.git". '
    description += 'It gives only read access. '
    description += 'For a write access you should do a git commit and use git.'
    description += ' For unmount just press ctrl-c, kill the program or do '
    description += '"fusermount -u target_dir".'
    epilog = 'Examples:\n\n'
    epilog += 'fuse_git_bare_fs tree a b\n\n'
    epilog += 'sudo -u gitolite fuse_git_bare_fs tree -daemon -allow_other '
    epilog += '-get_user_list_from_gitolite -provide_htaccess '
    epilog += '/var/lib/gitolite/repositories /var/www/gitolite/webdav\n\n'
    epilog += 'mount -t fuse.fuse_git_bare_fs -o uid=gitolite,gid=gitolite,'
    epilog += 'tree,allow_other,get_user_list_from_gitolite,provide_htaccess,'
    epilog += 'root_object=master,ro /var/lib/gitolite/repositories '
    epilog += '/var/www/gitolite/webdav\n\n'
    epilog += 'Example (put the following line to /etc/fstab):\n\n'
    epilog += '/var/lib/gitolite/repositories /var/www/gitolite/webdav '
    epilog += 'fuse.fuse_git_bare_fs uid=gitolite,gid=gitolite,tree,'
    epilog += 'allow_other,get_user_list_from_gitolite,provide_htaccess,'
    epilog += 'root_object=master,ro 0 0\n\n'
    epilog += 'Author: Daniel Mohr\n'
    epilog += 'Date: 2021-06-15\n'
    epilog += 'License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.'
    epilog += '\n\n'
    tree_parser = argparse.ArgumentParser(add_help=False)
    tree_parser.add_argument(
        'src_dir',
        help='This is the path to the directory tree of git bare repositories.'
        ' The working trees of their root_object (e. g. master) will be '
        'transparent available in the target_dir.')
    parser_tree = subparsers.add_parser(
        'tree',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='Mount the working tree of git repositories in a directory tree. '
        'For more help: fuse_git_bare_fs tree -h',
        description=description,
        epilog=epilog,
        parents=[tree_parser, common_parser])
    parser_tree.set_defaults(func=fuse_git_bare_fs_tree)
    parser_tree.add_argument(
        '-get_user_list_from_gitolite',
        action='store_true',
        help='This creates subdirectories for each user. The users are '
        'extracted from the gitolite-admin repository included in the given '
        'src_dir. In every user directory only the repositories are mounted, '
        'which are accessable for the appropriate user. It is suposed that '
        'the command "gitolite" is available and that the gitolite-admin '
        'repository is called "gitolite-admin". Additional configuration can '
        'be given with the flags "-gitolite_cmd" and "-gitolite_user_file".')
    parser_tree.add_argument(
        '-provide_htaccess',
        action='store_true',
        help='This creates ".htaccess" files in the user directories. This '
        'only appears if the flag "-get_user_list_from_gitolite" is given.')
    parser_tree.add_argument(
        '-htaccess_template',
        nargs=1,
        type=str,
        required=False,
        default=[None],
        dest='htaccess_template',
        help='A htaccess template can be given. '
        'It is "Require user [username]" '
        'added. On default only "Require user [username]" is used.')
    parser_tree.add_argument(
        '-gitolite_cmd',
        nargs=1,
        type=str,
        required=False,
        default=['gitolite'],
        dest='gitolite_cmd',
        help='Defines the gitolite command. You can give an absolute path. '
        'default: gitolite')
    parser_tree.add_argument(
        '-gitolite_user_file',
        nargs=1,
        type=str,
        required=False,
        default=[None],
        dest='gitolite_user_file',
        help='If given, the list of users is created from the content of this '
        'file and the gitolite command "list-users". You can give an absolute '
        'path. If not given (default) only the gitolite command "list-users" '
        'is used to create the list of users. If the file does not exist, '
        'it is ignored until it is available. This is useful if gitolite only '
        'knows groups and the users are defined elsewhere (e. g. LDAP '
        'configuration of gitolite). You should update the given file '
        'regularly (e. g. by a cron job) from the source (e. g. directory '
        'service). Further you could overwrite the default gitolite command '
        'by a command, which return nothing for "list-users" and otherwise '
        'uses the normal gitolite command.')
    return parser


def fuse_git_bare_fs():
    # command line arguments:
    parser = my_argument_parser()
    # parse arguments
    if '-o' in sys.argv:
        # adapt calling arguments due to the given options
        param = ['-daemon']
        found_positional_params = 0
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == '-o':
                opt = sys.argv[i + 1].split(',')
                for o in opt:
                    if '=' in o:
                        par, val = o.split('=')
                        param.append('-' + par)
                        param.append(val)
                    elif o in ['repo', 'tree']:
                        param = [o] + param
                    else:
                        param.append('-' + o)
            elif sys.argv[i] in ['repo', 'tree']:
                param = [sys.argv[i]] + param
            else:
                if found_positional_params in [0, 1]:
                    found_positional_params += 1
                    param.append(sys.argv[i])
        args = parser.parse_args(param)
    else:
        args = parser.parse_args()
    if args.subparser_name is not None:
        if args.gid[0] is not None:
            import grp
            gid = None
            try:
                gid = int(args.gid[0])
            except ValueError:
                pass
            if gid is None:
                gid = grp.getgrnam(args.gid[0]).gr_gid
            os.setgid(gid)
        if args.uid[0] is not None:
            import pwd
            uid = None
            try:
                uid = int(args.uid[0])
            except ValueError:
                pass
            if uid is None:
                uid = pwd.getpwnam(args.uid[0]).pw_uid
            os.setuid(uid)
            pw_dir = pwd.getpwuid(uid).pw_dir
            os.environ['HOME'] = pw_dir
            os.chdir(pw_dir)
            if 'PATH' not in os.environ:
                os.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:' + \
                    '/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin'
        args.func(args)  # call the programs
    else:  # no sub command given
        parser.print_help()
