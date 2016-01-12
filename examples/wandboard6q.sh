#!/bin/sh

set -e

# Important: this example is to create a VM image for wandboard
# To boot the device itself, u-boot support will need to be added
# to a real block device.

user=`whoami`

sudo ./vmdebootstrap \
 --owner ${user} --verbose \
 --size 3G \
 --mirror http://httpredir.debian.org/debian \
 --log wandboard.log --log-level debug \
 --arch armhf \
 --foreign /usr/bin/qemu-arm-static \
 --enable-dhcp \
 --configure-apt \
 --no-extlinux \
 --grub \
 --distribution sid \
 --serial-console-command "/sbin/getty -L ttymxc0 115200 vt100" \
 --customize "./examples/wandboard-customise.sh" \
 "$@"

