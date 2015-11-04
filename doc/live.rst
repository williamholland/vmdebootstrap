Initial schemes for vmdebootstrap creation of live images
=========================================================

#. vmdebootstrap has explicit support for foreign architecture
   bootstraps using qemu static binformat handling as well as
   support for Debian releases from wheezy onwards.

#. vmdebootstrap can support adding specific packages but a
   simpler approach is to use the existing task-* packages and
   only add packages manually where explicitly needed for a live
   image, e.g. ``wpa-supplicant``

#. Once a standard set of packages exist, create a metapackage
   expressing this support - possibly as a part of the vmdebootstrap
   packaging or as part of debian-cd.

#. debian-cd runs vmdebootstrap inside a VM in a similar manner to
   how debian-live currently operates, as both debian-live and
   vmdebootstrap need to call debootstrap which involves making
   device nodes and needs to run as root. This outer VM is specific
   for the release of Debian being built. vmdebootstrap can build
   older releases and it may be necessary to use a newer version of
   vmdebootstrap than is present in jessie to build jessie and to
   use that version to build wheezy.

#. vmdebootstrap uses a single config file per image type and each
   config file can have a single customisation script. The config
   file specifies the architecture of the image and the binformat
   handler for that architecture, so the customisation hook script
   can be architecture-specific.

#. Customisation hook scripts are shell scripts which will be passed
   a single parameter - the directory which represents the root
   directory of the final image. These scripts can use standard shell
   support to include other common functions or call out to utilities
   known to be installed in the outer VM running vmdebootstrap.

#. Customisation hooks clearly need to live in a VCS - possibly within
   the debian-cd git repo.

#. Although vmdebootstrap does have architecture support, the deciding
   factor is the availability of a working default kernel for the images
   built for that architecture and how to configure the bootloader(s) to
   provide the relevant dtb where needed.

#. Testing vmdebootstrap images uses qemu along the lines of::

    $ qemu-system-x86_64 -machine accel=kvm:tcg -m 4096 -smp 2 -drive file=test.img,format=raw

#. Unlike standard vmdebootstrap example scripts, the scripts calling
   vmdebootstrap itself do not need to use sudo as the call is made inside
   the outer VM which already has root. Using sudo will work but will output
   a message: sudo: unable to resolve host JESSIE-debian-live-builder

#. The building of live images doesn't appear to need changes in the
   vmdebootstrap package itself. The changes to isolinux to add the menu config,
   splash screen and to provide access to the install menus can all be done
   in the customisation hook.

#. Remember to use ``http://cdbuilder.debian.org/debian/`` for the bootstrap
   operations (--mirror option) and ``http://httpredir.debian.org/debian`` for
   the mirror to be used after the image has booted (--apt-mirror option).

#. Ensure that a user is created (``--user 'user/live'``) and that ``sudo`` is
   added to the set of packages to install and the --sudo option is passed
   to vmdebootstrap to ensure that the user is added to the sudo group. The
   root user password should also be locked (--lock-root-password).

#. Installing task packages using debootstrap **omits** ``Recommended`` packages,
   resulting in a much smaller image which is not expected for a live image.
   Task selection needs to be done in the customisation hook using the chroot
   command, at which point the default apt configuration will install the
   Recommends as well as the Depends packages. Ensure that the image size is
   big enough.

#. When installing using apt in the customisation script, ensure that the
   debconf non-interactive settings are exported to prevent the install
   waiting for keyboard interaction. ``DEBIAN_FRONTEND=noninteractive``

#. The customisation script needs to mount proc before starting the apt install.

#. Calls to apt should also not output the progress bar but the actual package
   installation steps should be logged.

#. Move the image apt sources aside and set the cdimage apt source instead.
   Use ``http://cdbuilder.debian.org/debian/`` Then, at the end of the
   customisation hook, remove that source and replace the original.

#. ``mksquashfs`` can fail without indication of why and when it does, the image
   file can be 4Kb or so of junk. ``vmdebootstrap`` will fail if the
   squashfs output is less than 1MB. This can occur if the drive runs
   out of space but squashfs does not report an error.
