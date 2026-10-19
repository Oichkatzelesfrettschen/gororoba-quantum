> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.calset_to_cal_data_tree.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.calset_to_cal_data_tree.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 863d282ed70dc3ab567eb816665654cb2443d55403ddfc856650d404654accfe.

# iqm.cpc.utils.calset_to_cal_data_tree

iqm.cpc.utils.calset_to_cal_data_tree(*calibration_set_values*)  
Build an iqm-pulse QuantumOp calibration data tree from a calibration set.

Splits the dotted observation names that are prefixed with “gates.” into the corresponding calibration data tree paths.

Parameters:  
**calibration_set_values** (*CalibrationSetValues*)

Return type:  
OpCalibrationDataTree
