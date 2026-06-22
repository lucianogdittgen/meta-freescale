FILESEXTRAPATHS:prepend:imxgpu := "${THISDIR}/${PN}:"

SRC_URI:append:imxgpu = " \
    file://Replace-glWindowPos2iARB-calls-with-glWindowPos2i.patch \
    file://fix-clear-build-break.patch \
    file://0001-egl-clear-backgrounds-black.patch \
    file://0001-YOCIMX-8300-Fix-mesa-demos-build-break-on-GCC-14.patch \
"

REQUIRED_DISTRO_FEATURES:remove:imxgpu = "x11"

PACKAGECONFIG:remove:imxgpu2d = "gles1 gles2"
PACKAGECONFIG:remove:imxgpu = "x11"

PACKAGECONFIG:append:imxgpu = " glu"

python () {
    if 'imxgpu' in (d.getVar('OVERRIDES') or '').split(':'):
        d.setVarFlag('PACKAGECONFIG', 'glu', ',,libglu')
}
