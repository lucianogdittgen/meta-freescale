#!/bin/sh
# Run oelint-adv over meta-freescale. Requires oelint-adv on PATH.
#
# The linter policy lives at the layer root in .oelint.cfg. If standalone
# linting needs layer-specific variable or override additions later, add them to
# oelint.constants.json at the layer root so oelint-adv auto-loads them.
set -eu

# Neutralise CDPATH so 'cd' below can't print or jump to an unexpected dir.
unset CDPATH

here=$(cd -- "$(dirname -- "$0")" && pwd)
layer=$(cd -- "$here/../.." && pwd)

# Run from the layer root so '.oelint.cfg' is picked up from the working
# directory.
cd -- "$layer"

files=$(find . \
    \( -name '*.bb' -o -name '*.bbappend' -o -name '*.bbclass' -o -name '*.inc' \) \
    | sort)

# Run serially: oelint-adv's parallel workers can race while loading layer
# constants, intermittently emitting false "unknown variable/override" findings.
# Serial execution is deterministic. Pass '--jobs N' to override.
# shellcheck disable=SC2086
exec oelint-adv --jobs 1 "$@" $files
