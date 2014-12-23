#!/bin/sh

set -e

rootdir=$1
image=$2

if [ -z "${image}" ]; then
	echo "Image not specified"
	exit
fi

if [ ! -f '/usr/lib/u-boot/wandboard_quad/u-boot.imx' ]; then
	echo "Unable to find wandboard u-boot file"
	exit
fi

# u-boot needs to be dd'd to the device, not a partition
# but kpartx does not setup the device, just the partitions

dd if=/usr/lib/u-boot/wandboard_quad/u-boot.imx of=${image} seek=1 conv=fsync bs=1k

mkdir -p $rootdir/boot/dtbs
cp $rootdir/usr/lib/linux-image-*-armmp/* $rootdir/boot/dtbs

for module in ahci_platform ahci_imx sd-mod; do
	echo ${module} >> ${rootdir}/etc/initramfs-tools/modules 
done
