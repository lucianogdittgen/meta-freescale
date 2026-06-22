DESCRIPTION = "Add packages for opencv i.MX build"

COMPATIBLE_MACHINE = "(mx8-nxp-bsp|mx9-nxp-bsp)"

inherit packagegroup

OPENCV_PKGS = "\
    opencv-apps \
    opencv-samples \
    python3-opencv \
"
RDEPENDS:${PN} = "\
    ${OPENCV_PKGS} \
"
