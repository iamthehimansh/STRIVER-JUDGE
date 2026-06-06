# Sandbox image for the per-run judge container.
# Build from the project root:  docker build -t striver-judge:latest -f judge/Dockerfile .
FROM debian:bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      clang g++ python3 ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY scripts/judge_exec.py /opt/judge_exec.py

# Run as an unprivileged user; the host mounts a per-run job dir at /work.
RUN useradd -m -u 1000 judge
USER judge
WORKDIR /work

ENTRYPOINT []
CMD ["python3", "/opt/judge_exec.py", "/work"]
