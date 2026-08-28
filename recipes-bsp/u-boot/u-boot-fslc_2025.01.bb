require recipes-bsp/u-boot/u-boot.inc
require u-boot-fslc-common_${PV}.inc

DESCRIPTION = "U-Boot based on mainline U-Boot used by FSL Community BSP in \
               order to provide support for some backported features and fixes, or because it \
               was submitted for revision and it takes some time to become part of a stable \
               version, or because it is not applicable for upstreaming."
SECTION = "bootloaders"

# DEPENDS accumulates across the include chain: oe-core u-boot.inc contributes
# computed ${@...} fragments, the shared u-boot-fslc-common.inc appends
# bison-native flex-native for every fslc variant, and this recipe adds its own
# build tools. These additive += groups are the correct form for a shared /
# variant split, and no single alphabetical order spans them without merging the
# shared-common deps into each variant (which would defeat the shared include)
# or ordering the computed fragments (which have no alphabetical position).
# DEPENDS is a set, so the order does not affect the build.
# nooelint: oelint.vars.dependsordered
DEPENDS += "bc-native dtc-native python3-setuptools-native gnutls-native"

PROVIDES += "u-boot u-boot-mfgtool"

# FIXME: Allow linking of 'tools' binaries with native libraries
#        used for generating the boot logo and other tools used
#        during the build process.
EXTRA_OEMAKE += 'HOSTCC="${BUILD_CC} ${BUILD_CPPFLAGS}" \
                HOSTLDFLAGS="${BUILD_LDFLAGS}" \
                HOSTSTRIP=true'

inherit ${@oe.utils.ifelse(d.getVar('UBOOT_PROVIDES_BOOT_CONTAINER') == '1', 'imx-boot-container', '')}
inherit uuu_bootloader_tag

PACKAGE_ARCH = "${MACHINE_ARCH}"
COMPATIBLE_MACHINE = "(imx-generic-bsp)"
