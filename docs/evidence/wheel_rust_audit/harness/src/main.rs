//! Differential harness for the `wheel` crate 0.1.0.
//!
//! Prints one JSON document on stdout: every unary and binary operation of
//! `w64` over a fixed binary64 corpus, every wheel law of
//! gororoba_quantum/wheel_algebra.py evaluated in `w64` over seeded triples,
//! the same for `qw64` over a rational corpus, and `qw8` integer-overflow
//! probes. Every `w64` value prints as its 16-hex-digit IEEE bit pattern.
//! scripts/wheel_rust_audit.py regenerates the corpus and triples with the
//! same SplitMix64 stream and recomputes every result exactly.

use std::fmt::Write as _;
use std::hint::black_box;
use std::panic;

use wheel::{qw64, qw8, w64, Wheel};

const SEED: u64 = 20_241_022;
const RANDOM_DYADICS: usize = 16;
const RANDOM_TRIPLES: usize = 1024;

/// Fixed corpus bit patterns: signed zeros, unit values, both infinities,
/// four NaN encodings, small dyadics, binary64 roundings of 1/10, 1/3 and
/// -2/3, the 2^53 boundary, the extreme normals and subnormals.
const FIXED: [u64; 39] = [
    0x0000_0000_0000_0000, // +0
    0x8000_0000_0000_0000, // -0
    0x3ff0_0000_0000_0000, // 1
    0xbff0_0000_0000_0000, // -1
    0x7ff0_0000_0000_0000, // +inf
    0xfff0_0000_0000_0000, // -inf
    0x7ff8_0000_0000_0000, // quiet NaN (f64::NAN)
    0x7ff8_0000_0000_0001, // quiet NaN with payload 1
    0xfff8_0000_0000_0000, // negative quiet NaN
    0x7ff0_0000_0000_0001, // signaling NaN
    0x3fe0_0000_0000_0000, // 0.5
    0xbfd0_0000_0000_0000, // -0.25
    0x4000_0000_0000_0000, // 2
    0x4008_0000_0000_0000, // 3
    0xc000_0000_0000_0000, // -2
    0x3ff8_0000_0000_0000, // 1.5
    0x3fd8_0000_0000_0000, // 0.375
    0xc01b_0000_0000_0000, // -6.75
    0x4090_0000_0000_0000, // 1024
    0x3f50_0000_0000_0000, // 2^-10
    0x4014_0000_0000_0000, // 5
    0x401c_0000_0000_0000, // 7
    0x4024_0000_0000_0000, // 10
    0x3fb9_9999_9999_999a, // RNE(1/10)
    0x3fd5_5555_5555_5555, // RNE(1/3)
    0xbfe5_5555_5555_5555, // RNE(-2/3)
    0x4340_0000_0000_0000, // 2^53
    0x4340_0000_0000_0001, // 2^53 + 2
    0x3ff0_0000_0000_0001, // 1 + 2^-52
    0x7fef_ffff_ffff_ffff, // f64::MAX
    0xffef_ffff_ffff_ffff, // -f64::MAX
    0x7fe0_0000_0000_0000, // 2^1023
    0x7fe1_ccf3_85eb_c8a0, // RNE(1e308)
    0x6570_0000_0000_0000, // 2^600
    0x1a70_0000_0000_0000, // 2^-600
    0x0010_0000_0000_0000, // f64::MIN_POSITIVE = 2^-1022
    0x0000_0000_0000_0001, // 2^-1074
    0x8000_0000_0000_0001, // -2^-1074
    0x000f_ffff_ffff_ffff, // largest subnormal
];

/// Corpus indices of the axiom pool, whose full cube of triples is evaluated:
/// +0, -0, 1, -1, +inf, -inf, NaN, signaling NaN, 3, 0.5, RNE(1/3),
/// RNE(1/10), f64::MAX, 2^-1022, 2^-1074, 2^600.
const AXIOM_POOL: [usize; 16] = [0, 1, 2, 3, 4, 5, 6, 9, 13, 10, 24, 23, 29, 35, 36, 33];

/// The qw64 corpus as constructor arguments; (2, -4) and (-3, 0) exercise
/// normalization of non-canonical pairs.
const QW_CORPUS: [(i64, i64); 14] = [
    (0, 1),
    (1, 1),
    (-1, 1),
    (1, 0),
    (0, 0),
    (3, 2),
    (-2, 5),
    (7, 1),
    (1, 3),
    (-5, 6),
    (2, -4),
    (-3, 0),
    (12, 1),
    (-1, 7),
];

