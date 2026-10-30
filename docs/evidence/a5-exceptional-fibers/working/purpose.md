# What the fiber computations measure, and why

**Programme.** The open claim `dimension32-global-topology` asks for the global topology of the zero-divisor set of
the 32-dimensional Cayley-Dickson algebra A_5, stratified by nullity. Its roadmap is the table "Route to the global
classification" in `docs/notes/rank_locus_two_dimension_gap.md:323-341`. Items 3-5 are discharged: components and
closed equations of every rank stratum, a Whitney stratification by orbits of H = G_2(C) x SO(2,C) x C^*
(`docs/evidence/a5-strata-regularity/README.md`), and kernel bundles on every stratum
(`docs/design/a5-kernel-bundles-nullity8-program.md`). Item 6, **attachments**, is open: how the partner spheres
(kernel fibers) of a stratum specialize across each closure incidence, that is, the attaching maps a finite global
model (item 7) is glued from.

**Where the runs enter.** Each run takes a nullity-8 orbit closure Y (W8, E8-bar, Iso, X_+, X_-) and a smaller orbit
Z in its closure (N_+, N_-, VB, ...), with I the ideal of Z on Y (generators G, ambient relation J). The fiber cone
F(I) = sum_d I^d / m I^d (the special fiber of the Rees algebra at a point of Z, after the normal-cone translation)
is the coordinate ring of the exceptional fiber of the blow-up of Y along Z over that point: the set of limiting
directions by which Y approaches Z. Its Hilbert function h_d, its degree and its relation degrees (for example the
K2 relations of degree 23 on Iso) describe that limit set. Item 6 needs exactly this set: the program doc (gap N3,
lines 38-40) says a nullity-12 boundary orbit carries the nullity-8 kernel representation plus two extra dimensions
and that "the shape of that specialization is the attaching data", and the nullity-8 record finds boundary limits
path-dependent, so the attaching datum is the whole limit set, not one inclusion. The fiber cone is its algebraic
certificate.

**What a result must deliver.** For each (Y, Z): the dimension and degree of the exceptional fiber, enough of its
Hilbert function to fix it (or its Hilbert series), and ideally its defining ideal or its decomposition into
components. Any reformulation that computes the same limit set is acceptable, for example: the exceptional fiber via
implicitization of limits of a parametrized family of curves into Z; the fiber over one point only, since H acts
transitively on Z and the point stabilizer acts on the fiber (equivariant decomposition by that representation);
the kernel-map limits directly (limits of ker L_y as y -> Z), which is the attaching datum itself. An option that
yields only h_d up to some d is weaker than one that yields the fiber's components; state which each option yields.
