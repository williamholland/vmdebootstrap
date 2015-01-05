#!/bin/sh

set -e

# This script is experimental and incomplete.

# Expects a tarball rootfs which includes a kernel, e.g.
# wandboard6q.sh --tarball wandboard.tgz
# wandboard-uboot.sh /dev/mmcblk0 wandboard.tgz

device=$1
tarball=$2

if [ -z "${device}" ]; then
    echo "Block device not specified"
    exit
fi

if [ ! -f "${device}" ]; then
    echo "Specified device does not exist: ${device}"
    exit
fi

if [ -z "${tarball}" ]; then
    echo "Tarball not specified"
    exit
fi

if [ ! -f '/usr/lib/u-boot/wandboard_quad/u-boot.imx' ]; then
    echo "Unable to find wandboard u-boot file"
    exit
fi

# u-boot needs to be dd'd to the device, not a partition
# but kpartx does not setup the device, just the partitions

sudo dd if=/dev/zero of=${device} bs=1M count=10
sudo dd if=/usr/lib/u-boot/wandboard_quad/u-boot.imx of=${device} seek=1 conv=fsync bs=1k
sudo sfdisk --in-order --Linux --unit M ${device} <<-__EOF__
1,,0x83,-
__EOF__
sudo mkfs.ext4 ${device}p1 -L rootfs

dir=`mktemp -d`
sudo mount ${Ddevice}p1 ${dir}
sudo tar -xzf ${tarball} -C ${dir}

# assumes a single partition deployment to SD card

ver=$(basename `find $rootdir/lib/modules/ -maxdepth 1 -mindepth 1 -type d`)
sudo touch ${dir}/uEnv.txt
sudo chmod 666 ${dir}/uEnv.txt
echo autoload=no > ${dir}/uEnv.txt
echo initrd_high=0xffffffff >> ${dir}/uEnv.txt
echo fdt_high=0xffffffff >> ${dir}/uEnv.txt
echo kernel_addr_r=0x11000000 >> ${dir}/uEnv.txt
echo initrd_addr_r=0x13000000 >> ${dir}/uEnv.txt
echo fdt_addr_r=0x12000000 >> ${dir}/uEnv.txt
echo mmcdev=0 >> ${dir}/uEnv.txt
echo mmcpart=1 >> ${dir}/uEnv.txt
echo ver=3.16.0-4-armmp >> ${dir}/uEnv.txt
echo loadkernel=load mmc ${mmcdev}:${mmcpart} ${kernel_addr_r} boot/vmlinuz-${ver} >> ${dir}/uEnv.txt
echo loadinitrd=load mmc ${mmcdev}:${mmcpart} ${initrd_addr_r} boot/initrd.img-${ver}.uboot; setenv initrd_size ${filesize} >> ${dir}/uEnv.txt
echo loadfdt=load mmc ${mmcdev}:${mmcpart} ${fdt_addr_r} boot/dtbs/imx6q-wandboard.dtb >> ${dir}/uEnv.txt
echo bootargs=console=ttymxc0,115200 root=/dev/mmcblk0p1 rootwait rw ip=dhcp >> ${dir}/uEnv.txt
echo uenvcmd=run loadkernel; run loadinitrd; run loadfdt; bootz ${kernel_addr_r} ${initrd_addr_r} ${fdt_addr_r} >> ${dir}/uEnv.txt
sudo chmod 644 ${dir}/uEnv.txt
sudo umount ${dir}
sudo rm -rf ${dir}
