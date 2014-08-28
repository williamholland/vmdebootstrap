#!/bin/sh

set -e

rootdir=$1

# copy u-boot to the boot partition
cp $rootdir/usr/lib/u-boot/am335x_boneblack/MLO $rootdir/boot/MLO
cp $rootdir/usr/lib/u-boot/am335x_boneblack/u-boot.img $rootdir/boot/u-boot.img

# Setup uEnv.txt
kernelVersion=$(basename `dirname $rootdir/usr/lib/*/am335x-boneblack.dtb`)
version=$(echo $kernelVersion | sed 's/linux-image-\(.*\)/\1/')
initRd=initrd.img-$version
vmlinuz=vmlinuz-$version

# uEnv.txt for Beaglebone
# based on https://github.com/beagleboard/image-builder/blob/master/target/boot/beagleboard.org.txt
cat >> $rootdir/boot/uEnv.txt <<EOF
mmcroot=/dev/mmcblk0p2 ro
mmcrootfstype=ext4 rootwait fixrtc

console=ttyO0,115200n8

kernel_file=$vmlinuz
initrd_file=$initRd

loadaddr=0x80200000
initrd_addr=0x81000000
fdtaddr=0x80F80000

initrd_high=0xffffffff
fdt_high=0xffffffff

loadkernel=load mmc \${mmcdev}:\${mmcpart} \${loadaddr} \${kernel_file}
loadinitrd=load mmc \${mmcdev}:\${mmcpart} \${initrd_addr} \${initrd_file}; setenv initrd_size \${filesize}
loadfdt=load mmc \${mmcdev}:\${mmcpart} \${fdtaddr} /dtbs/\${fdtfile}

loadfiles=run loadkernel; run loadinitrd; run loadfdt
mmcargs=setenv bootargs console=tty0 console=\${console} root=\${mmcroot} rootfstype=\${mmcrootfstype}

uenvcmd=run loadfiles; run mmcargs; bootz \${loadaddr} \${initrd_addr}:\${initrd_size} \${fdtaddr}
EOF

mkdir -p $rootdir/boot/dtbs
cp $rootdir/usr/lib/linux-image-*-armmp/* $rootdir/boot/dtbs
