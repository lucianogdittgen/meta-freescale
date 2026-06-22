# 6 and 7 Vivante do not provide virtual/libgbm required for any drm* flavour
PACKAGECONFIG:remove:imxgpu:mx6-nxp-bsp = "drm-gl drm-gles2"
PACKAGECONFIG:remove:imxgpu:mx7-nxp-bsp = "drm-gl drm-gles2"
