#!/usr/bin/env python3
"""
Compile + run a judge job inside a job directory. Used by BOTH the local
runner (host python3) and the Docker runner (python3 inside the container),
so judging behaviour is identical regardless of backend.

Reads  <jobdir>/job.json  and  <jobdir>/sol.{cpp,c}
Writes <jobdir>/result.json

job.json schema:
{
  "language": "cpp" | "c",
  "limits": { "memoryMb": 256, "timeMs": 3000, "compileMs": 15000 },
  "cases": [ { "argv": ["0"], "stdin": "..." }, ... ]
}
"""
import json
import os
import resource
import signal
import subprocess
import sys
import time

OUT_CAP = 256 * 1024  # cap captured stdout/stderr to 256 KB


def which(prog: str) -> bool:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        if p and os.access(os.path.join(p, prog), os.X_OK):
            return True
    return False


def main() -> None:
    job_dir = sys.argv[1]
    result_path = os.path.join(job_dir, "result.json")

    if not os.access(job_dir, os.W_OK):
        # surfaced via the runner's captured stderr (e.g. a Docker uid/mount mismatch)
        sys.stderr.write(f"judge_exec: job dir not writable by uid {os.getuid()}: {job_dir}\n")

    def dump(obj):
        with open(result_path, "w") as f:
            json.dump(obj, f)

    try:
        with open(os.path.join(job_dir, "job.json")) as f:
            job = json.load(f)
    except Exception as e:  # noqa
        dump({"compile": {"ok": False, "stderr": f"job.json error: {e}"}, "cases": []})
        return

    lang = job.get("language", "cpp")
    limits = job.get("limits", {})
    mem_mb = int(limits.get("memoryMb", 256))
    time_ms = int(limits.get("timeMs", 3000))
    compile_ms = int(limits.get("compileMs", 15000))
    cases = job.get("cases", [])

    ext = "cpp" if lang == "cpp" else "c"
    src = os.path.join(job_dir, f"sol.{ext}")
    binp = os.path.join(job_dir, "bin")

    if lang == "cpp":
        cc = "clang++" if which("clang++") else "g++"
        cmd = [cc, "-std=c++17", "-O0", "-w", "-pipe", "-I", job_dir, "-o", binp, src]
    else:
        cc = "clang" if which("clang") else "gcc"
        cmd = [cc, "-std=c11", "-O0", "-w", "-pipe", "-o", binp, src]

    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=compile_ms / 1000.0)
    except subprocess.TimeoutExpired:
        dump({"compile": {"ok": False, "stderr": "Compilation timed out."}, "cases": []})
        return
    except FileNotFoundError:
        dump({"compile": {"ok": False, "stderr": f"Compiler '{cc}' not found."}, "cases": []})
        return

    def sanitize(s: str) -> str:
        # hide the random temp job path from compiler diagnostics
        return (s or "").replace(job_dir + os.sep, "").replace(job_dir, "")[:OUT_CAP]

    if cp.returncode != 0:
        dump({"compile": {"ok": False, "stderr": sanitize(cp.stderr)}, "cases": []})
        return

    def preexec():
        # best-effort per-process limits (cgroups in Docker enforce harder)
        try:
            b = mem_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (b, b))
        except Exception:
            pass
        try:
            cpu = max(1, time_ms // 1000 + 1)
            resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
        except Exception:
            pass
        try:
            resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024, 16 * 1024 * 1024))
        except Exception:
            pass

    results = []
    for c in cases:
        argv = [binp] + [str(a) for a in c.get("argv", [])]
        stdin = c.get("stdin", "")
        t0 = time.time()
        timed_out = False
        sig = None
        try:
            p = subprocess.run(
                argv,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=time_ms / 1000.0 + 0.5,
                preexec_fn=preexec,
            )
            out, err, code = p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            out = e.stdout or ""
            err = e.stderr or ""
            if isinstance(out, bytes):
                out = out.decode("utf-8", "replace")
            if isinstance(err, bytes):
                err = err.decode("utf-8", "replace")
            code = None
            timed_out = True
        dur = int((time.time() - t0) * 1000)
        if code is not None and code < 0:
            sig = -code
            name = signal.Signals(sig).name if sig in signal.Signals.__members__.values() else str(sig)
            err = (err or "") + f"\n[process killed by signal {sig} ({name})]"
        results.append({
            "stdout": (out or "")[:OUT_CAP],
            "stderr": (err or "")[:OUT_CAP],
            "exitCode": code,
            "signal": sig,
            "timedOut": timed_out,
            "durationMs": dur,
        })

    dump({"compile": {"ok": True, "stderr": sanitize(cp.stderr)}, "cases": results})


if __name__ == "__main__":
    main()
