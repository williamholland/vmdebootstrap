"""
  Wrapper for Grub operations
"""
# -*- coding: utf-8 -*-
#
#  grub.py
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
    umount_wrapper
)
from vmdebootstrap.uefi import arch_table


def grub_serial_console(rootdir):
    cmdline = 'GRUB_CMDLINE_LINUX_DEFAULT="console=tty0 console=tty1 console=ttyS0,38400n8"'
    terminal = 'GRUB_TERMINAL="serial gfxterm"'
    command = 'GRUB_SERIAL_COMMAND="serial --speed=38400 --unit=0 --parity=no --stop=1"'
    grub_cfg = os.path.join(rootdir, 'etc', 'default', 'grub')
    logging.debug("Allowing serial output in grub config %s", grub_cfg)
    with open(grub_cfg, 'a+') as cfg:
        cfg.write("# %s serial support\n" % os.path.basename(__file__))
        cfg.write("%s\n" % cmdline)
        cfg.write("%s\n" % terminal)
        cfg.write("%s\n" % command)


class GrubHandler(Base):

    name = 'grub'

    def __init__(self):
        super(GrubHandler, self).__init__()

    def install_grub2(self, rootdev, rootdir):
        self.message("Configuring grub2")
        # rely on kpartx using consistent naming to map loop0p1 to loop0
        grub_opts = os.path.join('/dev', os.path.basename(rootdev)[:-2])
        if self.settings['serial-console']:
            grub_serial_console(rootdir)
        logging.debug("Running grub-install with options: %s", grub_opts)
        mount_wrapper(rootdir)
        try:
            runcmd(['chroot', rootdir, 'update-grub'])
            runcmd(['chroot', rootdir, 'grub-install', grub_opts])
        except cliapp.AppException as exc:
            logging.warning(exc)
            self.message("Failed. Is grub2-common installed? Using extlinux.")
            umount_wrapper(rootdir)
            return False
        umount_wrapper(rootdir)
        return True

    def install_grub_uefi(self, rootdir):
        ret = True
        self.message("Configuring grub-uefi")
        target = arch_table[self.settings['arch']]['target']
        grub_opts = "--target=%s" % target
        logging.debug("Running grub-install with options: %s", grub_opts)
        mount_wrapper(rootdir)
        try:
            runcmd(['chroot', rootdir, 'update-grub'])
            runcmd(['chroot', rootdir, 'grub-install', grub_opts])
        except cliapp.AppException as exc:
            logging.warning(exc)
            ret = False
            self.message(
                "Failed to configure grub-uefi for %s" %
                self.settings['arch'])
        finally:
            umount_wrapper(rootdir)
        if not ret:
            raise cliapp.AppException("Failed to install grub uefi")

    def install_extra_grub_uefi(self, rootdir):
        ret = True
        extra = arch_table[self.settings['arch']]['extra']
        if extra:
            logging.debug("Installing extra grub support for %s", extra)
            mount_wrapper(rootdir)
            target = arch_table[extra]['target']
            grub_opts = "--target=%s" % target
            self.message("Adding grub target %s" % grub_opts)
            try:
                runcmd(['chroot', rootdir, 'update-grub'])
                runcmd(['chroot', rootdir, 'grub-install', grub_opts])
            except cliapp.AppException as exc:
                logging.warning(exc)
                ret = False
                self.message(
                    "Failed to configure grub-uefi for %s" % extra)
            finally:
                umount_wrapper(rootdir)
            if not ret:
                raise cliapp.AppException("Failed to install extra grub uefi")