const LAWS: [&str; 18] = [
    "(1) addition is associative",
    "(1) addition is commutative",
    "(1) 0 is the additive unit",
    "(2) multiplication is associative",
    "(2) multiplication is commutative",
    "(2) 1 is the multiplicative unit",
    "(2) involution: //x = x",
    "(2) involution is multiplicative: /(xy) = /x /y",
    "(3) distributive: (x + y)z + 0z = xz + yz",
    "(4) division: x/y + z + 0y = (x + yz)/y",
    "(5) 0 * 0 = 0",
    "(6) (x + 0y)z = xz + 0y",
    "(7) /(x + 0y) = /x + 0y",
    "(8) x + 0/0 = 0/0",
    "(10) 0x + 0y = 0xy",
    "(11) (0/0)x = 0/0",
    "(12) x/x = 1 + 0x/x",
    "(p. 5) x - x = 0x^2",
];

struct SplitMix64(u64);

impl SplitMix64 {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e37_79b9_7f4a_7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
        z ^ (z >> 31)
    }
}

/// A dyadic value with at most 21 significant bits and binary exponent in
/// [-40, 40], so every corpus value is exactly representable.
fn random_dyadic(rng: &mut SplitMix64) -> u64 {
    let r = rng.next();
    let sign = r >> 63;
    let exponent = 1023 - 40 + (r >> 32) % 81;
    let mantissa = (r & 0xf_ffff) << 32;
    (sign << 63) | (exponent << 52) | mantissa
}

/// The w64 laws, each as its (left, right) sides, with the expression trees
/// of wheel_algebra.axioms; division is x * /y and x - x is x + (-x).
fn laws<W: Wheel + Copy>(x: W, y: W, z: W) -> [(W, W); 18] {
    let zero = W::ZERO;
    let one = W::ONE;
    let div = |a: W, b: W| a.mul(&b.inv());
    let bottom = div(zero, zero);
    [
        (x.add(&y).add(&z), x.add(&y.add(&z))),
        (x.add(&y), y.add(&x)),
        (x.add(&zero), x),
        (x.mul(&y).mul(&z), x.mul(&y.mul(&z))),
        (x.mul(&y), y.mul(&x)),
        (x.mul(&one), x),
        (x.inv().inv(), x),
        (x.mul(&y).inv(), x.inv().mul(&y.inv())),
        (
            x.add(&y).mul(&z).add(&zero.mul(&z)),
            x.mul(&z).add(&y.mul(&z)),
        ),
        (
            div(x, y).add(&z).add(&zero.mul(&y)),
            div(x.add(&y.mul(&z)), y),
        ),
        (zero.mul(&zero), zero),
        (x.add(&zero.mul(&y)).mul(&z), x.mul(&z).add(&zero.mul(&y))),
        (x.add(&zero.mul(&y)).inv(), x.inv().add(&zero.mul(&y))),
        (x.add(&bottom), bottom),
        (zero.mul(&x).add(&zero.mul(&y)), zero.mul(&x.mul(&y))),
        (bottom.mul(&x), bottom),
        (div(x, x), one.add(&zero.mul(&x).mul(&x.inv()))),
        (x.sub(&x), zero.mul(&x).mul(&x)),
    ]
}

/// The binary64 bit pattern inside a w64. Wheel64 is a one-field tuple
/// struct over f64 with private access; every pattern is cross-checked
/// against the crate's own Debug rendering before it is printed.
fn bits(w: w64) -> u64 {
    const _: () = assert!(core::mem::size_of::<w64>() == 8);
    const _: () = assert!(core::mem::align_of::<w64>() == 8);
    // SAFETY: w64 has the size and alignment of f64 and wraps one f64.
    let value: f64 = unsafe { core::mem::transmute::<w64, f64>(w) };
    let pattern = value.to_bits();
    let debug = format!("{w:?}");
    let expected = if value.is_nan() {
        "Wheel64::BOTTOM".to_string()
    } else if value.is_infinite() {
        "Wheel64::INFINITY".to_string()
    } else if value == 0.0 {
        "Wheel64::ZERO".to_string()
    } else {
        let inner = debug
            .strip_prefix("Wheel64(")
            .and_then(|rest| rest.strip_suffix(')'))
            .unwrap_or_else(|| panic!("unexpected rendering {debug}"));
        let parsed: f64 = inner.parse().expect("Display of a finite f64 parses");
        assert_eq!(
            parsed.to_bits(),
            pattern,
            "bit extraction disagrees with Debug"
        );
        debug.clone()
    };
    assert_eq!(debug, expected, "bit extraction disagrees with Debug");
    pattern
}

