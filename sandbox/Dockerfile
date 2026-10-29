# Image for every student code run. It is started with no network, a
# read-only filesystem, no capabilities and CPU/memory/process limits
# (see smoke-test.sh for the exact flags the runner will use).
FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc libc6-dev clang libclang-rt-18-dev cppcheck valgrind \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin sandbox
USER sandbox
WORKDIR /tmp
