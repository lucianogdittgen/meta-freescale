SUMMARY = "DPAA2 Resource Manager Tool"
DESCRIPTION = "Userspace resource manager tool for DPAA2 objects on NXP QorIQ SoCs."
HOMEPAGE = "https://github.com/nxp-qoriq/restool"
SECTION = "base"
LICENSE = "BSD-3-Clause OR GPL-2.0-or-later"
LIC_FILES_CHKSUM = "file://LICENSE;md5=83af78c71766dd5fb1c1c3dd64a75ee7"

SRC_URI = "git://github.com/nxp-qoriq/restool;protocol=https;nobranch=1"
SRCREV = "df31aaa46b77e3918f893ca08b1e63871ae880b6"

inherit bash-completion

EXTRA_OEMAKE = 'CC="${CC}" MANPAGE= EXTRA_CFLAGS="-O2 -Wno-missing-field-initializers -Wno-missing-braces -Wno-maybe-uninitialized -Wno-date-time"'

do_install () {
    oe_runmake install DESTDIR=${D}
}

COMPATIBLE_MACHINE = "(qoriq-arm64)"
PACKAGE_ARCH = "${MACHINE_ARCH}"

RDEPENDS:${PN} += "bash dtc"
# ${PN}-bash-completion is added to PACKAGES by the bash-completion bbclass,
# which oelint cannot resolve statically.
# nooelint: oelint.vars.specific
RDEPENDS:${PN}-bash-completion += "bash"

