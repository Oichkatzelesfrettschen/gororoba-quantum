# msolve against Singular std on J + m^N (E8-bar -> N-, p = 32009)

Timing probe at N = 7 to 11, retained as it ran: Singular inputs and logs (`singN.*`, `degbound11.*`), msolve inputs
and logs (`jmN.ms`, `msolveN.*`) and the driver scripts. At N = 11 Singular takes 133,031 ms with a degree bound and
144,845 ms without, both bases have 3,847 elements and the quotient has dimension 7,887. The
[Kaggle and local-run audit](../../../../../archive/reviews/kaggle-audit-2026-11-09/README.md) lists this directory as
undecided: the msolve logs were not read in full, so no msolve timing is claimed from it.