fn hex(w: w64) -> String {
    format!("\"{:016x}\"", bits(w))
}

fn pair_of<T: std::fmt::Debug>(w: &T) -> String {
    let debug = format!("{w:?}");
    let inner = debug
        .strip_prefix("FractionWheel(")
        .and_then(|rest| rest.strip_suffix(')'))
        .unwrap_or_else(|| panic!("unexpected rendering {debug}"));
    let (n, d) = inner.split_once(", ").expect("two fields");
    format!("[{n}, {d}]")
}

fn list(items: impl IntoIterator<Item = String>) -> String {
    let joined: Vec<String> = items.into_iter().collect();
    format!("[{}]", joined.join(", "))
}

/// Per law, the hold flags of every triple as a hex string (triple t is bit
/// t mod 4 of hex digit t / 4), and the sides of every failing case.
fn law_section<W: Wheel + Copy>(
    triples: &[(usize, usize, usize)],
    corpus: &[W],
    render: impl Fn(&W) -> String,
) -> (String, String) {
    let mut flags = vec![vec![0u8; triples.len().div_ceil(4)]; LAWS.len()];
    let mut failures = Vec::new();
    for (t, &(i, j, k)) in triples.iter().enumerate() {
        let sides = laws(corpus[i], corpus[j], corpus[k]);
        for (law, (left, right)) in sides.iter().enumerate() {
            if left == right {
                flags[law][t / 4] |= 1 << (t % 4);
            } else {
                failures.push(format!("[{law}, {t}, {}, {}]", render(left), render(right)));
            }
        }
    }
    let holds = list(flags.iter().map(|row| {
        let digits: String = row.iter().map(|d| format!("{d:x}")).collect();
        format!("\"{digits}\"")
    }));
    (holds, list(failures))
}

fn binary_table<W: Copy>(
    corpus: &[W],
    op: impl Fn(W, W) -> W,
    render: impl Fn(&W) -> String,
) -> String {
    list(
        corpus
            .iter()
            .map(|&a| list(corpus.iter().map(|&b| render(&op(a, b))))),
    )
}

fn f64_section(rng: &mut SplitMix64) -> String {
    let mut patterns: Vec<u64> = FIXED.to_vec();
    patterns.extend((0..RANDOM_DYADICS).map(|_| random_dyadic(rng)));
    let corpus: Vec<w64> = patterns
        .iter()
        .map(|&b| w64::new(f64::from_bits(b)))
        .collect();
    for (w, &b) in corpus.iter().zip(&patterns) {
        assert_eq!(bits(*w), b, "w64::new preserves the bit pattern");
    }
    let mut triples: Vec<(usize, usize, usize)> = Vec::new();
    for &i in &AXIOM_POOL {
        for &j in &AXIOM_POOL {
            for &k in &AXIOM_POOL {
                triples.push((i, j, k));
            }
        }
    }
    let n = corpus.len() as u64;
    for _ in 0..RANDOM_TRIPLES {
        let i = (rng.next() % n) as usize;
        let j = (rng.next() % n) as usize;
        let k = (rng.next() % n) as usize;
        triples.push((i, j, k));
    }
    let render = |w: &w64| hex(*w);
    let (holds, failures) = law_section(&triples, &corpus, render);
    let mut out = String::new();
    write!(
        out,
        "{{\"corpus\": {}, \"neg\": {}, \"inv\": {}, \"add\": {}, \"sub\": {}, \"mul\": {}, \"div\": {}, \
         \"triples\": {}, \"holds\": {}, \"failures\": {}}}",
        list(corpus.iter().map(render)),
        list(corpus.iter().map(|&a| hex(-a))),
        list(corpus.iter().map(|&a| hex(a.inv()))),
        binary_table(&corpus, |a, b| a + b, render),
        binary_table(&corpus, |a, b| a - b, render),
        binary_table(&corpus, |a, b| a * b, render),
        binary_table(&corpus, |a, b| a / b, render),
        list(triples.iter().map(|(i, j, k)| format!("[{i}, {j}, {k}]"))),
        holds,
        failures,
    )
    .expect("write to String");
    out
}

