#!/usr/bin/env bash
# Builds the sandbox image and runs smoke/check.sh inside it with the same
# lockdown flags the runner will use for student code.
# Usage: sandbox/smoke-test.sh   (from anywhere; needs Docker)
set -euo pipefail

cd "$(dirname "$0")"
IMAGE=${SANDBOX_IMAGE:-securecode-sandbox:dev}

if [ "${SKIP_BUILD:-0}" != 1 ]; then
    docker build -t "$IMAGE" .
fi

docker run --rm \
    --network none \
    --read-only \
    --tmpfs /tmp:rw,exec,nosuid,size=64m \
    --cap-drop ALL \
    --security-opt no-new-privileges \
    --pids-limit 64 \
    --memory 512m --memory-swap 512m \
    --cpus 1 \
    --user 10001:10001 \
    --volume "$PWD/smoke:/smoke:ro" \
    "$IMAGE" \
    timeout 60 sh /smoke/check.sh
