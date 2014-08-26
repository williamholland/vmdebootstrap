#!/bin/sh

set -e

rootdir=$1

# u-boot needs to be dd'd to the partition
#cp /usr/lib/u-boot/Cubietruck/uboot.elf /boot/
#cp /usr/lib/u-boot/Cubietruck/u-boot-sunxi-with-spl.bin /boot/

mkdir -p $rootdir/boot/dtbs
cp $rootdir/usr/lib/linux-image-*-armmp/* $rootdir/boot/dtbs
