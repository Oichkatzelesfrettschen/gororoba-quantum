> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6d03c9fd79c6088c0f1ddbffd889ea2f0a97674969e6d86726fdaa7f708178d3.

# iqm.benchmarks.compressive_gst.mgst.algorithm

The main algorithm and functions that perform iteration steps.

Functions

|  |  |
|----|----|
| [`A_SFN_riem_Hess`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.A_SFN_riem_Hess.html#iqm.benchmarks.compressive_gst.mgst.algorithm.A_SFN_riem_Hess "iqm.benchmarks.compressive_gst.mgst.algorithm.A_SFN_riem_Hess")(K, A, B, y, J\[, lam, mle\]) | Riemannian saddle free Newton step on the POVM parametrization. |
| [`B_SFN_riem_Hess`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.B_SFN_riem_Hess.html#iqm.benchmarks.compressive_gst.mgst.algorithm.B_SFN_riem_Hess "iqm.benchmarks.compressive_gst.mgst.algorithm.B_SFN_riem_Hess")(K, A, B, y, J\[, lam, mle\]) | Riemannian saddle free Newton step on the initial state parametrization. |
| [`SFN_riem_Hess`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess.html#iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess "iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess")(K, E, rho, y, J\[, lam, ls, ...\]) | Riemannian saddle free Newton step on each gate individually. |
| [`SFN_riem_Hess_full`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess_full.html#iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess_full "iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess_full")(K, E, rho, y, J\[, lam, ...\]) | Riemannian saddle free Newton step on product manifold of all gates. |
| [`gd`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.gd.html#iqm.benchmarks.compressive_gst.mgst.algorithm.gd "iqm.benchmarks.compressive_gst.mgst.algorithm.gd")(K, E, rho, y, J\[, fixed_gates, mle\]) | Do Riemannian gradient descent optimization step on gates. |
| [`optimize`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.optimize.html#iqm.benchmarks.compressive_gst.mgst.algorithm.optimize "iqm.benchmarks.compressive_gst.mgst.algorithm.optimize")(y, J, method, K, rho, A, B, ...\[, mle\]) | Full gate set optimization update alternating on E, K and rho. |
| [`run_mGST`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.run_mGST.html#iqm.benchmarks.compressive_gst.mgst.algorithm.run_mGST "iqm.benchmarks.compressive_gst.mgst.algorithm.run_mGST")(args\[, method, max_inits, ...\]) | Main mGST routine. |
