"""
  Wrapper for filesystem utilities
"""
# -*- coding: utf-8 -*-
#
#  filesystem.py
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
import logging
import tempfile
import cliapp
from vmdebootstrap.base import (
    Base,
    runcmd,
    copy_files
)

# pylint: disable=missing-docstring


class Filesystem(Base):

    name = 'filesystem'

    def __init__(self):
        super(Filesystem, self).__init__()
        self.settings = None
        self.devices = {
            'rootdir': None,
            'rootdev': None,
            'bootdev': None,
            'boottype': None,
            'roottype': None,
            'swapdev': None,
        }

    def define_settings(self, settings):
        self.settings = settings
        self.devices['roottype'] = self.settings['roottype']
        self.devices['boottype'] = self.settings['boottype']

    def chown(self):
        if not self.settings['owner']:
            return
        # Change image owner after completed build
        if self.settings['image']:
            filename = self.settings['image']
        elif self.settings['tarball']:
            filename = self.settings['tarball']
        elif self.settings['squash']:
            filename = self.settings['squash']
        else:
            return
        self.message("Changing owner to %s" % self.settings["owner"])
        runcmd(["chown", "-R", self.settings["owner"], filename])

    def update_initramfs(self):
        rootdir = self.devices['rootdir']
        if not rootdir:
            raise cliapp.AppException("rootdir not set")
        if not os.path.exists(
                os.path.join(rootdir, 'usr', 'sbin', 'update-initramfs')):
            self.message("Error: Unable to run update-initramfs.")
            return
        if 'no-update-initramfs' in self.settings or not self.settings['update-initramfs']:
            return
        cmd = os.path.join('usr', 'sbin', 'update-initramfs')
        if os.path.exists(os.path.join(str(rootdir), cmd)):
            self.message("Updating the initramfs")
            runcmd(['chroot', rootdir, cmd, '-u'])

    def setup_kpartx(self):
        bootindex = None
        swapindex = None
        out = runcmd(['kpartx', '-avs', self.settings['image']])
        if self.settings['bootsize'] and self.settings['swap'] > 0:
            bootindex = 0
            rootindex = 1
            swapindex = 2
            parts = 3
        elif self.settings['use-uefi']:
            bootindex = 0
            rootindex = 1
            parts = 2
        elif self.settings['use-uefi'] and self.settings['swap'] > 0:
            bootindex = 0
            rootindex = 1
            swapindex = 2
            parts = 3
        elif self.settings['bootsize']:
            bootindex = 0
            rootindex = 1
            parts = 2
        elif self.settings['swap'] > 0:
            rootindex = 0
            swapindex = 1
            parts = 2
        else:
            rootindex = 0
            parts = 1
        boot = None
        swap = None
        devices = [line.decode('utf-8').split()[2]
                   for line in out.splitlines()
                   if line.decode('utf-8').startswith('add map ')]
        if len(devices) != parts:
            msg = 'Surprising number of partitions - check output of losetup -a'
            logging.debug("%s", runcmd(['losetup', '-a']))
            logging.debug("%s: devices=%s parts=%s", msg, devices, parts)
            raise cliapp.AppException(msg)
        root = '/dev/mapper/%s' % devices[rootindex]
        if self.settings['bootsize'] or self.settings['use-uefi']:
            boot = '/dev/mapper/%s' % devices[bootindex].decode('utf-8')
        if self.settings['swap'] > 0:
            swap = '/dev/mapper/%s' % devices[swapindex]
        self.devices['rootdev'] = root
        self.devices['bootdev'] = boot
        self.devices['swap'] = swap

    def mkfs(self, device, fstype, opt=None):
        self.message('Creating filesystem %s' % fstype)
        if opt:
            runcmd(['mkfs', '-t', fstype, '-O', opt, device])
        else:
            runcmd(['mkfs', '-t', fstype, device])

    def create_fstab(self):
        rootdir = self.devices['rootdir']
        rootdev = self.devices['rootdev']
        bootdev = self.devices['bootdev']
        boottype = self.devices['boottype']
        roottype = self.devices['roottype']

        def fsuuid(device):
            out = runcmd(['blkid', '-c', '/dev/null', '-o', 'value',
                          '-s', 'UUID', device])
            return out.splitlines()[0].strip()

        if rootdev:
            rootdevstr = 'UUID=%s' % fsuuid(rootdev)
        else:
            rootdevstr = '/dev/sda1'

        if bootdev and not self.settings['use-uefi']:
            bootdevstr = 'UUID=%s' % fsuuid(bootdev)
        else:
            bootdevstr = None

        if not rootdir:
            raise cliapp.AppException("rootdir not set")

        fstab = os.path.join(str(rootdir), 'etc', 'fstab')
        with open(fstab, 'w') as fstab:
            fstab.write('proc /proc proc defaults 0 0\n')
            fstab.write('%s / %s %s 0 1\n' %
                        (rootdevstr, roottype, self.get_mount_flags(roottype)))
            if bootdevstr:
                fstab.write('%s /boot %s %s 0 2\n' %
                            (bootdevstr, boottype, self.get_mount_flags(boottype)))
                if self.settings['swap'] > 0:
                    fstab.write("/dev/sda3 swap swap defaults 0 0\n")
            elif self.settings['swap'] > 0:
                fstab.write("/dev/sda2 swap swap defaults 0 0\n")

    @staticmethod
    def get_mount_flags(fstype):
        """Return the fstab mount flags for a given file system type."""
        flags = ['errors=remount-ro']
        if fstype == 'btrfs':
            flags = []

        return ','.join(flags) or 'defaults'

    def squash_rootfs(self):
        """
        Run squashfs on the rootfs within the image.
        Copy the initrd and the kernel out, squashfs the rest.
        Also UEFI files, if enabled, ESP partition as a vfat image. TBD.
        """
        if not self.settings['squash']:
            return
        if not os.path.exists('/usr/bin/mksquashfs'):
            logging.warning("Squash selected but mksquashfs not found!")
            return
        if not os.path.exists(self.settings['squash']):
            os.makedirs(self.settings['squash'])
        suffixed = os.path.join(self.settings['squash'], "filesystem.squashfs")
        if os.path.exists(suffixed):
            os.unlink(suffixed)
        _, exclusions = tempfile.mkstemp()
        with open(exclusions, 'w') as exclude:
            exclude.write("/proc\n")
            exclude.write("/dev\n")
            exclude.write("/sys\n")
            exclude.write("/run\n")
        self.message("Running mksquashfs on rootfs.")
        msg = runcmd(
            ['nice', 'mksquashfs', self.devices['rootdir'], suffixed,
             '-no-progress', '-comp', 'xz',
             '-e', exclusions], ignore_fail=False)
        os.unlink(exclusions)
        logging.debug(msg)
        check_size = os.path.getsize(suffixed)
        logging.debug("Created squashfs: %s", suffixed)
        if check_size < (1024 * 1024):
            logging.warning(
                "%s appears to be too small! %s bytes",
                suffixed, check_size)
        else:
            logging.debug("squashed size: %s", check_size)
        bootdir = os.path.join(self.devices['rootdir'], 'boot')
        # copying the boot/* files
        self.message("Copying boot files out of squashfs")
        copy_files(bootdir, self.settings['squash'])

    def configure_apt(self):
        rootdir = self.devices['rootdir']
        if not self.settings['configure-apt'] or not self.settings['apt-mirror']:
            return
        if not rootdir:
            raise cliapp.AppException("rootdir not set")
        # use the distribution and mirror to create an apt source
        self.message("Configuring apt to use distribution and mirror")
        conf = os.path.join(str(rootdir), 'etc', 'apt', 'sources.list.d', 'base.list')
        logging.debug('configure apt %s', conf)
        mirror = self.settings['mirror']
        if self.settings['apt-mirror']:
            mirror = self.settings['apt-mirror']
            self.message("Setting apt mirror to %s" % mirror)
        os.unlink(os.path.join(str(rootdir), 'etc', 'apt', 'sources.list'))
        source = open(conf, 'w')
        line = 'deb %s %s main\n' % (mirror, self.settings['distribution'])
        source.write(line)
        line = '#deb-src %s %s main\n' % (mirror, self.settings['distribution'])
        source.write(line)
        source.close()
        # ensure the apt sources have valid lists
        runcmd(['chroot', rootdir, 'apt-get', '-qq', 'update'])

    def list_installed_pkgs(self):
        if not self.settings['pkglist']:
            return
        rootdir = self.devices['rootdir']
        # output the list of installed packages for sources identification
        self.message("Creating a list of installed binary package names")
        out = runcmd(['chroot', rootdir,
                      'dpkg-query', '-W', "-f='${Package}.deb\n'"])
        with open('dpkg.list', 'w') as dpkg:
            dpkg.write(out)

    def remove_udev_persistent_rules(self):
        rootdir = self.devices['rootdir']
        if not rootdir:
            raise cliapp.AppException("rootdir not set")
        self.message('Removing udev persistent cd and net rules')
        for xrule in ['70-persistent-cd.rules', '70-persistent-net.rules']:
            pathname = os.path.join(str(rootdir), 'etc', 'udev', 'rules.d', xrule)
            if os.path.exists(pathname):
                logging.debug('rm %s', pathname)
                os.remove(pathname)
            else:
                logging.debug('not removing non-existent %s', pathname)

    def set_hostname(self):
        rootdir = self.devices['rootdir']
        hostname = self.settings['hostname']
        if not rootdir:
            raise cliapp.AppException("rootdir not set")
        with open(os.path.join(str(rootdir), 'etc', 'hostname'), 'w') as fhost:
            fhost.write('%s\n' % hostname)

        etc_hosts = os.path.join(str(rootdir), 'etc', 'hosts')
        try:
            with open(etc_hosts, 'r') as fhost:
                data = fhost.read()
            with open(etc_hosts, 'w') as fhosts:
                for line in data.splitlines():
                    if line.startswith('127.0.0.1'):
                        line += ' %s' % hostname
                    fhosts.write('%s\n' % line)
        except IOError:
            pass

    def make_rootfs_part(self, extent):
        bootsize = self.settings['esp-size'] / (1024 * 1024) + 1
        runcmd(['parted', '-s', self.settings['image'],
                'mkpart', 'primary', str(bootsize), extent])

    def convert_image_to_qcow2(self):
        """
        Current images are all prepared as raw
        rename to .raw and let the conversion put the
        original name back
        """
        if not self.settings['convert-qcow2'] or not self.settings['image']:
            return
        self.message('Converting raw image to qcow2')
        tmpname = self.settings['image'] + '.raw'
        os.rename(self.settings['image'], tmpname)
        runcmd(['qemu-img', 'convert', '-O', 'qcow2',
                tmpname, self.settings['image']])
