"""
  Wrapper for network support
"""
# -*- coding: utf-8 -*-
#
#  network.py
#  
#  Copyright 2015 Neil Williams <codehelp@debian.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import os
from vmdebootstrap.base import (
    Base,
    runcmd,
)

# pylint: disable=missing-docstring


class Networking(Base):

    name = 'networking'

    def _write_network_interfaces(self, rootdir, line):
        self.message('Setting up networking')
        ifc_d = os.path.join(rootdir, 'etc', 'network', 'interfaces.d')
        ifc_file = os.path.join(rootdir, 'etc', 'network', 'interfaces')
        with open(ifc_file, 'w') as netfile:
            netfile.write(line)
        if not os.path.exists(ifc_d):
            os.mkdir(ifc_d)
        with open(ethpath, 'w') as eth:
            eth.write('auto lo\n')
            eth.write('iface lo inet loopback\n')
            if self.settings['enable-dhcp']:
                eth.write('\n')
                eth.write('auto eth0\n')
                eth.write('iface eth0 inet dhcp\n')

    def setup_wheezy_networking(self, rootdir):
        """
        unconditionally write for wheezy
        (which became oldstable on 2015.04.25)
        """
        self._write_network_interfaces(
            rootdir, 'source /etc/network/interfaces.d/*\n')

    def setup_networking(self, rootdir):
        self._write_network_interfaces(
            rootdir, 'source-directory /etc/network/interfaces.d\n')

    def systemd_support(self, rootdir):
        """
        Handle the systemd-networkd setting
        """
        if self.settings['systemd-networkd']:
            self.enable_systemd_networkd(rootdir)
        else:
            self.mask_udev_predictable_rules(rootdir)

    def mask_udev_predictable_rules(self, rootdir):
        """
        This can be reset later but to get networking using eth0
        immediately upon boot, the interface we're going to use must
        be known and must update the initramfs after setting up the
        mask.
        """
        self.message('Disabling systemd predictable interface names')
        udev_path = os.path.join(
            'etc', 'udev', 'rules.d', '80-net-setup-link.rules')
        runcmd(['chroot', rootdir, 'ln', '-s', '/dev/null', udev_path])

    def enable_systemd_networkd(self, rootdir):
        """
        Get networking working immediately on boot, allow any en* interface
        to be enabled by systemd-networkd using DHCP
        https://coreos.com/os/docs/latest/network-config-with-networkd.html
        http://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/
        """
        if not self.settings['enable-dhcp']:
            return
        self.message('Enabling systemd-networkd for DHCP')
        ethpath = os.path.join(rootdir, 'etc', 'systemd', 'network', '99-dhcp.network')
        with open(ethpath, 'w') as eth:
            eth.write('[Match]\n')
            eth.write('Name=en*\n')
            eth.write('\n[Network]\n')
            eth.write('DHCP=yes\n')
        runcmd(['chroot', rootdir, 'systemctl', 'enable', 'systemd-networkd'])
