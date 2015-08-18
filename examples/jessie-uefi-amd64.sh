#!/bin/bash

set -e

WHO=`whoami`
sudo vmdebootstrap --owner ${WHO} --verbose \
 --sudo --lock-root-password \
 --enable-dhcp --configure-apt \
 --log amd64-uefi.log --log-level debug \
 --size 5G --distribution jessie \
 --grub --use-uefi \
 --package task-xfce-desktop \
 --customize ./examples/qemu-efi-bochs-drm.sh \
 "$@"

