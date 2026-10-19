> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_parameters.DRIVE_CROSSTALK_MATRIX.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_parameters.DRIVE_CROSSTALK_MATRIX.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 da67b5d402fb10c3520220e3e8e8682e5e05b5bf35ceadfef2d73479748d7418.

# DRIVE_CROSSTALK_MATRIX

iqm.cpc.core.observation.observation_parameters.DRIVE_CROSSTALK_MATRIX *= Parameter(name='characterization.model.crosstalk.drive_crosstalk_matrix', label='Drive crosstalk matrix', unit='dB', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None)*  
Drive crosstalk matrix \[dB\], a square matrix over the sorted qubits, with NaN for unmeasured or diagonal entries. Rows are target qubits, columns are control (drive) qubits.
