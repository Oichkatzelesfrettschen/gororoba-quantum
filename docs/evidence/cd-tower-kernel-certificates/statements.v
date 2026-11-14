(** The statements of the kernel certificates, printed for the receipt. *)
From Stdlib Require Import ZArith Zmod.
Require Import CdTowerRing CdTowerRingBasis CdTowerRingBaseChange CdTowerKernelCertificate CdTowerCanonicalKernels.

Module ZmodHom := IntegerHom Zmod7.
Module Generic := KernelCertificate IntegerRing Zmod7 ZmodHom.
Check Generic.kernel_vectors.
Check Generic.kernel_spanned.
Check Generic.coefficients_recovered.
Check Generic.combination_zero_coefficients.
Check Generic.kernel_free_basis.
Check Generic.kernel_coefficients_unique.
Check Mod7.W8_kernel_free_basis.
Check Mod7.V_kernel_free_basis.
Check Mod7.Np_kernel_free_basis.
