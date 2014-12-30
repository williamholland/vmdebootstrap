#!/bin/sh

set -e

rootdir=$1

mkdir -p $rootdir/boot/dtbs
cp $rootdir/usr/lib/linux-image-*-armmp/* $rootdir/boot/dtbs

for module in ahci_platform ahci_imx sd-mod; do
	echo ${module} >> ${rootdir}/etc/initramfs-tools/modules 
done
