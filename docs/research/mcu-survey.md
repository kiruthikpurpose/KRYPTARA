<!-- Title: MCU/MPU public-documentation survey (GATE-10, item 29) -->
> New (2026-11-09), item 29 of the 50-things completion list. Produced by a research subagent
> working from public vendor datasheets/app-notes/documentation only (no hardware in hand, no
> attack or bypass content). Document level: L3 (literature survey, not a measurement). Evidence
> label: [S] standard/vendor documentation, as cited per row.
>
> **This is NOT the same evidence class as E-A1 / GATE-10's original intent.** GATE-10 as written
> ("locked first stage with safe torn reads on ≥30% of sampled MCU families") implies a measured
> result on real silicon. This survey is literature-only: it reports what vendors' own
> documentation claims, not what was independently measured. Treat it as a defensible first pass
> that narrows where EXP-01/E-A1's real measurement should focus, not as a substitute for it.

# MCU/MPU public-documentation survey

17 families surveyed: STM32 (F4/L4/G4/H7 generic), STM32U5/U3, LPC55S6x, Kinetis K, i.MX RT1060,
SAM L10/L11, SAM D21, nRF52840, nRF5340, RP2040, RP2350, PSoC 6, CC2652R/P, MSP432P401R, ESP32,
RA6 (RA6M4/M5), EFR32xG21-28.

| Family | Vendor | Lockable first-stage (mechanism) | Torn-write safety documented | Dedicated presence input | Clock class |
|---|---|---|---|---|---|
| STM32 (F4/L4/G4/H7) | ST | Yes — RDP Level 2 (option byte 0xCC), irreversible, cannot downgrade | No — RM explicitly disclaims ("contents not guaranteed if reset during Flash op"); app-level mitigation only (AN4894) | No (TAMP_IN is general tamper detection, not presence) | ~80–216MHz M4/M7 |
| STM32U5/U3 | ST | Yes — RDP Level 2, permanent unless OEM2 regression pre-provisioned | Same disclaim as above | No | ~160MHz M33 |
| LPC55S6x | NXP | Yes — ROM root-of-trust, SRK hash in OTP, CMPA/CFPA lock fields | Not documented in sources found | No | ~150MHz M33 |
| Kinetis K | NXP | Partial — FSEC/KEYEN flash-config-field security, not fuse/OTP | Not found | No | ~100–180MHz M4 |
| i.MX RT1060 | NXP | Yes (uncertain) — HABv4, OCOTP eFuses; RT1060-specific lock behaviour not independently confirmed, inferred from i.MX6 | Not documented | No | ~600MHz M7 |
| SAM L10/L11 | Microchip | Yes — TrustZone region fuses (BS/BNSC/BOOTPROT/etc, AN5365) | Not found | No | ~32MHz M23 |
| SAM D21 | Microchip | Partial — NVM User Row LOCK bits, region-granular, reversible only via full chip erase | Not found | No | ~48MHz M0+ |
| nRF52840 | Nordic | Yes — APPROTECT (UICR), disable requires full chip erase; Nordic also published an advisory on software-only bypass on some revisions | Not found | No | 64MHz M4 |
| nRF5340 | Nordic | Yes — two-tier AP-Protect + SECUREAPPROTECT, lockable permanently | Not found | No | 128MHz M33 (dual-core) |
| RP2040 | Raspberry Pi | Partial/unconfirmed — RP2040-specific OTP secure-boot detail not found; RP2350 sibling documented | Not found | No | 133MHz M0+ |
| RP2350 | Raspberry Pi | Yes — 8KB anti-fuse OTP, OTP page locking, key fingerprint, secure-boot flag, glitch detector | Not found | No | 150MHz M33/Hazard3 (dual-core) |
| PSoC 6 | Infineon | Yes — SECURE lifecycle stage, eFuse SHA-256 hash, irreversible DEAD state on integrity failure | Implied by DEAD-state integrity checks; no explicit power-loss statement | No | ~150MHz M4+M0+ |
| CC2652R/P | TI | Partial — CCFG BOOTLOADER_ENABLE permanent-disable field; sector write-protect bits | Not found | No | 48MHz M4 |
| MSP432P401R | TI | Yes — JTAG/SWD Lock + secure flash zones, reversible only via full JTAG Factory Reset (erases all) | Not found | No | 48MHz M4F |
| ESP32 | Espressif | Yes — Flash Encryption + Secure Boot v2, one-time eFuses incl. JTAG_DISABLE, irreversible once burned in Release mode | **The one explicit caveat found in this survey**: vendor warns power loss during eFuse BURNING "could cause issues... permanent boot-up failures" — about one-time fuse programming, not general flash writes | No | 240MHz Xtensa LX6 (not ARM) |
| RA6 (RA6M4/M5) | Renesas | Yes — Security MPU + Flash Access Window, Permanent Block Protection | Not found | No | ~120–200MHz M33/M4 |
| EFR32xG21-28 | Silicon Labs | Yes — Secure Boot (permanent) + Permanent Debug Lock (bricks RMA path) | Not found; vendor flags brick risk from premature locking | No | ~40MHz M33 |

## Summary

14/17 (82%) families clearly document a Yes/Partial permanent or semi-permanent first-stage lock
mechanism. 2/17 (Kinetis, RP2040) had only partial/unconfirmed evidence; i.MX RT1060's exact lock
behaviour couldn't be confirmed from part-specific sources (inferred from the i.MX6 family only,
flagged explicitly). **Torn/interrupted-write safety is almost never explicitly guaranteed**: of 17
families, only Espressif's eFuse-burning warning is an explicit power-loss caveat, and it concerns
one-time fuse programming, not general flash writes — so by a strict reading, **0/17 to 1/17
(0-6%) explicitly document safe torn WRITES**, well below the 30% GATE-10 threshold. **0/17 (0%)
document anything resembling a dedicated physical presence input** distinct from general-purpose
tamper detection (STM32's TAMP_IN is the closest analogue, and it's an anti-intrusion peripheral,
not a consent switch).

## GATE-10 disposition

Reading GATE-10 strictly ("safe torn reads on ≥30% of sampled families") against this literature
survey: **it fails** — not because MCUs can't lock a first stage (82% can), but because vendors
essentially never document torn-write safety as a guarantee; application-level mitigation (a
journal, dual-slot commit, as ST's own AN4894 recommends) is the documented pattern, not a hardware
property. This matches `docs/architecture/*`'s own design (`src/prototypes/c/fs_journal.c`'s
write-ahead journal exists precisely because the hardware doesn't guarantee this) — so the finding
confirms the architecture's own premise rather than contradicting it, but it does mean GATE-10 as
literally worded cannot pass on documentation alone; only EXP-01/E-A1's real measurement (actually
cutting power mid-write on real silicon and checking the journal's own recovery, not the flash
controller's) can close it. **This survey does not trigger the 50-things list's stop condition**
(too few LOCKABLE parts) because lockability itself is fine; it does sharpen what E-A1 needs to
measure directly (recovery-after-cut behaviour under the project's OWN journal, not a hardware
guarantee that doesn't exist).

## Honesty notes (carried from the research agent's own report)

- RP2040-specific OTP/secure-boot and i.MX RT1060 fuse-lock behaviour are flagged
  unconfirmed/by-analogy, not asserted as fact.
- Several entries rely on vendor community/forum posts layered on app-note material where the
  primary datasheet text itself wasn't directly retrieved; marked inline.
- No attack/bypass procedures were researched or included. Several search results surfaced
  third-party glitching/fault-injection papers (STM32 RDP, RP2350); their technical content was
  deliberately excluded, per this project's defensive-only hardware-discussion rule.
