# Item 18 (50-things list): "never write your own primitive" -- integrate PQ signatures/KEM
# through maintained implementations, check their status first. [M]
#
# Libraries used (all optional deps, see requirements-dev.txt; this check SKIPS, not fails, if
# absent from the running interpreter):
#   mlkem     (PyPI, Rust-backed) -- ML-KEM / FIPS 203. Status checked 2026-11-09: actively
#             maintained, implements all three parameter sets.
#   mldsa     (PyPI, pure Python, author: Filippo Valsorda) -- ML-DSA / FIPS 204, VERIFY-ONLY.
#             This is deliberately the one this project would actually want on-device: D-12
#             commits to "verify-only ML-DSA" and this library's own scope matches that exactly
#             rather than needing us to strip a signing-capable library down ourselves.
#   dilithium-py (PyPI, pure Python, author: Giacomo Pope) -- full ML-DSA incl. signing. Used here
#             ONLY as an independent test-harness signer, to produce signatures for mldsa to
#             verify -- i.e. two DIFFERENT authors' implementations cross-checked against each
#             other, not one library self-testing its own output.
#   slhdsa    (PyPI, pure Python) -- SLH-DSA / FIPS 205, both sign and verify. Single
#             implementation (no second independent SLH-DSA library was integrated in this pass);
#             tested by self-consistency (sign -> verify -> True) and fail-closed on tampering,
#             not by cross-implementation agreement the way ML-DSA is below.
#
# Explicitly NOT done here: this project's locked-stage code does not call into any of these
# libraries (none are C, none are suitable for a Cortex-M0+ locked stage) -- this is host-side
# conformance evidence that the ALGORITHMS behave as FIPS 203/204/205 describe, using real
# maintained implementations, not a claim that the device firmware now uses them. The actual
# target-firmware providers (mlkem-native, mldsa-native per ADR on D-12) remain uninstalled and
# unintegrated; this only discharges "check library status, verify against real implementations",
# not "ship it on the device".
import sys

def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    try:
        import mlkem
    except ImportError:
        print("mlkem not installed -- SKIPPED (pip install mlkem; see requirements-dev.txt)")
        return 0

    for ps, name, expected_ct in [
        (mlkem.ParameterSet.ML_KEM_512, "ML-KEM-512", 768),
        (mlkem.ParameterSet.ML_KEM_768, "ML-KEM-768", 1088),
        (mlkem.ParameterSet.ML_KEM_1024, "ML-KEM-1024", 1568),
    ]:
        k = mlkem.ML_KEM(ps)
        ek, dk = k.key_gen()
        ss1, ct = k.encaps(ek)
        ss2 = k.decaps(dk, ct)
        check(f"{name}: shared secret matches after encaps/decaps round trip", ss1 == ss2)
        check(f"{name}: ciphertext length matches FIPS 203 ({expected_ct} B)", len(ct) == expected_ct)
    # resource-estimates.md independently claims ML-KEM-768 enrolment ciphertext = 1,088 B [F] --
    # cross-check that documented figure against this real library's actual output.
    k768 = mlkem.ML_KEM(mlkem.ParameterSet.ML_KEM_768)
    ek, dk = k768.key_gen()
    _, ct = k768.encaps(ek)
    check("ML-KEM-768 ciphertext matches resource-estimates.md's documented 1,088 B", len(ct) == 1088)

    try:
        import mldsa
        from dilithium_py.ml_dsa import ML_DSA_65
    except ImportError:
        print("mldsa and/or dilithium-py not installed -- ML-DSA cross-check SKIPPED")
        print(f"pqc_conformance (ML-KEM only) failures={failures}")
        return failures

    pk, sk = ML_DSA_65.keygen()
    msg = b"KRYPTARA conformance test message"
    sig = ML_DSA_65.sign(sk, msg)
    check("dilithium-py's own signature self-verifies", ML_DSA_65.verify(pk, msg, sig))
    vk = mldsa.VerificationKey(pk, parameters=mldsa.ParameterSet.ML_DSA_65)
    try:
        vk.verify(sig, msg)
        cross_ok = True
    except Exception:
        cross_ok = False
    check("INDEPENDENT verify-only library (mldsa) accepts dilithium-py's signature", cross_ok)
    tampered = b"KRYPTARA conformance test messagE"
    try:
        vk.verify(sig, tampered)
        tamper_rejected = False
    except mldsa.VerificationError:
        tamper_rejected = True
    except Exception:
        tamper_rejected = False
    check("mldsa correctly REJECTS a signature over a tampered message", tamper_rejected)
    check("ML-DSA-65 public key length matches FIPS 204 (1,952 B)", len(pk) == 1952)

    try:
        import slhdsa
    except ImportError:
        print("slhdsa not installed -- SLH-DSA check SKIPPED")
        print(f"pqc_conformance failures={failures}")
        return failures

    kp = slhdsa.KeyPair.gen(slhdsa.sha2_128s)
    msg2 = b"KRYPTARA SLH-DSA conformance test"
    sig2 = kp.sign_pure(msg2)
    check("SLH-DSA-SHA2-128s sign then verify (self-consistency, single implementation)",
          kp.verify_pure(msg2, sig2))
    check("SLH-DSA signature length matches FIPS 205 SHA2-128s (7,856 B)", len(sig2) == 7856)
    check("SLH-DSA fails closed on a tampered message", not kp.verify_pure(msg2 + b"x", sig2))

    print(f"pqc_conformance failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        sys.exit(1)
