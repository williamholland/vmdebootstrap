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

sudo ./beagleboneblack.sh --image bbb.img

Arguments other than those already included in the shortcut can also
be supplied, where required. e.g. --size, --variant, --package (can be
specified multiple times), --hostname, --sudo, --root-password or
--lock-root-password.

CubieTruck
----------
