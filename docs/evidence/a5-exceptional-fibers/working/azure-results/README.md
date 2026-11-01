# Azure fiber-run work trees

The complete working directories of the two Azure trial VMs that ran A_5 fiber computations, copied off each VM
before it was deleted. Each archive holds the inputs, logs and outputs exactly as the VM left them.

| Archive | sha256 | Bytes | Stored as |
|---|---|---|---|
| `vm1/vm1-work.tgz` (VM `gororoba-a5-fiber`, eastus) | `555a86abce09fc889356fdc60ab52bbd50ace127e30407d549aced03b21e82b0` | 405,302,105 | nine 45 MiB parts `vm1-work.tgz.part00` to `.part08` (listed in [split.txt](../../split.txt)) |
| `vm2/vm2-work.tgz` (VM `gororoba-a5-fiber-2`, westus2) | `839900e3aa86124dc60440c257912d62d040b7a829b5902b0b4671856c4fbb1b` | 436,297 | one file |

Restore and verify:

```sh
cat vm1/vm1-work.tgz.part* > vm1-work.tgz
sha256sum vm1-work.tgz vm2/vm2-work.tgz
tar -xzf vm1-work.tgz -C vm1-work
```

The vm1 tree's large outputs, all over F_32009 in Singular's `dp` ordering:

- `iso_d4/sq.txt` (1.17 GB): the reduced standard basis (option `redSB`) of J + m*P_4 in k[t2..t7], 1,879
  polynomials, where P_4 is the 640 degree-4 products of the 17 Iso generators reduced modulo J. It serves only to
  re-verify the normal forms by membership.
- `iso_d4/nf.txt` (447 MB): the normal forms of those 640 products modulo `sq.txt`. Their F_p rank, 640 over 141,676
  monomials, is the measured h_4. The jet-truncated normal forms `trunc/iso_d4/jnf13.txt` (640 polynomials over 3,105
  monomials, rank 640) certify the same h_4 = 640 at a fraction of the size, together with the K2 count of 640.
- `e8nm_a2/nf2.txt` (40 MB): the normal forms of the degree-2 products of the 21 E8-bar to N- generators modulo
  std(J + m*P_2); their rank is h_2 = 83, and their left kernel is the 148 quadric relations K2. The archive's
  `e8nm_a2-nf1.rel` and `e8nm_a2-nf2.rel` are byte copies of `e8nm_a2/nf1.txt` and `e8nm_a2/nf2.txt` (normal forms,
  not relations); the kernel step that turns normal forms into relations ran in the distributed degree-2 runs,
  whose 148 relations in y(1..21) are retained as
  `../distribute/out/a5-e8-d2/e8nm_p1/d2/relations-d2.rel` and `../distribute/out/a5-e8-d2/e8nm_p2/d2/relations-d2.rel`.

Each regenerates from the retained inputs in hours; the archives are the audit record of the runs as executed.
