#!/bin/sh

set -e

# define before sourcing common
WHO=`whoami`
USER='user/live'
SUITE='jessie'
SIZE='5G'
ARCH='amd64'
SHARE_PATH='/usr/share/vmdebootstrap/common'
# needs a path for arch and task desktop
IMAGE_PATH='.'

. ${SHARE_PATH}/customise.lib

sudo vmdebootstrap \
 ${BASE_OPTS} --user ${USER} \
 --size ${SIZE} \
 --arch ${ARCH} \
 --no-extlinux \
 --grub --use-uefi \
 --distribution ${SUITE} \
 --customize "${SHARE_PATH}/${SUITE}-${ARCH}-hook.sh" \
 --image ${IMAGE_PATH}/${SUITE}.img \
 "$@"

# report results and check we have something valid.
ls -l ${IMAGE_PATH}/${SUITE}.img
md5sum ${IMAGE_PATH}/${SUITE}.img
