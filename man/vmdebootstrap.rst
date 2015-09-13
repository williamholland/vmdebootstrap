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

Synopsis
********

::

 $ sudo vmdebootstrap --image=FILE --size=SIZE [--mirror=URL] [--distribution=NAME]

Options
*******

 --output=FILE         write output to FILE, instead of standard output
 --verbose             report what is going on
 --image=FILE          put created disk image in FILE
 --size=SIZE           create a disk image of size SIZE (1000000000)
 --tarball=FILE        tar up the disk's contents in FILE
 --mirror=URL          use MIRROR as package source (http://http.debian.net/debian/)
 --arch=ARCH           architecture to use (amd64) - if using an 
                       architecture which the host system cannot execute,
                       ensure the --foreign option is also used.
 --distribution=NAME   release to use (defaults to stable). The release
                       needs to be a valid Debian or Ubuntu release name
                       or codename.
 --debootstrapopts="command=option,command=option"
                       Supply options and arguments to ``debootstrap``,
                       separated by spaces.
                       e.g. --debootstrapopts="variant=buildd no-check-gpg components=main,contrib".
                       See **debootstrap (1)** for more information. This
                       option replaces the ``--variant`` support in
                       previous versions.
 --package=PACKAGE     install PACKAGE onto system
 --custom-package=DEB  install package in DEB file onto system (not
                       from mirror)
 --no-kernel           do not install a linux package
 --kernel-package      If --no-kernel is not used and the auto-selection
                       of the **linux-image-586** or **linux-image-armmp**
                       or **linux-image-$ARCH** package is not suitable,
                       the kernel package can be specified explicitly.
 --enable-dhcp         enable DHCP on eth0
 --root-password=PASSWORD
                       set root password
 --customize=SCRIPT    run SCRIPT after setting up system. If the script
                       does not exist in the current working directory, 
                       :file:`usr/share/vmdebootstrap/examples/` will be
                       checked as a fallback. The script needs to be
                       executable and is passed the root directory of the
                       debootstrap as the only argument. Use chroot if
                       you need to execute binaries within the
                       debootstrap.
 --hostname=HOSTNAME   set name to HOSTNAME (debian)
 --user=USERSTRING     create USER with PASSWORD. The USERSTRING needs to
                       be of the format: USER/PASSSWORD.
 --owner=OWNER         change the owner of the final image from root to
                       the specified user.
 --serial-console      configure image to use a serial console
 --serial-console-command
                       set the command to manage the serial console which
                       will be appended to :file:`/etc/inittab`. Default
                       is ``/sbin/getty \-L ttyS0 115200 vt100``, resulting
                       in a line::

                        "S0:23:respawn:/sbin/getty \-L ttyS0 115200 vt100"

 --sudo                install sudo, and if user is created, add them to
                       sudo group
 --bootsize=BOOTSIZE   If specified, create a /boot partition of the given
                       size within the image. Debootstrapping will fail
                       if this is too small for the selected kernel
                       package and upgrading such a kernel package is
                       likely to need two or three times the space of the
                       installed kernel.
 --boottype=FSTYPE     Filesystem to use for the /boot partition. (default ext2)
 --roottype=FSTYPE     Filesystem to use for the / (root) partition. (default ext4)
 --swap=SWAPSIZE       If specified, create a swap partition of the given
                       size within the image. Debootstrapping will fail
                       if this results in a root partition which is too
                       small for the selected packages. The minimum swap
                       space is 256Mb as the default memory allocation
                       of QEMU is 128Mb. A default 1Gb image is not likely
                       to have enough space for a swap partition as well.
 --foreign=PATH        Path to the binfmt_handler to enable foreign support
                       in debootstrap. e.g. :file:`/usr/bin/qemu-arm-static`
                       Note: foreign debootstraps may take a signficant
                       amount of time to complete and that debootstrap will
                       retry five times if packages fail to install by default.
 --no-extlinux         Skip installation of extlinux. needs a customize script
                       or alternative bootloader to make the image bootable.
                       Useful for architectures where extlinux is not supportable.
                       Depending on how the image is to be booted, the --mbr
                       option may also be necessary with extlinux.
 --squash              Run mksquashfs against the final image using xz
                       compression - requires ``squashfs-tools`` to be installed.
                       The final file will have the ``.squashfs`` suffix.
                       By default, mksquashfs is allowed to use all processors
                       which may result in high load. Run ``mksquashfs``
                       separately if you need to control the number of
                       processors used per run. squashfs can also have issues
                       with large image files (where large is a factor of the
                       amount of data inside the image rather than the size
                       of the image itself). These errors can result in invalid
                       images (e.g. image does not boot) or corrupted images
                       (truncated file). This is a known bug in squashfs.
                       Avoid using the --squash option and consider squashing
                       the loopback mounted directory tree of the image.
                       ``vmdebootstrap`` will check if the squashed filesystem
                       is less than 1MB and leave the unsquashed image in
                       place with a warning about a possible squashfs failure.
 --configure-apt       Use the specified mirror and distribution to create a
                       suitable apt source inside the VM. Can be useful if
                       debootstrap fails to create it automatically.
 --apt-mirror          Use the specified mirror inside the image instead of the
                       mirror used to build the image. This is useful if you have
                       a local mirror to make building the image quicker but
                       the image needs to run even if that mirror is not available.
 --grub                Disable extlinux installation and configure grub2 instead.
                       grub2 will be added to the list of packages to install.
                       update-grub will be called once the debootstrap is
                       complete and grub-install will be called in the image.
 --no-acpid            Disable installation of acpid if not required, otherwise
                       acpid will be installed if --foreign is not used.
 --pkglist             Output a list of package names installed inside the image.
                       Useful if you need to track the relevant source packages
                       used inside the image for licence compliance.

Configuration files and settings
********************************

 --dump-config         write out the entire current configuration
 --no-default-configs  clear list of configuration files to read
 --config=FILE         add FILE to config files

Logging
*******

 --log=FILE            write log entries to FILE (default is to not write
                       log files at all); use "syslog" to log to system
                       log, or "none" to disable logging.
 --log-level=LEVEL     log at LEVEL, one of debug, info, warning, error,
                       critical, fatal (default: debug).
 --log-max=SIZE        rotate logs larger than SIZE, zero for never (default: 0)
 --log-keep=N          keep last N logs (10)
 --log-mode=MODE       set permissions of new log files to MODE (octal;  default 0600)

Peformance
**********

 --dump-memory-profile=METHOD
                       make memory profiling dumps using METHOD, which is one
                       of: none, simple, meliae, or heapy (default: simple)
 --memory-dump-interval=SECONDS
                       make memory profiling dumps at least SECONDS apart

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

.. caution:: if you are also using a separate /boot partition in your options to 
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
