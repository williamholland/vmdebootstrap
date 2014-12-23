#!/bin/sh

set -e

rootdir=$1
image=$2

if [ -z "${image}" ]; then
	echo "Image not specified"
	exit
fi

if [ ! -f '/usr/lib/u-boot/Cubietruck/u-boot-sunxi-with-spl.bin' ]; then
	echo "Unable to find cubietruck u-boot file"
	exit
fi

# u-boot needs to be dd'd to the device, not a partition
# but kpartx does not setup the device, just the partitions

dd if=/usr/lib/u-boot/Cubietruck/u-boot-sunxi-with-spl.bin of=${image} bs=1k seek=8

mkdir -p $rootdir/boot/dtbs
cp $rootdir/usr/lib/linux-image-*-armmp/* $rootdir/boot/dtbs
