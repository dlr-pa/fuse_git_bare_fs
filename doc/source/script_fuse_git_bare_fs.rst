command line script: :program:`fuse_git_bare_fs`
================================================

.. program:: fuse_git_bare_fs


	     
overview
--------

:program:`fuse_git_bare_fs` has two subcommands:

.. option:: repo

   Mount the working tree of a [git]_ repository as a
   filesystem in user space ([FUSE]_).

.. option:: tree

   Mount the working tree of git repositories in a directory tree.

Instead of these subcommands you can also use the flag '-o' to
use :program:`fuse_git_bare_fs` as a mount program(cf. [vfs_fuse]_, [mount]_).
For example to mount '/foo' to '/bar' as the user 'sr' and the group 'grp',
you can add the following line to your '/etc/fstab' (cf. [fstab]_::

  /foo /bar fuse.fuse_git_bare_fs uid=sr,gid=grp,tree,root_object=master,ro 0 0

For a non persistent mount you can use :program:`fuse_git_bare_fs` directly::

  fuse_git_bare_fs tree -uid=sr -gid=grp /foo /bar

These commands are explained in more detail in the following (help output):


.. only:: html

  References:
  ___________

.. [git] https://git-scm.com/
.. [FUSE] https://en.wikipedia.org/wiki/Filesystem_in_Userspace,
	  https://github.com/libfuse/libfuse
.. [vfs_fuse] https://www.kernel.org/doc/html/latest/filesystems/vfs.html,
	      https://www.kernel.org/doc/html/latest/filesystems/fuse.html
.. [mount] https://linux.die.net/man/8/mount
.. [fstab] https://en.wikipedia.org/wiki/Fstab


help output
-----------

.. argparse::
   :module: py_fuse_git_bare_fs.fuse_git_bare_fs
   :func: my_argument_parser
   :prog: fuse_git_bare_fs
