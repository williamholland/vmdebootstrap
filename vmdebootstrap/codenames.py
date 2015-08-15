"""
  Wrapper for distro information
"""
# -*- coding: utf-8 -*-
#
#  codenames.py
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

import datetime
from vmdebootstrap.base import Base
from distro_info import DebianDistroInfo, UbuntuDistroInfo

# pylint: disable=missing-docstring


class Codenames(Base):

    name = 'codenames'

    def __init__(self):
        super(Codenames, self).__init__()
        self.debian_info = DebianDistroInfo()
        self.ubuntu_info = UbuntuDistroInfo()
        self.settings = None

    def define_settings(self, settings):
        self.settings = settings

    def suite_to_codename(self, distro):
        suite = self.debian_info.codename(distro, datetime.date.today())
        if not suite:
            return distro
        return suite

    def was_oldstable(self, limit):
        suite = self.suite_to_codename(self.settings['distribution'])
        # this check is only for debian
        if not self.debian_info.valid(suite):
            return False
        return suite == self.debian_info.old(limit)

    def was_stable(self, limit):
        suite = self.suite_to_codename(self.settings['distribution'])
        # this check is only for debian
        if not self.debian_info.valid(suite):
            return False
        return suite == self.debian_info.stable(limit)
