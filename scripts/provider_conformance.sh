#!/usr/bin/env bash
# Item 17 (50-things list): crypto provider conformance suite. [M]
# "Two independent providers pass the same suite": this repo's own portable sha256.c
# (src/prototypes/c/sha256.c) against OpenSSL's libcrypto (widely audited, can use hardware
# SHA extensions when present -- the closest thing to "a hardware-accelerated provider" available
# without actual target silicon) and Python's hashlib (a third, independent implementation).
# Includes the official FIPS 180-4 test vectors, not just random input, so this is checked against
# the published standard, not just internal self-consistency.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
BUILD="$ROOT/build"; mkdir -p "$BUILD"
gcc -O2 -o "$BUILD/sha256_hexdump" tests/sha256_hexdump.c

bad=0
check() {
    local label="$1" input="$2" expected="$3"
    local ours; ours=$(printf '%s' "$input" | "$BUILD/sha256_hexdump")
    local ossl; ossl=$(printf '%s' "$input" | openssl dgst -sha256 -r | awk '{print $1}')
    local py; py=$(printf '%s' "$input" | python3 -c "import sys,hashlib; sys.stdout.write(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())")
    local ok=1
    [ -n "$expected" ] && [ "$ours" != "$expected" ] && ok=0
    [ "$ours" != "$ossl" ] && ok=0
    [ "$ours" != "$py" ] && ok=0
    if [ "$ok" = "1" ]; then
        echo "  $label: MATCH (ours=openssl=python${expected:+=FIPS-vector})"
    else
        echo "  $label: MISMATCH ours=$ours openssl=$ossl python=$py expected=${expected:-n/a}"
        bad=1
    fi
}

# FIPS 180-4 official test vectors (empty string and "abc")
printf '' | "$BUILD/sha256_hexdump" | grep -q 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' \
    && echo "  FIPS vector (empty string): MATCH" \
    || { echo "  FIPS vector (empty string): FAIL"; bad=1; }
printf 'abc' | "$BUILD/sha256_hexdump" | grep -q 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad' \
    && echo "  FIPS vector (\"abc\"): MATCH" \
    || { echo "  FIPS vector (\"abc\"): FAIL"; bad=1; }

check "empty string, three-way" "" ""
check "short ascii" "KRYPTARA" ""
check "binary-ish with repeats" "$(printf 'A%.0s' {1..1000})" ""
check "exactly one block (64 bytes)" "$(printf 'B%.0s' {1..64})" ""
check "block boundary + 1 (65 bytes)" "$(printf 'C%.0s' {1..65})" ""

echo "provider_conformance: $([ $bad -eq 0 ] && echo PASSED || echo FAILED)"
exit $bad
