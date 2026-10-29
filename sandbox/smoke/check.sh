#!/bin/sh
# Runs inside the sandbox container. Proves that:
#   1. the container is locked down (not root, read-only, no network)
#   2. ASan catches the overflow in overflow.c with the triggering input
#   3. overflow_fixed.c passes ASan/UBSan, Cppcheck and Valgrind
set -eu

SRC=/smoke
WORK=$(mktemp -d)
TRIGGER=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA # 40 bytes into a 16-byte buffer
SAFE=Ada
# LeakSanitizer needs ptrace, which the sandbox blocks. Valgrind covers leaks.
export ASAN_OPTIONS=detect_leaks=0:abort_on_error=0
failures=0

pass() { echo "PASS  $1"; }
fail() { echo "FAIL  $1"; failures=$((failures + 1)); }

echo "== Lockdown"
[ "$(id -u)" -ne 0 ] && pass "not running as root (uid $(id -u))" || fail "running as root"
if touch /probe 2>/dev/null; then fail "root filesystem is writable"; else pass "root filesystem is read-only"; fi
interfaces=$(ls /sys/class/net)
[ "$interfaces" = "lo" ] && pass "no network (interfaces: $interfaces)" || fail "network interfaces: $interfaces"

echo "== Vulnerable program"
clang -g -O0 -fsanitize=address,undefined -fno-omit-frame-pointer \
    "$SRC/overflow.c" -o "$WORK/vuln"
"$WORK/vuln" "$SAFE" >/dev/null 2>&1 && pass "runs cleanly with safe input" || fail "fails with safe input"
if "$WORK/vuln" "$TRIGGER" >/dev/null 2>"$WORK/vuln.err"; then
    fail "ASan did not stop the overflow"
elif grep -q "AddressSanitizer: stack-buffer-overflow" "$WORK/vuln.err"; then
    pass "ASan reports stack-buffer-overflow with triggering input"
else
    fail "crashed, but not with a stack-buffer-overflow report"
fi

echo "== Fixed program"
clang -g -O0 -fsanitize=address,undefined -fno-omit-frame-pointer \
    "$SRC/overflow_fixed.c" -o "$WORK/fixed_asan"
"$WORK/fixed_asan" "$TRIGGER" >/dev/null 2>"$WORK/fixed.err" \
    && pass "ASan/UBSan clean with triggering input" || { fail "ASan/UBSan errors"; cat "$WORK/fixed.err"; }

cppcheck --enable=warning,portability --error-exitcode=1 --quiet "$SRC/overflow_fixed.c" \
    && pass "Cppcheck clean" || fail "Cppcheck findings"

gcc -g -O0 "$SRC/overflow_fixed.c" -o "$WORK/fixed_plain"
valgrind -q --error-exitcode=1 --leak-check=full "$WORK/fixed_plain" "$TRIGGER" >/dev/null \
    && pass "Valgrind clean" || fail "Valgrind errors"

echo "== Time limit"
if timeout 2 sh -c 'while :; do :; done'; then fail "infinite loop was not stopped"; else pass "infinite loop stopped by timeout"; fi

echo
[ "$failures" -eq 0 ] && echo "Smoke test passed." || { echo "$failures check(s) failed."; exit 1; }
