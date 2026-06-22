# Copyright (C) 2012-2016 Freescale Semiconductor
# Released under the MIT license (see COPYING.MIT for the terms)

DESCRIPTION = "Package group used by FSL Community to provide a set of benchmark applications."
SUMMARY = "FSL Communtiy package group - tools/benchmark"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

RDEPENDS:${PN} = ""
