#! /usr/bin/python
# -*- coding: utf-8 -*-
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
import cliapp
import guestfs
import tarfile
import logging

__version__ = '0.1'
__desc__ = "Helper to mount an image read-only and extract files" + \
           " or directories."


# pylint: disable=missing-docstring


class VmExtract(cliapp.Application):  # pylint: disable=too-many-public-methods
    """
    Support for extracting useful content from VM images.
    For example, to assist in validation.
    """

    def __init__(
            self, progname=None,
            version=__version__, description=__desc__, epilog=None):
        super(VmExtract, self).__init__(
            progname, version,
            description, epilog)
        self.guest_os = None
        self.mps = []

    def add_settings(self):
        self.settings.boolean(
            ['verbose'], 'report what is going on')
        self.settings.string(
            ['image'], 'image to read', metavar='FILE')
        self.settings.string(
            ['directory'], 'directory to extract as a tarball.')
        self.settings.string_list(
            ['path'], 'path to the filename to extract - can repeat.')
        self.settings.boolean(
            ['boot'], 'mount the boot partition as well as root')
        self.settings.string(
            ['filename'],
            'name of tarball containing the extracted directory',
            default='vmextract.tgz',
            metavar='FILE')

    # pylint: disable=too-many-branches,too-many-statements
    def process_args(self, args):

        if not self.settings['image']:
            raise cliapp.AppException(
                'You must give an image to read')
        if not self.settings['directory'] and not self.settings['path']:
            raise cliapp.AppException(
                'You must provide either a filename or directory '
                'to extract')

        try:
            self.prepare()
            self.mount_root()
            if self.settings['boot']:
                self.mount_boot()
            if self.settings['directory']:
                self.extract_directory()
            elif self.settings['path']:
                for path in self.settings['path']:
                    self.download(path)
        except BaseException as exc:
            self.message('EEEK! Something bad happened... %s' % exc)
            sys.exit(1)

    def message(self, msg):
        logging.info(msg)
        if self.settings['verbose']:
            print(msg)

    def prepare(self):
        """
        Initialise guestfs
        """
        self.message("Preparing %s" % self.settings['image'])
        self.guest_os = guestfs.GuestFS(python_return_dict=True)
        self.guest_os.add_drive_opts(
            self.settings['image'],
            format="raw",
            readonly=1)
        # ensure launch is only called once per run
        self.guest_os.launch()
        drives = self.guest_os.inspect_os()
        self.mps = self.guest_os.inspect_get_mountpoints(drives[0])

    def download(self, path):
        """
        Copy a single file out of the image
        If a filename is not specified, use the basename of the original.
        """
        filename = os.path.basename(path)
        self.message(
            "Extracting %s as %s" % (path, filename))
        self.guest_os.download(path, filename)
        if not os.path.exists(filename):
            return RuntimeError("Download failed")

    def mount_root(self):
        """
        Mounts the root partition to /
        """
        root = [part for part in self.mps if part == '/'][0]
        if not root:
            raise RuntimeError("Unable to identify root partition")
        self.guest_os.mount_ro(self.mps[root], '/')

    def mount_boot(self):
        """
        Mounts the /boot partition to a new /boot mountpoint
        """
        boot = [part for part in self.mps if part == '/boot'][0]
        if not boot:
            raise RuntimeError("Unable to identify boot partition")
        if not self.guest_os.is_dir('/boot'):
            self.guest_os.mkmountpoint('/boot')
        self.guest_os.mount_ro(self.mps[boot], '/boot')

    def extract_directory(self):
        """
        Create a tarball of a complete directory existing in the image.
        """
        if not self.settings['filename']:
            self.settings['filename'] = 'vmextract.tgz'
        self.guest_os.tar_out(
            self.settings['directory'],
            self.settings['filename'], compress='gzip')
        if not tarfile.is_tarfile(self.settings['filename']):
            raise RuntimeError("Extraction failed")


def main():
    VmExtract(version=__version__).run()
    return 0


if __name__ == '__main__':
    main()
