FILESEXTRAPATHS:prepend:imxgpu := "${THISDIR}/${PN}:"

SRC_URI:append:imxgpu = " \
    file://0001-tests-Fix-cl-test-Include-Directories-error-Error-0-.patch \
    file://0002-cl-Add-mutually-exclusive-memory-flags-for-CL_MEM_KE.patch"

PACKAGECONFIG:append:imxgpu = " gbm opencl ${@bb.utils.filter('DISTRO_FEATURES', 'vulkan', d)}"
PACKAGECONFIG:remove:imxgpu = "glx"
PACKAGECONFIG:remove:imxgpu:mx6-nxp-bsp = "glx x11 gbm opencl vulkan"
PACKAGECONFIG:remove:imxgpu:mx7-nxp-bsp = "glx x11 gbm opencl vulkan"

python () {
    if 'imxgpu' in (d.getVar('OVERRIDES') or '').split(':'):
        d.setVarFlag('PACKAGECONFIG', 'gbm', '-DPIGLIT_USE_GBM=1,-DPIGLIT_USE_GBM=0,virtual/libgbm')
}

CFLAGS:append:imxgpu:toolchain-clang = " -Wno-error=int-conversion"
