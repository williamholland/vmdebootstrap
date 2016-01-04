#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  vmsquash-tar.py
#
#  Copyright 2015 Neil Williams <codehelp@debian.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import shutil
import cliapp
import logging
import tempfile
from vmdebootstrap.base import runcmd
from vmdebootstrap.filesystem import Filesystem


__version__ = '0.1'
__desc__ = "Helper to make a squashfs from a tarball."

# pylint: disable=missing-docstring


class VmSquash(cliapp.Application):

    def __init__(
            self, progname=None,
            version=__version__, description=__desc__, epilog=None):
        super(VmSquash, self).__init__(
            progname, version,
            description, epilog)
        self.rootdir = None
        self.filesystem = Filesystem()

    def add_settings(self):
        self.settings.boolean(['verbose'], 'report what is going on')
        self.settings.string(['squash'], 'directory for squashfs ',
                             'and boot files', metavar='DIRECTORY')
        self.settings.string(['roottype'], 'specify file system type for /', default='ext4')
        self.settings.string(['tarball'], "tarball of the filesystem",
                             metavar='FILE')

    def message(self, msg):
        logging.info(msg)
        if self.settings['verbose']:
            print msg

    def process_args(self, args):
        """
        Unpack a tarball of the disk's contents,
        shell out to runcmd since it more easily handles rootdir.
        Then run the vmdebootstrap Filesystem squash_rootfs.
        """
        # unpacking tarballs containing device nodes needs root
        if os.geteuid() != 0:
            sys.exit("You need to have root privileges to run this script.")
        self.filesystem.define_settings(self.settings)
        rootdir = tempfile.mkdtemp()
        logging.debug('mkdir %s', rootdir)
        self.message('Unpacking tarball of disk contents')
        self.filesystem.devices['rootdir'] = rootdir
        runcmd(['tar', '-xf', self.settings['tarball'], '-C', rootdir])
        # set rootdir in self.devices
        self.devices = {
            'rootdir': rootdir,
        }
        self.filesystem.squash_rootfs()
        shutil.rmtree(rootdir)


def main():
    VmSquash(version=__version__).run()
    return 0

if __name__ == '__main__':
    main()
    sys.exit()
