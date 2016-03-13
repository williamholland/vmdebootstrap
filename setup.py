#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
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


from setuptools import setup, find_packages


setup(
    name='vmdebootstrap',
    version='1.5',
    description='Bootstrap Debian into a (virtual machine) disk image',
    author='Neil Williams',
    author_email='codehelp@debian.org',
    url='http://git.liw.fi/cgi-bin/cgit/cgit.cgi/vmdebootstrap/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup',
    ],
    packages=[
        'vmdebootstrap',
    ],
    package_data={
        'vmdebootstrap': ['README', 'COPYING', 'NEWS'],
    },
    install_requires=[
        'cliapp >= 1.20150829',
        'distro-info',
    ],
    scripts=['bin/vmdebootstrap']
)
