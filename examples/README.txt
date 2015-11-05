Examples
========

The Freedombox project are using vmdebootstrap for ARM based images.

http://anonscm.debian.org/cgit/freedombox/freedom-maker.git/

Those scripts have been adapted to work directly within vmdebootstrap
as customise scripts in this examples directory.

There are also examples which fold all of the options into a single
script which just needs to be called with a size and an image name.

The only required argument for each example is the image name.

Beaglebone-black
----------------

/usr/share/vmdebootstrap/examples/beagleboneblack.sh --image bbb.img

Examples will run vmdebootstrap with sudo, you may be asked for
authentication.

Arguments other than those already included in the shortcut can also
be supplied, where required. e.g. --size, --variant, --package (can be
specified multiple times), --hostname, --sudo, --root-password or
--lock-root-password.

CubieTruck
----------

Currently untested and lacking u-boot support.

QEMU and EFI
------------

The bochs-drm kernel driver can be a problem when testing UEFI images,
even headless ones, causing systemd to halt before a login prompt is
offered.

vmdebootstrap includes a simple customisation script which blacklists
the bochs-drm module. Use, copy or extend this script for any image
which uses UEFI and which should be testable using QEMU.

To run UEFI with QEMU, the ovmf package needs to be installed from
non-free (due to patent issues with VFAT) and the -L option used to
QEMU to indicate the directory containing the EFI firmware to use.
For amd64, the firmware installed by ovmf can need to be renamed
(or symlinked) as /usr/share/ovmf/bios-256k.bin - then supply the
-L option to QEMU:

$ qemu-system-x86_64 -machine accel=kvm -m 4096 -smp 2 -drive format=raw,file=test.img -L /usr/share/ovmf/

debootstrap and task packages
-----------------------------

debootstrap is designed to be a minimalist tool and vmdebootstrap
wraps this support without substantial changes. Task packages are
the simplest way to extend a minimal bootstrap to a more general
purpose machine but there are limitations. debootstrap does not
handle Recommended packages, so installing a task package using
the --package support of vmdebootstrap (just as with the --include
support of debootstrap itself) may result in a system with fewer
packages installed than expected. Such systems can have the extra
packages identified after boot using graphical tools like aptitude
but to have all packages available during the creation of the image,
a customisation hook is required. The hook simply needs to install
the task package using apt instead of passing the task package to
--package. This allows apt to do all the normal Recommends calculations
and results in all of the extra packages being installed in one
operation. However, the apt source used for this will be the apt
source specified to vmdebootstrap for use after the system is booted,
so you may also want to extend the hook to temporarily reinstate a
local mirror (as used for the bootstrap phase) and put the other
mirror back at the end of the hook.

Examples of such hooks are available here:
http://anonscm.debian.org/cgit/debian-cd/pettersson-live.git/tree/vmdebootstrap

(These will need modification for other uses as the hooks expect
a particular filesystem layout only useful for debian-cd.)

