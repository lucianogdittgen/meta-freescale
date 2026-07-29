#!/usr/bin/env python3
# Split oelint-adv findings into the ones this layer owns and the ones it does
# not.
#
# meta-freescale carries a lot of metadata copied from other layers, in two
# shapes:
#
#   1. WHOLE-FILE MIRROR - the file opens with a 'Copied from <layer>/<path>'
#      comment, e.g. recipes-security/optee-imx/optee-os-fslc.inc. Nothing in it
#      is ours to change.
#
#   2. MARKED COPY BLOCK - a fork whose upstream half is fenced off:
#
#          ########## meta-openembedded copy ###########
#          ...upstream's lines...
#          ########## End of meta-openembedded copy ####
#          ########## i.MX overrides ##################
#          ...our lines...
#
#      Only the part outside the fence is ours. The literal word 'copy' is what
#      distinguishes a real fence from the decorative '#######' rules that
#      appear elsewhere in the layer.
#
# A finding inside either region is not actionable here: "fixing" it makes the
# file diverge from the layer it was copied from, and the fix belongs upstream.
# Keeping such findings out of the CI baseline matters because re-syncing a
# mirror from upstream otherwise shows up as a wall of new findings on a change
# that is correct by policy - and the only way out would be regenerating the
# whole baseline, which also silently accepts any real regression in the same
# change.
#
# Reads oelint-adv's native 'path:line:severity:rule:msg' output or a
# tab-separated scan, from a file or stdin. With --filter the surviving lines
# are echoed back unchanged, so it can sit in the middle of a pipeline.
#
# Usage:
#   run-oelint.sh --quiet --output /dev/stdout | oelint-mirror-scope.py --filter
#   oelint-mirror-scope.py --list <scan>
#   oelint-mirror-scope.py <scan>

from __future__ import annotations

import argparse
import os
import re
import sys

# '########## meta-openembedded copy ####' / '### OE-core copy ###'
_FENCE = re.compile(r"^#{3,}.*\bcopy\b.*$", re.IGNORECASE)
_FENCE_END = re.compile(r"^#{3,}.*\bend\s+of\b.*\bcopy\b.*$", re.IGNORECASE)
# '# Copied from meta-arm/recipes-security/optee/optee-os.inc.'
_MIRROR = re.compile(r"\bcopied\s+from\b\s*(\S+)?", re.IGNORECASE)

# A provenance note this far into the file still counts as a header.
_MIRROR_HEADER_LINES = 5

_SUFFIXES = (".bb", ".bbappend", ".inc", ".bbclass")


def find_layer_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, "conf", "layer.conf")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            sys.exit("error: no conf/layer.conf at or above %s" % start)
        d = parent


def scan_file(path):
    """Return (mirror_source or None, [(start_line, end_line), ...])."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return None, []

    for line in lines[:_MIRROR_HEADER_LINES]:
        if not line.lstrip().startswith("#"):
            continue
        m = _MIRROR.search(line)
        if m:
            return (m.group(1) or "upstream").rstrip("."), []

    blocks, open_at = [], None
    for n, line in enumerate(lines, 1):
        stripped = line.strip()
        if not _FENCE.match(stripped):
            continue
        if _FENCE_END.match(stripped):
            if open_at is not None:
                blocks.append((open_at, n))
                open_at = None
        elif open_at is None:
            open_at = n
    if open_at is not None:
        # Unclosed fence: assume it runs to end of file rather than silently
        # treating the remainder as ours.
        blocks.append((open_at, len(lines)))
    return None, blocks


def build_index(layer):
    index = {}
    for root, dirs, files in os.walk(layer):
        dirs[:] = [d for d in dirs if d not in (".git", "build", "tmp")]
        for name in files:
            if not name.endswith(_SUFFIXES):
                continue
            full = os.path.join(root, name)
            mirror, blocks = scan_file(full)
            if mirror or blocks:
                index[os.path.relpath(full, layer)] = (mirror, blocks)
    return index


def parse_line(raw, layer):
    """Return (relpath, line_no, rule) or None if this is not a finding."""
    text = raw.rstrip("\n")
    if not text or text.startswith("#!"):
        return None
    fields = text.split("\t") if "\t" in text else text.split(":")
    if len(fields) < 4 or not fields[3].startswith("oelint."):
        return None
    path = fields[0]
    if os.path.isabs(path):
        try:
            path = os.path.relpath(path, layer)
        except ValueError:
            pass
    path = path[2:] if path.startswith("./") else path
    try:
        return path, int(fields[1]), fields[3]
    except ValueError:
        return None


def classify(rel, line, index):
    entry = index.get(rel)
    if not entry:
        return "layer", ""
    mirror, blocks = entry
    if mirror:
        return "mirror", mirror
    for start, end in blocks:
        if start <= line <= end:
            return "copy-block", "lines %d-%d" % (start, end)
    return "layer", ""


def main():
    ap = argparse.ArgumentParser(
        description="Separate layer-owned oelint findings from copied content.")
    ap.add_argument("scan", nargs="?", default="-",
                    help="scan file, or '-' for stdin (default)")
    ap.add_argument("--layer", default=".", help="layer root (default: search upwards)")
    ap.add_argument("--list", action="store_true", help="print every non-layer finding")
    ap.add_argument("--filter", action="store_true",
                    help="echo only layer-owned findings, unchanged")
    ap.add_argument("--exclude-rule", action="append", default=["homepageping"],
                    help="drop findings whose rule id contains this (repeatable)")
    args = ap.parse_args()

    layer = find_layer_root(args.layer)
    index = build_index(layer)

    src = sys.stdin if args.scan == "-" else open(args.scan, encoding="utf-8",
                                                  errors="replace")
    counts = {"layer": 0, "copy-block": 0, "mirror": 0}
    detail = []
    try:
        for raw in src:
            parsed = parse_line(raw, layer)
            if parsed is None:
                continue
            rel, line, rule = parsed
            if any(x in rule for x in args.exclude_rule):
                continue
            kind, note = classify(rel, line, index)
            counts[kind] += 1
            if kind == "layer":
                if args.filter:
                    sys.stdout.write(raw)
            else:
                detail.append((kind, rel, line, rule, note))
    finally:
        if src is not sys.stdin:
            src.close()

    if args.filter:
        return 0

    total = sum(counts.values())
    print("layer root: %s" % layer)
    print("files with copied content: %d\n" % len(index))
    print("  %5d  layer-owned        <- the actual backlog" % counts["layer"])
    print("  %5d  in a copy block    <- not ours, fix belongs upstream"
          % counts["copy-block"])
    print("  %5d  whole-file mirror  <- not ours, fix belongs upstream"
          % counts["mirror"])
    print("  %5d  total" % total)
    if total:
        share = (counts["copy-block"] + counts["mirror"]) * 100.0 / total
        print("\n  %.0f%% of findings are in content copied from another layer."
              % share)

    if args.list and detail:
        print("\n--- not ours ---")
        for kind, rel, line, rule, note in sorted(detail):
            print("  %-11s %s:%d  %s%s"
                  % (kind, rel, line, rule, "  [%s]" % note if note else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
