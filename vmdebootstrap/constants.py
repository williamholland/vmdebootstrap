"""
  Constants which can be used by any handler
"""
# -*- coding: utf-8 -*-
#
#  constants.py
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


arch_table = {  # pylint: disable=invalid-name
    'amd64': {
        'removable': '/EFI/boot/bootx64.efi',  # destination location
        'install': '/EFI/debian/grubx64.efi',  # package location
        'package': 'grub-efi-amd64',  # bootstrap package
        'bin_package': 'grub-efi-amd64-bin',  # binary only
        'extra': 'i386',  # architecture to add binary package
        'exclusive': False,  # only EFI supported for this arch.
        'target': 'x86_64-efi',  # grub target name
    },
    'i386': {
        'removable': '/EFI/boot/bootia32.efi',
        'install': '/EFI/debian/grubia32.efi',
        'package': 'grub-efi-ia32',
        'bin_package': 'grub-efi-ia32-bin',
        'extra': None,
        'exclusive': False,
        'target': 'i386-efi',
    },
    'arm64': {
        'removable': '/EFI/boot/bootaa64.efi',
        'install': '/EFI/debian/grubaa64.efi',
        'package': 'grub-efi-arm64',
        'bin_package': 'grub-efi-arm64-bin',
        'extra': None,
        'exclusive': True,
        'target': 'arm64-efi',
    }
}
