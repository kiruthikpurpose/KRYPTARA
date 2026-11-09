// Builds ../c/fs_quorum.c into a static lib, only for the differential test feature.
use std::{env, path::PathBuf, process::Command};
fn main() {
    println!("cargo:rerun-if-changed=../c/fs_quorum.c");
    if env::var("CARGO_FEATURE_DIFF_C").is_err() { return; }
    let out = PathBuf::from(env::var("OUT_DIR").unwrap());
    let o = out.join("fs_quorum.o");
    assert!(Command::new("gcc").args(["-std=c99","-O2","-c","../c/fs_quorum.c","-o"]).arg(&o).status().unwrap().success());
    assert!(Command::new("ar").arg("crs").arg(out.join("libfsquorum.a")).arg(&o).status().unwrap().success());
    println!("cargo:rustc-link-search=native={}", out.display());
    println!("cargo:rustc-link-lib=static=fsquorum");
}
