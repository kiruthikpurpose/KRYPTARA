# REQ-STALE-01 (ADR-010, D-30): "Chains MUST end at a fresh witnessed checkpoint; authority catch-up
# older than window W MUST require presence when an RTC is trusted." [C]
# This is a pure decision function, not a full chain-verifier; it formalises the one rule ADR-010
# states, not the whole witnessed-receipt / chain-of-custody machinery (which is Phase 1, not built
# yet -- see docs/implementation/roadmap.md). "Fresh" = chain_tip ends in a checkpoint carrying a
# witness receipt (the WIT atom, ADR-006); staleness is only measurable at all when an RTC is
# trusted, since a device with no trusted clock cannot know how old its last checkpoint is.

def catchup_authorised(ends_at_witnessed_checkpoint, age_since_checkpoint, window_w, rtc_trusted, presence):
    """Returns True iff authority catch-up may proceed under REQ-STALE-01."""
    if not ends_at_witnessed_checkpoint:
        return False                      # "chains MUST end at a fresh witnessed checkpoint"
    if rtc_trusted and age_since_checkpoint > window_w:
        return presence                   # stale AND measurably so: presence required, no exception
    return True                           # not measurably stale (or within window): no extra bar

if __name__ == "__main__":
    cases = [
        # (ends_witnessed, age, W, rtc_trusted, presence) -> expected
        (True,  5,  10, True,  False, True),   # fresh enough, no presence needed
        (True,  15, 10, True,  False, False),  # stale, RTC trusted, no presence -> refused
        (True,  15, 10, True,  True,  True),   # stale, RTC trusted, presence given -> ok
        (True,  15, 10, False, False, True),   # stale but RTC not trusted: staleness unmeasurable, not blocked by this rule
        (False, 0,  10, True,  True,  False),  # chain doesn't even end at a witnessed checkpoint -> always refused
    ]
    failures = 0
    for ends, age, w, rtc, pres, expect in cases:
        got = catchup_authorised(ends, age, w, rtc, pres)
        ok = got == expect
        failures += (not ok)
        print(f"  ends_witnessed={ends!s:5s} age={age:3d} W={w:3d} rtc_trusted={rtc!s:5s} presence={pres!s:5s} "
              f"-> authorised={got!s:5s} (expected {expect!s:5s}) {'OK' if ok else 'FAIL'}")
    print(f"REQ-STALE-01 failures={failures}")
    if failures:
        raise SystemExit(1)
