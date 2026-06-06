#!/usr/bin/env python3
"""
Server-side / post-clone tool: reassemble any split test-case files in
generated-tests/. For each <original>.part000 it finds, it concatenates every
matching <original>.part??? in lexical order into <original>, then removes the
parts. Idempotent — running again after restore does nothing.

Usage (after `git clone`):
    python3 scripts/restore_data.py
"""
import glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "generated-tests")


def restore_one(first_part):
    # first_part = ".../<original>.part000"
    base = first_part[: -len(".part000")]
    if os.path.exists(base):
        return None, "already restored"
    parts = sorted(glob.glob(base + ".part???"))
    if not parts:
        return None, "no parts found"
    tmp = base + ".tmp"
    total = 0
    with open(tmp, "wb") as out:
        for p in parts:
            with open(p, "rb") as src:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
                    total += len(chunk)
    os.replace(tmp, base)
    for p in parts:
        os.remove(p)
    return total, f"{len(parts)} parts"


def main():
    firsts = sorted(glob.glob(os.path.join(DATA, "*.part000")))
    if not firsts:
        print("nothing to restore")
        return
    restored = skipped = 0
    for fp in firsts:
        size, info = restore_one(fp)
        base = os.path.basename(fp[: -len(".part000")])
        if size is None:
            print(f"  skip  {base:60s}  ({info})")
            skipped += 1
        else:
            print(f"  ok    {base:60s}  {size//1024//1024:4d} MB ({info})")
            restored += 1
    print(f"\ndone — restored {restored}, skipped {skipped}")


if __name__ == "__main__":
    main()
