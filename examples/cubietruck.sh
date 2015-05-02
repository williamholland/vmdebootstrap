#!/bin/sh

set -e

user=`whoami`

sudo vmdebootstrap \
 --owner ${user} --verbose \
 --size 3G \
 --mirror http://http.debian.net/debian \
 --log cubietruck.log --log-level debug \
 --arch armhf \
 --foreign /usr/bin/qemu-arm-static \
 --enable-dhcp \
 --configure-apt \
 --distribution sid \
 --serial-console-command "/sbin/getty -L ttyS0 115200 vt100" \
 --customize "cubietruck-customise.sh" \
 "$@"
