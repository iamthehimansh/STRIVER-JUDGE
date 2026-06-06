#!/usr/bin/env python3
"""
Pre-commit tool: split any test-case file in generated-tests/ over THRESHOLD_MB
into ~CHUNK_MB chunks at line boundaries so no single file exceeds GitHub's
100 MB per-file limit. Run this locally before committing/pushing; on a fresh
clone, `python3 scripts/restore_data.py` reassembles them.

Each chunk is named  <original>.part000  <original>.part001  ...
The original file is removed once chunks are written successfully.
Re-running is a no-op when the original is already absent.
"""
import os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "generated-tests")
THRESHOLD_BYTES = 40 * 1024 * 1024   # split anything larger than this
CHUNK_BYTES = 40 * 1024 * 1024       # target chunk size (line-aligned)


def split_one(path):
    size = os.path.getsize(path)
    if size <= THRESHOLD_BYTES:
        return 0
    parts_written = 0
    buf, buf_sz = [], 0
    with open(path, "rb") as src:
        idx = 0
        for line in src:
            if buf and buf_sz + len(line) > CHUNK_BYTES:
                with open(f"{path}.part{idx:03d}", "wb") as out:
                    out.writelines(buf)
                parts_written += 1
                idx += 1
                buf, buf_sz = [], 0
            buf.append(line)
            buf_sz += len(line)
        if buf:
            with open(f"{path}.part{idx:03d}", "wb") as out:
                out.writelines(buf)
            parts_written += 1
    os.remove(path)
    return parts_written


def main():
    files = sorted(glob.glob(os.path.join(DATA, "*.jsonl")))
    big = [(f, os.path.getsize(f)) for f in files if os.path.getsize(f) > THRESHOLD_BYTES]
    if not big:
        print("nothing to split")
        return
    print(f"splitting {len(big)} files (>{THRESHOLD_BYTES//1024//1024} MB) into <={CHUNK_BYTES//1024//1024} MB chunks ...")
    total_parts = 0
    for f, sz in big:
        n = split_one(f)
        total_parts += n
        print(f"  {os.path.basename(f):60s}  {sz//1024//1024:4d} MB -> {n} parts")
    print(f"done — {total_parts} chunks written")


if __name__ == "__main__":
    main()
