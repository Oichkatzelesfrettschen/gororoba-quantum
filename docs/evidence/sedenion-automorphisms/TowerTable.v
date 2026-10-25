(** The sedenion basis products of the integer pair tower of
    CdImaginarySumConference.v, (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)),
    evaluated at level k = 4: row a, column b holds the 16 coordinates of
    e_a e_b. CdTowerBasisSign.v proves the same products equal
    sigma_4(a, b) e_(a XOR b); this file evaluates the tower's own mul, so
    the printed table depends on the doubling formula and not on sigma. *)

From Stdlib Require Import ZArith List.
Require Import CdImaginarySumConference CdTowerBasisSign.
Import ListNotations.
Open Scope Z_scope.

Definition product_coords (a b : nat) : list Z :=
  map (coord 4 (mul 4 (basis 4 a) (basis 4 b))) (seq 0 16).

Definition table : list (list (list Z)) :=
  map (fun a => map (product_coords a) (seq 0 16)) (seq 0 16).

Eval vm_compute in table.
