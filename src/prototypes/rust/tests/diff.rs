//! Differential + property tests. Run: cargo test --features diff-c --release
use descreg::*;
use proptest::prelude::*;

#[cfg(feature = "diff-c")]
extern "C" { fn fs_quorum_valid(sets: *const u16, n: u32) -> i32; }
#[cfg(feature = "diff-c")]
fn c_valid(s: &[u16]) -> bool { unsafe { fs_quorum_valid(s.as_ptr(), s.len() as u32) != 0 } }

/// Reference oracle written independently: O(n^2) pairwise definition straight from the rule.
fn oracle(s: &[u16]) -> bool {
    if s.is_empty() { return false; }
    if s.iter().any(|&x| x == 0) { return false; }
    for i in 0..s.len() { for j in i + 1..s.len() { if s[i] & s[j] != 0 { return false; } } }
    true
}

#[test]
fn rust_matches_oracle_exhaustive_u4_universe() {
    // all ordered tuples of length 1..=4 over the full 4-class universe (16 sets): 16+256+4096+65536
    let mut count = 0u64;
    for len in 1..=4usize {
        let total = 16u32.pow(len as u32);
        for code in 0..total {
            let mut v = [0u16; 4]; let mut c = code;
            for k in 0..len { v[k] = (c % 16) as u16; c /= 16; }
            assert_eq!(quorum_valid(&v[..len]), oracle(&v[..len]), "{:?}", &v[..len]);
            count += 1;
        }
    }
    assert_eq!(count, 16 + 256 + 4096 + 65536);
}

#[cfg(feature = "diff-c")]
#[test]
fn c_vs_rust_exhaustive_8_classes() {
    // universe = the 8 assigned classes (256 sets). All tuples of length 1,2,3 : 256 + 65,536 + 16,777,216
    let mut n = 0u64; let mut valid = 0u64;
    assert_eq!(c_valid(&[]), quorum_valid(&[]));
    for a in 0..256u16 {
        let t = [a]; assert_eq!(c_valid(&t), quorum_valid(&t)); n += 1; valid += quorum_valid(&t) as u64;
        for b in 0..256u16 {
            let t = [a, b]; let r = quorum_valid(&t);
            assert_eq!(c_valid(&t), r, "{:?}", t); n += 1; valid += r as u64;
            for c in 0..256u16 {
                let t = [a, b, c]; let r = quorum_valid(&t);
                assert_eq!(c_valid(&t), r, "{:?}", t); n += 1; valid += r as u64;
            }
        }
    }
    println!("differential C vs Rust: {} tuples compared, {} valid", n, valid);
    assert_eq!(n, 256 + 65_536 + 16_777_216);
}

#[cfg(feature = "diff-c")]
#[test]
fn c_vs_rust_exhaustive_subsets_of_6_class_universe_len4() {
    // every length-4 tuple over a 6-class universe (64 sets): 16,777,216 tuples
    for a in 0..64u16 { for b in 0..64u16 { for c in 0..64u16 { for d in 0..64u16 {
        let t = [a, b, c, d]; assert_eq!(c_valid(&t), quorum_valid(&t), "{:?}", t);
    }}}}
}

proptest! {
    #[test]
    fn prop_matches_oracle(v in proptest::collection::vec(any::<u16>(), 0..9)) {
        prop_assert_eq!(quorum_valid(&v), oracle(&v));
        #[cfg(feature = "diff-c")] prop_assert_eq!(c_valid(&v), quorum_valid(&v));
    }
    #[test]
    fn prop_permutation_invariant(mut v in proptest::collection::vec(any::<u16>(), 1..8), seed in any::<u64>()) {
        let r = quorum_valid(&v);
        // deterministic shuffle
        let mut s = seed | 1;
        for i in (1..v.len()).rev() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; v.swap(i, (s % (i as u64 + 1)) as usize); }
        prop_assert_eq!(quorum_valid(&v), r);
    }
    #[test]
    fn prop_sub_quorum_of_valid_is_valid(v in proptest::collection::vec(1u16..=255, 1..8)) {
        if quorum_valid(&v) { for k in 1..=v.len() { prop_assert!(quorum_valid(&v[..k])); } }
    }
    #[test]
    fn prop_duplicate_member_invalid(a in 1u16..) { prop_assert!(!quorum_valid(&[a, a])); }
    #[test]
    fn prop_registry_union_is_disjoint_sum(ids in proptest::collection::vec(1u16..=10, 1..5)) {
        let r = Registry::new(&BUILTIN);
        match r.quorum(&ids) {
            Ok(u) => { let sum: u32 = ids.iter().map(|&i| r.get(i).unwrap().assumptions.count_ones()).sum();
                       prop_assert_eq!(u.count_ones(), sum); }
            Err(e) => prop_assert_eq!(e, QuorumError::Overlap),
        }
    }
}
