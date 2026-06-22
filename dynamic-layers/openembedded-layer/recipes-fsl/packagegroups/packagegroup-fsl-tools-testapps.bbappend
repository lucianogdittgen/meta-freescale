RDEPENDS:${PN}:append = " evtest memtester ${@bb.utils.contains('DISTRO_FEATURES', 'x11', 'v4l-utils', '', d)}"
