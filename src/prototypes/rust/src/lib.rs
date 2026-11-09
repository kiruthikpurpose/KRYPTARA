//! Prototype crypto-agility descriptor registry (no_std, no alloc, no unsafe).
#![no_std]
#![forbid(unsafe_code)]

/// Assumption classes, bit positions identical to ../c/fs_quorum.h.
pub mod ac {
    pub const HASH_SHA2: u16 = 0x0001;
    pub const HASH_KECCAK: u16 = 0x0002;
    pub const LATTICE_STRUCT: u16 = 0x0004;
    pub const CLASSICAL_DL: u16 = 0x0008;
    pub const CLASSICAL_FACT: u16 = 0x0010;
    pub const CODE_BASED: u16 = 0x0020;
    pub const MULTIVARIATE: u16 = 0x0040;
    pub const RESERVED7: u16 = 0x0080;
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Role { Signature, Kem, Hash }

/// One algorithm descriptor. `assumptions` = classes whose break lets an attacker forge /
/// break this algorithm. Composite (AND-hybrid) algorithms list the union: conservative
/// for quorum accounting (a hybrid then conflicts with each of its parts).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Descriptor {
    pub id: u16,
    pub name: &'static str,
    pub role: Role,
    pub assumptions: u16,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum QuorumError { Empty, UnknownAlgorithm, EmptyAssumptions, Overlap, TooMany }

/// Pairwise-disjoint rule on raw bitsets. Same contract as C `fs_quorum_valid`.
pub fn quorum_valid(sets: &[u16]) -> bool {
    if sets.is_empty() { return false; }
    let mut acc = 0u16;
    for &s in sets {
        if s == 0 || acc & s != 0 { return false; }
        acc |= s;
    }
    true
}

pub const MAX_QUORUM: usize = 8;

pub struct Registry<'a> { table: &'a [Descriptor] }

impl<'a> Registry<'a> {
    /// `table` must have strictly increasing ids (checked by `validate`).
    pub const fn new(table: &'a [Descriptor]) -> Self { Registry { table } }
    pub fn validate(&self) -> bool {
        let mut prev: Option<u16> = None;
        for d in self.table {
            if d.assumptions == 0 { return false; }
            if let Some(p) = prev { if d.id <= p { return false; } }
            prev = Some(d.id);
        }
        true
    }
    pub fn get(&self, id: u16) -> Option<&Descriptor> {
        self.table.binary_search_by_key(&id, |d| d.id).ok().map(|i| &self.table[i])
    }
    /// Check a quorum of algorithm ids; returns the union of assumption classes.
    pub fn quorum(&self, ids: &[u16]) -> Result<u16, QuorumError> {
        if ids.is_empty() { return Err(QuorumError::Empty); }
        if ids.len() > MAX_QUORUM { return Err(QuorumError::TooMany); }
        let mut sets = [0u16; MAX_QUORUM];
        for (i, &id) in ids.iter().enumerate() {
            let d = self.get(id).ok_or(QuorumError::UnknownAlgorithm)?;
            if d.assumptions == 0 { return Err(QuorumError::EmptyAssumptions); }
            sets[i] = d.assumptions;
        }
        let s = &sets[..ids.len()];
        if !quorum_valid(s) { return Err(QuorumError::Overlap); }
        Ok(s.iter().fold(0, |a, &b| a | b))
    }
}

/// Built-in table. IDs are local to this prototype (NOT registry-assigned code points).
pub static BUILTIN: [Descriptor; 10] = [
    Descriptor { id: 1, name: "LMS-SHA256-M32", role: Role::Signature, assumptions: ac::HASH_SHA2 },
    Descriptor { id: 2, name: "SLH-DSA-SHA2", role: Role::Signature, assumptions: ac::HASH_SHA2 },
    Descriptor { id: 3, name: "SLH-DSA-SHAKE", role: Role::Signature, assumptions: ac::HASH_KECCAK },
    Descriptor { id: 4, name: "ML-DSA", role: Role::Signature, assumptions: ac::LATTICE_STRUCT },
    Descriptor { id: 5, name: "ECDSA-P256", role: Role::Signature, assumptions: ac::CLASSICAL_DL },
    Descriptor { id: 6, name: "RSA-PSS", role: Role::Signature, assumptions: ac::CLASSICAL_FACT },
    Descriptor { id: 7, name: "Hybrid-MLDSA+ECDSA", role: Role::Signature, assumptions: ac::LATTICE_STRUCT | ac::CLASSICAL_DL },
    Descriptor { id: 8, name: "XMSS-SHA256", role: Role::Signature, assumptions: ac::HASH_SHA2 },
    Descriptor { id: 9, name: "ML-KEM", role: Role::Kem, assumptions: ac::LATTICE_STRUCT },
    Descriptor { id: 10, name: "HQC", role: Role::Kem, assumptions: ac::CODE_BASED },
];

#[cfg(test)]
mod unit {
    use super::*;
    #[test] fn builtin_valid() { assert!(Registry::new(&BUILTIN).validate()); }
    #[test] fn examples() {
        let r = Registry::new(&BUILTIN);
        assert_eq!(r.quorum(&[1, 3]), Ok(ac::HASH_SHA2 | ac::HASH_KECCAK));
        assert_eq!(r.quorum(&[1, 2]), Err(QuorumError::Overlap));      // both SHA-2
        assert_eq!(r.quorum(&[4, 5]), Ok(ac::LATTICE_STRUCT | ac::CLASSICAL_DL));
        assert_eq!(r.quorum(&[7, 5]), Err(QuorumError::Overlap));      // hybrid conflicts with its DL part
        assert_eq!(r.quorum(&[]), Err(QuorumError::Empty));
        assert_eq!(r.quorum(&[99]), Err(QuorumError::UnknownAlgorithm));
        assert_eq!(r.quorum(&[1]), Ok(ac::HASH_SHA2));
    }
}
