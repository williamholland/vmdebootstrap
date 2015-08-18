#!/bin/bash

set -e

rootdir=$1

echo "blacklist bochs-drm" > $rootdir/etc/modprobe.d/qemu-blacklist.conf

