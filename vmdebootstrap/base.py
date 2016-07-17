"""
  Base for common utility functions
"""
# -*- coding: utf-8 -*-
#
#  base.py
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
import crypt
import shutil
import logging
import subprocess
import cliapp

# pylint: disable=missing-docstring


def runcmd(argv, stdin='', ignore_fail=False, env=None, **kwargs):
    logging.debug('runcmd: %s %s %s', argv, env, kwargs)
    proc = subprocess.Popen(
        argv, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=env, **kwargs)
    out, err = proc.communicate(stdin)
    if proc.returncode != 0:
        msg = 'command failed: %s\n%s\n%s' % (argv, out, err)
        logging.error(msg)
        if not ignore_fail:
            raise cliapp.AppException(msg)
    return out


# FIXME: use contextmanager
def mount_wrapper(rootdir):
    runcmd(['mount', '/dev', '-t', 'devfs', '-obind',
            '%s' % os.path.join(rootdir, 'dev')])
    runcmd(['mount', '/dev/pts', '-t', 'devpts', '-obind',
            '%s' % os.path.join(rootdir, 'dev', 'pts')])
    runcmd(['mount', '/proc', '-t', 'proc', '-obind',
            '%s' % os.path.join(rootdir, 'proc')])
    runcmd(['mount', '/sys', '-t', 'sysfs', '-obind',
            '%s' % os.path.join(rootdir, 'sys')])


def umount_wrapper(rootdir):
    runcmd(['umount', os.path.join(rootdir, 'sys')])
    runcmd(['umount', os.path.join(rootdir, 'proc')])
    runcmd(['umount', os.path.join(rootdir, 'dev', 'pts')])
    runcmd(['umount', os.path.join(rootdir, 'dev')])


def cleanup_apt_cache(rootdir):
    out = runcmd(['chroot', rootdir, 'apt-get', 'clean'])
    logging.debug('stdout:\n%s', out)


def set_password(rootdir, user, password):
    encrypted = crypt.crypt(password, '..')
    runcmd(['chroot', rootdir, 'usermod', '-p', encrypted, user])


def delete_password(rootdir, user):
    runcmd(['chroot', rootdir, 'passwd', '-d', user])


def copy_files(src, dest):
    for filename in os.listdir(src):
        src_path = os.path.join(src, filename)
        if os.path.isdir(src_path) or os.path.islink(src_path):
            continue
        shutil.copyfile(
            src_path,
            os.path.join(dest, filename))


class Base(object):

    name = 'base'

    def __init__(self):
        super(Base, self).__init__()
        self.settings = None

    def define_settings(self, settings):
        self.settings = settings

    def message(self, msg):
        logging.info(msg)
        if self.settings['verbose']:
            print(msg)  # pylint: disable=superfluous-parens

    def create_empty_image(self):
        self.message('Creating disk image')
        runcmd(['qemu-img', 'create', '-f', 'raw',
                self.settings['image'],
                str(self.settings['size'])])

    def create_tarball(self, rootdir):
        # Create a tarball of the disk's contents
        # shell out to runcmd since it more easily handles rootdir
        self.message('Creating tarball of disk contents')
        runcmd(['tar', '-cf', self.settings['tarball'], '-C', rootdir, '.'])

    def mkfs(self, device, fstype):
        self.message('Creating filesystem %s' % fstype)
        runcmd(['mkfs', '-t', fstype, device])

    def set_root_password(self, rootdir):
        if self.settings['root-password']:
            self.message('Setting root password')
            set_password(rootdir, 'root', self.settings['root-password'])
        elif self.settings['lock-root-password']:
            self.message('Locking root password')
            runcmd(['chroot', rootdir, 'passwd', '-l', 'root'])
        else:
            self.message('Give root an empty password')
            delete_password(rootdir, 'root')

    def create_users(self, rootdir):
        def create_user(vmuser):
            runcmd(['chroot', rootdir, 'adduser', '--gecos', vmuser,
                    '--disabled-password', vmuser])
            if self.settings['sudo']:
                runcmd(['chroot', rootdir, 'adduser', vmuser, 'sudo'])

        for userpass in self.settings['user']:
            if '/' in userpass:
                user, password = userpass.split('/', 1)
                create_user(user)
                set_password(rootdir, user, password)
            else:
                create_user(userpass)
                delete_password(rootdir, userpass)

    def customize(self, rootdir):
        script = self.settings['customize']
        if not script:
            return
        if not os.path.exists(script):
            example = os.path.join("/usr/share/vmdebootstrap/examples/", script)
            if not os.path.exists(example):
                self.message("Unable to find %s" % script)
                return
            script = example
        self.message('Running customize script %s' % script)
        logging.info("rootdir=%s", rootdir)
        try:
            with open('/dev/tty', 'w') as tty:
                cliapp.runcmd([script, rootdir, self.settings['image']], stdout=tty, stderr=tty)
        except IOError:
            logging.debug('tty unavailable, trying in headless mode.')
            subprocess.call([script, rootdir, self.settings['image']])

    def append_serial_console(self, rootdir):
        if self.settings['serial-console']:
            serial_command = self.settings['serial-console-command']
            logging.debug('adding getty to serial console')
            inittab = os.path.join(rootdir, 'etc/inittab')
            # to autologin, serial_command can contain '-a root'
            with open(inittab, 'a') as ftab:
                ftab.write('\nS0:23:respawn:%s\n' % serial_command)

    def check_swap_size(self):
        # swap - modifies extent
        extent = '100%'
        swap = 256 * 1024 * 1024
        if self.settings['swap'] > 0:
            if self.settings['swap'] > swap:
                swap = self.settings['swap']
            else:
                # minimum 256MB as default qemu ram is 128MB
                logging.debug("Setting minimum 256MB swap space")
            extent = "%s%%" % int(100 * (self.settings['size'] - swap) / self.settings['size'])
        return extent

    def make_swap(self, extent):
        if self.settings['swap'] > 0:
            logging.debug("Creating swap partition")
            runcmd([
                'parted', '-s', self.settings['image'],
                'mkpart', 'primary', 'linux-swap', extent, '100%'])

    def base_packages(self):
        packages = []
        if not self.settings['foreign'] and not self.settings['no-acpid']:
            packages.append('acpid')
        if self.settings['sudo']:
            packages.append('sudo')
        if not self.settings['no-kernel']:
            if self.settings['kernel-package']:
                packages.append(self.settings['kernel-package'])
        return packages
