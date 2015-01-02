#!/bin/sh

set -e

rootdir=$1

mkdir -p $rootdir/boot/dtbs
cp $rootdir/usr/lib/linux-image-*-armmp/* $rootdir/boot/dtbs

for module in phy-sun4i-usb ohci-platform; do
	echo ${module} >> ${rootdir}/etc/initramfs-tools/modules 
done
