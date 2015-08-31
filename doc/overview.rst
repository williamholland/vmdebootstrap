VMDebootstrap
#############

Purpose
*******
vmdebootstrap is a helper to install basic Debian system into virtual
disk image. It wraps **debootstrap**. You need to run :file:`vmdebootstrap`
as root. If the ``--verbose`` option is not used, no output will be
sent to the command line. If the ``--log`` option is not used, no
output will be sent to any log files either.

To use the image, you probably want to create a virtual machine using
your preferred virtualization technology, such as file:`kvm` or
file:`qemu`. Configure the virtual machine to use the image you've
created. Then start the virtual machine and log into it via its console
to configure it. The image has an empty root password and will not have
networking configured by default. Set the root password before you
configure networking.

Networking
**********

The ``--enable-networking`` option uses the :file:`/etc/network/interfaces.d/`
source directory, with the default settings for ``lo`` and ``eth0``
being added to :file:`/etc/network/interfaces.d/setup`. Other networking
configuration can be specified using a customisation script.
Localhost settings would be::

 auto lo
 iface lo inet loopback

If ``--enable-dhcp`` is specified, these settings are also included
into :file:`/etc/network/interfaces.d/setup`::

 auto eth0
 iface eth0 inet dhcp

Bootloaders
***********

Unless the ``--no-extlinux`` or ``--grub`` options are specified, the
image will use ``extlinux`` as a boot loader. ``bootsize`` is not
recommended when using ``extlinux`` - use ``grub`` instead.

Versions of grub2 in wheezy
===========================

Grub2 in wheezy can fail to install in the VM, at which point 
:file:`vmdebootstrap` will fall back to ``extlinux``. It may still be
possible to complete the installation of ``grub2`` after booting the
VM as the problem may be related to the need to use loopback devices
during the ``grub-install`` operation. Details of the error will appear
in the vmdebootstrap log file, if enabled with the ``--log`` option.

.. note:: **grub-legacy** is not supported.

:file:`vmdebootstrap` also supports **EFI**.

Use ``--use-uefi`` to use ``grub-efi`` instead of ``grub-pc``. If the
default 5Mb is not enough space, use the ``--esp-size`` option to
specify a different size for the EFI partition. Registered firmware is
not supported as it would need to be done after boot. If the system you
are creating is for more than just a VM or live image, you will likely
need a larger ESP, up to 500Mb.

UBoot
=====

UBoot needs manual configuration via the customisation hook scripts,
typically support requires adding ``u-boot`` using ``--package`` and then
copying or manipulating the relevant ``u-boot`` files in the customisation
script. Examples are included for beaglebone-black.

Installation images and virtual machines
****************************************

:file:`vmdebootstrap`` is aimed principally at creating virtual machines,
not installers or prebuilt installation images. It is possible to create
prebuilt installation images for some devices but this depends on the
specific device. (A 'prebuilt installation image' is a single image file
which can be written to physical media in a single operation and which
allows the device to boot directly into a fully installed system - in
a similar way to how a virtual machine would behave.)

:file:`vmdebootstrap` assumes that all operations take place on a local
image file, not a physical block device / removable media.

:file:`vmdebootstrap` is intended to be used with tools like ``qemu`` on
the command line to launch a new virtual machine. Not all devices have
virtualisation support in hardware.

This has implications for file:`u-boot` support in some cases. If the
device can support reading the bootloader from a known partition, like
the beaglebone-black, then :file:`vmdebootstrap` can provide space for
the bootloader and the image will work as a prebuilt installation image.
If the device expects that the bootloader exists at a specific offset
and therefore requires that the bootloader is written as an image not
as a binary which can be copied into an existing partition,
:file:vmdebootstrap` is unable to include that bootloader image into
the virtual machine image.

The beagleboneblack.sh script in the examples/ directory provides a worked
example to create a prebuilt installation image. However, the beagleboneblack
itself does not support virtualisation in hardware, so is unable to launch
a virtual machine. Other devices, like the Cubietruck or Wandboard need
:file:`u-boot` at a predefined offset but can launch a virtual machine
using ``qemu``, so the cubietruck and wandboard6q scripts in the
examples/ directory relate to building images for virtual machines once
the device is already installed and booted into a suitable kernel.

It is possible to wrap :file:`vmdebootstrap` in such a way as to prepare
a physical block device with a bootloader image and then deploy the
bootstrap on top. However, this does require physical media to be
inserted and removed each time the wrapper is executed. To do this, use
the ``--tarball`` option instead of the ``--image`` option. Then setup
the physical media and bootloader image manually, as required for the
device, redefine the partitions to make space for the rootfs, create a
filesystem on the physical media and unpack the :file:`vmdebootstrap`
tarball onto that filesystem. Once you have working media, an image can be
created using dd to read back from the media to an image file, allowing
other media to be written with a single image file.

Example
*******

To create an image for the stable release of Debian::

 sudo vmdebootstrap --image test.img --size 1g \\
    --log test.log --log-level debug --verbose \\
    --mirror http://mirror.lan/debian/

To run the test image, make sure it is writeable. Use the ``--owner``
option to set mode 0644 for the specified user or use chmod manually::

 sudo chmod a+w ./test.img

Execute using qemu, e.g. on amd64 using qemu-system-x86_64::

 qemu-system-x86_64 -drive format=raw,file=./test.img

(This loads the image in a new window.) Note the use of ``-drive
file=<img>,format=raw`` which is needed for newer versions of QEMU.

There is EFI firmware available to use with QEMU when testing images built
using the UEFI support, but this software is in Debian non-free due to patent
concerns. If you choose to install ``ovmf`` to test UEFI builds, a
secondary change is also needed to symlink the provided ``OVMF.fd`` to
the file required by QEMU: ``bios-256k.bin`` and then tell QEMU about
the location of this file with the -L option::

 $ qemu-system-x86_64 -L /usr/share/ovmf/ -machine accel=kvm \\
  -m 4096 -smp 2 -drive format=raw,file=test.img

For further examples, including u-boot support for beaglebone-black,
see ``/usr/share/vmdebootstrap/examples``

Notes
*****

If you get problems with the bootstrap process, run a similar bootstrap
call directly and chroot into the directory to investigate the failure.
The actual debootstrap call is part of the vmdebootstrap logfile. The
debootstrap logfile, if any, will be copied into your current working
directory on error.

:file:`debootstrap` will download all the apt archive files into the apt cache and does not
remove them before starting the configuration of the packages. This can
mean that debootstrap can fail due to a lack of space on the device if
the VM size is small. vmdebootstrap cleans up the apt cache once debootstrap
has finished but this doesn't help if the package unpack or configuration
steps use up all of the space in the meantime. Avoid this problem by
specifying a larger size for the image.

.. note:: if you are also using a separate /boot partition in your options to 
   :file:`vmdebootstrap` it may well be the boot partition which needs
   to be enlarged rather than the entire image.

It is advisable to change the mirror in the example scripts to a mirror
closer to your location, particularly if you need to do repeated builds.
Use the --apt-mirror option to specify the apt mirror to be used inside
the image, after boot.

There are two types of examples for ARM devices available with
:file:`vmdebootstrap`: prebuilt installation images (like the beaglebone-black) and virtual
machine images (cubietruck and wandboard). ARM devices which do not
support hypervisor mode and which also rely on the bootloader being at
a specific offset instead of using a normal partition will
**not** be supportable by vmdebootstrap. Similarly, devices which support
hypervisor will only be supported using virtual machine images, unless
the bootloader can be executed from a normal partition.
