(* Coordinates over Z[sqrt 3] of psi2(e_m) = 2 psi(e_m) at level 4, as pairs (a, b) for a + b sqrt 3: row m
   lists the 16 coordinates of the image of the m-th basis element. *)
From Stdlib Require Import List ZArith.
Require CdTowerOrderThreeMap.
Definition image_row (m : nat) : list (Z * Z) :=
  map (CdTowerOrderThreeMap.Root3Map.BC.TA.coord 4 (CdTowerOrderThreeMap.Root3Map.images m)) (seq 0 16).
Eval vm_compute in map image_row (seq 0 16).
