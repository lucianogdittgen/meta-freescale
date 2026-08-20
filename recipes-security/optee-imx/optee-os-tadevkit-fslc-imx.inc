# Copied from meta-imx/meta-imx-bsp/recipes-security/optee/optee-os-tadevkit-imx.inc.
# See: https://github.com/nxp-imx/imx-manifest/blob/imx-linux-whinlatter/imx-6.18.2-1.0.0.xml#L39

require optee-os-common-fslc-imx.inc

SUMMARY = "OP-TEE Trusted OS TA devkit"
DESCRIPTION = "OP-TEE TA devkit for build TAs"
HOMEPAGE = "https://www.op-tee.org/"

# Mirrors NXP meta-imx optee-os-tadevkit-imx.inc: this imx-specific TA-devkit
# dependency is appended in the imx layer on top of the meta-arm-derived base
# (optee-os-fslc.inc) DEPENDS. The analyzer concatenates across the include chain
# and demands one global alphabetical order, but pycryptodome cannot join the
# base list without diverging from the BSP source and moving an imx-only dep into
# the meta-arm mirror; the additive += in the imx layer is the correct form.
# nooelint: oelint.vars.dependsordered
DEPENDS += "python3-pycryptodome-native"

do_install() {
    #install TA devkit
    install -d ${D}${includedir}/optee/export-user_ta/
    for f in ${B}/export-ta_${OPTEE_ARCH}/* ; do
        cp -aR $f ${D}${includedir}/optee/export-user_ta/
    done
}

do_deploy() {
    echo "Do not inherit do_deploy from optee-os."
}

# The TA devkit ships only its headers under ${includedir}/optee, packed
# explicitly. This deliberately replaces the "${nonarch_base_libdir}/firmware/"
# default from optee-os-fslc.inc (the devkit has no firmware payload). The
# include's FILES:${PN} overrides the bitbake.conf default with a hard "=", so
# a "?=" here would let that config default win instead; and the devkit content
# is not additive to the base package. Keep the full replacement.
# nooelint: oelint.var.filesoverride oelint.var.override
FILES:${PN} = "${includedir}/optee/"

# Build paths are currently embedded
INSANE_SKIP:${PN}-dev += "buildpaths"
