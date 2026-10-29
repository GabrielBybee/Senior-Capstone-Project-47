# Sandbox

Locked-down image used for every code run: gcc/clang with ASan/UBSan, Cppcheck and Valgrind.

Containers from this image run as a non-root user with no network, a read-only
filesystem (only a small `/tmp` is writable), no Linux capabilities and limits on
CPU, memory, processes and time. The exact `docker run` flags are in
[`smoke-test.sh`](smoke-test.sh); the runner service will use the same ones.

## Smoke test

```bash
sandbox/smoke-test.sh
```

It builds the image and runs [`smoke/check.sh`](smoke/check.sh) inside it, which checks that:

- the container is locked down (not root, read-only, no network, timeouts work)
- ASan reports a `stack-buffer-overflow` in [`smoke/overflow.c`](smoke/overflow.c) with the triggering input
- the fixed version [`smoke/overflow_fixed.c`](smoke/overflow_fixed.c) is clean under ASan/UBSan, Cppcheck and Valgrind

This is the same check every generated exercise must pass before a student sees it:
the original must fail and the fix must pass.

Note: Cppcheck does not flag the `strcpy` bug in `overflow.c`. That's why grading uses
several tools instead of relying on one.
