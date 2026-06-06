# ─── Striver Judge — Next.js app image ──────────────────────────────────────
# Multi-stage build of the workspace itself. The actual code-execution sandbox
# is a SEPARATE image (judge/Dockerfile -> striver-judge:latest); this app
# image just ships the UI + judge API and shells out to `docker run …` to
# create per-submission sandbox containers (so Docker CLI is included here).

# ---------- deps ----------
FROM node:20-bookworm-slim AS deps
WORKDIR /app
# build tools for better-sqlite3 (falls back to building from source if no
# matching prebuilt binary is found for the host arch)
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 make g++ ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund

# ---------- build ----------
FROM node:20-bookworm-slim AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# self-host Monaco; build Next
RUN node scripts/copy_monaco.js && npm run build

# ---------- runtime ----------
FROM node:20-bookworm-slim AS run
WORKDIR /app

# Docker CLI talks to the host's daemon via the mounted /var/run/docker.sock.
# python3 is used by the judge_exec helper if it ever needs to run inside the
# app image (it normally runs inside the sandbox).
RUN apt-get update && apt-get install -y --no-install-recommends \
      docker.io ca-certificates python3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/scripts ./scripts
COPY --from=build /app/lib ./lib
COPY --from=build /app/app ./app
COPY --from=build /app/components ./components
COPY --from=build /app/next.config.mjs ./

ENV NODE_ENV=production \
    JUDGE_BACKEND=docker \
    JUDGE_IMAGE=striver-judge:latest \
    JUDGE_MEMORY_MB=256 \
    JUDGE_TIME_MS=3000 \
    JUDGE_COMPILE_MS=15000

EXPOSE 3000
CMD ["npm", "start"]
