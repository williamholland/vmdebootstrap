"""
  Wrapper for UEFI operations
"""
# -*- coding: utf-8 -*-
#
#  uefi.py
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


# pylint: disable=missing-docstring,duplicate-code


import os
import cliapp
import logging
from vmdebootstrap.base import (
    Base,
    runcmd,
    mount_wrapper,
    umount_wrapper,
)
from vmdebootstrap.constants import arch_table


class Uefi(Base):

    name = 'uefi'

    def __init__(self):
        super(Uefi, self).__init__()
        self.bootdir = None

    def efi_packages(self):
        packages = []
        pkg = arch_table[self.settings['arch']]['package']
        self.message("Adding %s" % pkg)
        packages.append(pkg)
        extra = arch_table[self.settings['arch']]['extra']
        if extra and isinstance(extra, str):
            bin_pkg = arch_table[str(extra)]['bin_package']
            self.message("Adding support for %s using %s" % (extra, bin_pkg))
            packages.append(bin_pkg)
        return packages

    def copy_efi_binary(self, efi_removable, efi_install):
        logging.debug("using bootdir=%s", self.bootdir)
        if efi_removable.startswith('/'):
            efi_removable = efi_removable[1:]
        if efi_install.startswith('/'):
            efi_install = efi_install[1:]
        efi_output = os.path.join(self.bootdir, efi_removable)
        efi_input = os.path.join(self.bootdir, efi_install)
        logging.debug("moving %s to %s", efi_output, efi_input)
        if not os.path.exists(efi_input):
            logging.warning("%s does not exist (%s)", efi_input, efi_install)
            raise cliapp.AppException("Missing %s" % efi_input)
        if not os.path.exists(os.path.dirname(efi_output)):
            os.makedirs(os.path.dirname(efi_output))
        logging.debug(
            'Moving UEFI support: %s -> %s', efi_input, efi_output)
        if os.path.exists(efi_output):
            os.unlink(efi_output)
        os.rename(efi_input, efi_output)

    def configure_efi(self, rootdir):
        """
        Copy the bootloader file from the package into the location
        so needs to be after grub and kernel already installed.
        """
        self.message('Configuring EFI')
        mount_wrapper(rootdir)
        efi_removable = str(arch_table[self.settings['arch']]['removable'])
        efi_install = str(arch_table[self.settings['arch']]['install'])
        self.message('Installing UEFI support binary')
        logging.debug("moving %s to %s", efi_removable, efi_install)
        try:
            self.copy_efi_binary(efi_removable, efi_install)
        finally:
            umount_wrapper(rootdir)

    def configure_extra_efi(self, rootdir):
        extra = arch_table[self.settings['arch']]['extra']
        if extra:
            mount_wrapper(rootdir)
            efi_removable = str(arch_table[extra]['removable'])
            efi_install = str(arch_table[extra]['install'])
            self.message('Copying UEFI support binary for %s' % extra)
            try:
                self.copy_efi_binary(efi_removable, efi_install)
            finally:
                umount_wrapper(rootdir)

    def partition_esp(self):
        if not self.settings['use-uefi']:
            return
        espsize = self.settings['esp-size'] / (1024 * 1024)
        self.message("Using ESP size: %smib %s bytes" % (espsize, self.settings['esp-size']))
        runcmd(['parted', '-s', self.settings['image'],
                'mkpart', 'primary', 'fat32',
                '1', str(espsize)])
        runcmd(['parted', '-s', self.settings['image'],
                'set', '1', 'boot', 'on'])
        runcmd(['parted', '-s', self.settings['image'],
                'set', '1', 'esp', 'on'])

    def prepare_esp(self, rootdir, bootdev):
        self.bootdir = '%s/%s/%s' % (rootdir, 'boot', 'efi')
        logging.debug("bootdir:%s", self.bootdir)
        self.mkfs(bootdev, fstype='vfat')
        os.makedirs(self.bootdir)
        return self.bootdir
