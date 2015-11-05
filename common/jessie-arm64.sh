#!/bin/sh

set -e

# define before sourcing common
WHO=`whoami`
USER='user/live'
SUITE='jessie'
SIZE='5G'
ARCH='arm64'
BINFMT='/usr/bin/qemu-aarch64-static'
SHARE_PATH='/usr/share/vmdebootstrap/common'
# needs a path for arch and task desktop
IMAGE_PATH='.'

. ${SHARE_PATH}/customise.lib

sudo vmdebootstrap \
 ${BASE_OPTS} --user ${USER} \
 --size ${SIZE} \
 --arch ${ARCH} \
 --foreign ${BINFMT} \
 --no-extlinux \
 --grub --use-uefi \
 --package dosfstools \
 --distribution ${SUITE} \
 --customize "${SHARE_PATH}/${SUITE}-${ARCH}-hook.sh" \
 --image ${IMAGE_PATH}/${SUITE}-${ARCH}.img \
 "$@"

# report results and check we have something valid.
ls -l ${IMAGE_PATH}/${SUITE}-${ARCH}.img
md5sum ${IMAGE_PATH}/${SUITE}-${ARCH}.img
