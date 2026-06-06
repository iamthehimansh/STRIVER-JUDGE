// Server-only. Prepares a job directory and runs it either inside a fresh
// Docker container (production sandbox: per-run, memory + time limited) or via
// host clang as a labelled fallback when Docker is unavailable.
import "server-only";
import { spawn } from "node:child_process";
import { mkdtemp, writeFile, mkdir, readFile, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import type { Language, RunLimits } from "../types";
import { BITS_SHIM } from "./harness";

export interface JobCase {
  argv: string[];
  stdin: string;
}

export interface RawCaseResult {
  stdout: string;
  stderr: string;
  exitCode: number | null;
  signal: number | null;
  timedOut: boolean;
  durationMs: number;
}

export interface JobResult {
  compile: { ok: boolean; stderr: string };
  cases: RawCaseResult[];
  backend: "docker" | "local";
}

const DOCKER_IMAGE = process.env.JUDGE_IMAGE || "striver-judge:latest";

let dockerAvailable: boolean | null = null;
let dockerCheckedAt = 0;
const DOCKER_TTL_MS = 30_000;

async function hasDocker(): Promise<boolean> {
  if (process.env.JUDGE_BACKEND === "local") return false;
  if (process.env.JUDGE_BACKEND === "docker") return true;
  // re-probe periodically so the daemon starting/stopping is picked up
  if (dockerAvailable !== null && Date.now() - dockerCheckedAt < DOCKER_TTL_MS) {
    return dockerAvailable;
  }
  dockerAvailable = await new Promise<boolean>((resolve) => {
    const p = spawn("docker", ["info", "--format", "{{.ServerVersion}}"], { stdio: "ignore" });
    p.on("error", () => resolve(false));
    p.on("close", (code) => resolve(code === 0));
  });
  dockerCheckedAt = Date.now();
  return dockerAvailable;
}

function runProc(
  cmd: string,
  args: string[],
  opts: { timeoutMs: number; cwd?: string }
): Promise<{ code: number | null; stdout: string; stderr: string; timedOut: boolean }> {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { cwd: opts.cwd });
    let stdout = "";
    let stderr = "";
    let timedOut = false;
    const cap = 1024 * 1024;
    child.stdout.on("data", (d) => { if (stdout.length < cap) stdout += d.toString(); });
    child.stderr.on("data", (d) => { if (stderr.length < cap) stderr += d.toString(); });
    const timer = setTimeout(() => {
      timedOut = true;
      try { child.kill("SIGKILL"); } catch {}
    }, opts.timeoutMs);
    child.on("error", (e) => {
      clearTimeout(timer);
      resolve({ code: -1, stdout, stderr: stderr + String(e), timedOut });
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      resolve({ code, stdout, stderr, timedOut });
    });
  });
}

export async function runJob(
  language: Language,
  source: string,
  cases: JobCase[],
  limits: RunLimits
): Promise<JobResult> {
  const dir = await mkdtemp(path.join(os.tmpdir(), "striver-judge-"));
  try {
    const ext = language === "cpp" ? "cpp" : "c";
    await writeFile(path.join(dir, `sol.${ext}`), source, "utf8");
    if (language === "cpp") {
      await mkdir(path.join(dir, "bits"), { recursive: true });
      await writeFile(path.join(dir, "bits", "stdc++.h"), BITS_SHIM, "utf8");
    }
    await writeFile(
      path.join(dir, "job.json"),
      JSON.stringify({ language, limits, cases }),
      "utf8"
    );

    const useDocker = await hasDocker();
    // generous overall wall budget: compile + all cases + slack
    const overall = limits.compileMs + cases.length * (limits.timeMs + 1500) + 5000;

    let backend: "docker" | "local";
    if (useDocker) {
      backend = "docker";
      // fail fast with a helpful message if the image hasn't been built
      const img = await runProc("docker", ["image", "inspect", DOCKER_IMAGE], { timeoutMs: 8000 });
      if (img.code !== 0) {
        return {
          backend,
          compile: {
            ok: false,
            stderr: `Docker image "${DOCKER_IMAGE}" not found. Build it with: npm run judge:build`,
          },
          cases: [],
        };
      }
      // run as the host uid so the process can write result.json into the
      // bind-mounted, host-owned job dir (overrides the image's USER judge)
      const uid = typeof process.getuid === "function" ? process.getuid() : undefined;
      const gid = typeof process.getgid === "function" ? process.getgid() : undefined;
      const mem = `${limits.memoryMb}m`;
      const args = [
        "run", "--rm",
        "--network", "none",
        "--memory", mem, "--memory-swap", mem,
        "--cpus", "1.0",
        "--pids-limit", "128",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        ...(uid !== undefined ? ["--user", `${uid}:${gid ?? uid}`] : []),
        "-v", `${dir}:/work`,
        "-w", "/work",
        DOCKER_IMAGE,
        "python3", "/opt/judge_exec.py", "/work",
      ];
      const r = await runProc("docker", args, { timeoutMs: overall });
      if (r.code !== 0 && !existsSync(path.join(dir, "result.json"))) {
        return {
          backend,
          compile: { ok: false, stderr: `Docker run failed: ${r.stderr || r.stdout}` },
          cases: [],
        };
      }
    } else {
      backend = "local";
      const script = path.join(process.cwd(), "scripts", "judge_exec.py");
      const r = await runProc("python3", [script, dir], { timeoutMs: overall });
      if (!existsSync(path.join(dir, "result.json"))) {
        return {
          backend,
          compile: { ok: false, stderr: `Local runner failed: ${r.stderr || r.stdout}` },
          cases: [],
        };
      }
    }

    let raw: { compile: { ok: boolean; stderr: string }; cases: RawCaseResult[] };
    try {
      raw = JSON.parse(await readFile(path.join(dir, "result.json"), "utf8"));
    } catch (e: any) {
      return {
        backend,
        compile: {
          ok: false,
          stderr: `Could not read judge result (the run may have been killed or timed out): ${
            e?.message || e
          }`,
        },
        cases: [],
      };
    }
    return { backend, compile: raw.compile, cases: raw.cases };
  } finally {
    rm(dir, { recursive: true, force: true }).catch(() => {});
  }
}

export async function activeBackend(): Promise<"docker" | "local"> {
  return (await hasDocker()) ? "docker" : "local";
}
