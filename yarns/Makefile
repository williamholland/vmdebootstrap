# Copyright 2015  Lars Wirzenius
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
#
# =*= License: GPL-3+ =*=


yarns = $(shell ls [0-9][0-9][0-9]-*.yarn)

all: vmdebootstrap-yarns.pdf vmdebootstrap-yarns.html

vmdebootstrap-yarns.pdf: $(yarns) Makefile
	pandoc --chapters \
		--toc \
		--number-sections \
		-V documentclass:report \
		-o $@ $(yarns)

vmdebootstrap-yarns.html: $(yarns) Makefile yarns.css
	pandoc --chapters \
		--toc \
		--number-sections \
		--standalone \
		--self-contained \
		-H yarns.css \
		-o $@ $(yarns)