fn qw_section() -> String {
    let corpus: Vec<qw64> = QW_CORPUS.iter().map(|&(n, d)| qw64::new(n, d)).collect();
    let mut triples = Vec::new();
    for i in 0..corpus.len() {
        for j in 0..corpus.len() {
            for k in 0..corpus.len() {
                triples.push((i, j, k));
            }
        }
    }
    let render = |w: &qw64| pair_of(w);
    let (holds, failures) = law_section(&triples, &corpus, render);
    format!(
        "{{\"inputs\": {}, \"corpus\": {}, \"neg\": {}, \"inv\": {}, \"add\": {}, \"sub\": {}, \"mul\": {}, \
         \"div\": {}, \"holds\": {}, \"failures\": {}}}",
        list(QW_CORPUS.iter().map(|(n, d)| format!("[{n}, {d}]"))),
        list(corpus.iter().map(render)),
        list(corpus.iter().map(|&a| render(&-a))),
        list(corpus.iter().map(|a| render(&a.inv()))),
        binary_table(&corpus, |a, b| a + b, render),
        binary_table(&corpus, |a, b| a - b, render),
        binary_table(&corpus, |a, b| a * b, render),
        binary_table(&corpus, |a, b| a / b, render),
        holds,
        failures,
    )
}

/// One qw8 probe: the rendered result, or "panic" when the operation
/// panics on integer overflow.
fn probe(op: impl Fn() -> String + panic::UnwindSafe) -> String {
    match panic::catch_unwind(op) {
        Ok(rendered) => rendered,
        Err(_) => "\"panic\"".to_string(),
    }
}

fn overflow_section() -> String {
    let q = |n: i8, d: i8| black_box(qw8::new(black_box(n), black_box(d)));
    let probes: Vec<(&str, String)> = vec![
        (
            "(1/2) + (1/3)",
            probe(move || pair_of(&(q(1, 2) + q(1, 3)))),
        ),
        (
            "(1/16) * (1/16)",
            probe(move || pair_of(&(q(1, 16) * q(1, 16)))),
        ),
        (
            "100 + 100",
            probe(move || pair_of(&(q(100, 1) + q(100, 1)))),
        ),
        ("64 * 2", probe(move || pair_of(&(q(64, 1) * q(2, 1))))),
        ("-(-128)", probe(move || pair_of(&(-q(-128, 1))))),
        ("/(-128)", probe(move || pair_of(&q(-128, 1).inv()))),
        (
            "127/2 == 127/3",
            probe(move || (q(127, 2) == q(127, 3)).to_string()),
        ),
        (
            "127/2 == 127/2",
            probe(move || (q(127, 2) == q(127, 2)).to_string()),
        ),
    ];
    list(
        probes
            .into_iter()
            .map(|(name, result)| format!("{{\"probe\": \"{name}\", \"result\": {result}}}")),
    )
}

fn overflow_checks() -> bool {
    panic::catch_unwind(|| black_box(black_box(i8::MAX) + black_box(1i8))).is_err()
}

/// Runs `f` with the panic message hook silenced, so overflow probes that
/// panic by design leave stderr empty.
fn quietly<R>(f: impl FnOnce() -> R) -> R {
    let previous = panic::take_hook();
    panic::set_hook(Box::new(|_| {}));
    let result = f();
    panic::set_hook(previous);
    result
}

fn main() {
    let section = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "full".to_string());
    let checks = quietly(overflow_checks);
    let mut out = format!(
        "{{\"schema\": \"wheel-rust-audit-harness-v1\", \"crate\": \"wheel 0.1.0\", \"section\": \"{section}\", \
         \"overflow_checks\": {checks}, \"seed\": {SEED}, \"laws\": {}",
        list(LAWS.iter().map(|law| format!("\"{law}\"")))
    );
    match section.as_str() {
        "full" => {
            let mut rng = SplitMix64(SEED);
            let f64s = f64_section(&mut rng);
            let qws = qw_section();
            write!(out, ", \"w64\": {f64s}, \"qw64\": {qws}").expect("write to String");
        }
        "qw8-overflow" => {}
        other => panic!("unknown section {other}"),
    }
    write!(out, ", \"qw8_overflow\": {}}}", quietly(overflow_section)).expect("write to String");
    println!("{out}");
}
