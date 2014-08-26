#!/bin/sh

set -e

sudo vmdebootstrap \
 --owner $(whoami) --verbose \
 --size 3G \
 --mirror http://http.debian.net/debian \
 --log cubietruck.log --log-level debug \
 --arch armhf \
 --foreign /usr/bin/qemu-arm-static \
 --enable-dhcp \
 --configure-apt \
 --no-extlinux \
 --no-kernel \
 --package u-boot \
 --package linux-image-armmp \
 --distribution sid \
 --serial-console-command "/sbin/getty -L ttyS0 115200 vt100" \
 --customize "cubietruck-customise.sh" \
 --serial-console-command \
 --bootsize 50m --boottype vfat \
 "$@"
