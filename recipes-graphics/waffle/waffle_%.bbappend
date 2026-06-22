FILESEXTRAPATHS:prepend:imxgpu := "${THISDIR}/${PN}:"

SRC_URI:append:imxgpu = " \
    file://0001-meson-Add-missing-wayland-dependency-on-EGL.patch \
    file://0002-meson-Separate-surfaceless-option-from-x11.patch \
"

PACKAGECONFIG_IMXGPU_X11:imxgpu3d = "x11-egl glx"
PACKAGECONFIG:imxgpu = " \
    ${@bb.utils.contains('DISTRO_FEATURES', 'wayland',                     'wayland', \
       bb.utils.contains('DISTRO_FEATURES',     'x11', '${PACKAGECONFIG_IMXGPU_X11}', \
                                                                                  '', d), d)} \
    gbm \
"
PACKAGECONFIG:remove:imxgpu:mx6-nxp-bsp = "gbm"
PACKAGECONFIG:remove:imxgpu:mx7-nxp-bsp = "gbm"
