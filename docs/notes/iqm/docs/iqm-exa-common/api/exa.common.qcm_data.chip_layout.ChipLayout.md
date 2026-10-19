> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_layout.ChipLayout.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_layout.ChipLayout.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f8f9d6f07b1ebce3f3b2401b24ee8b2a1729f49e33dbb9722419e4f382c80271.

# ChipLayout

Module: [`exa.common.qcm_data.chip_layout`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_layout.html#module-exa.common.qcm_data.chip_layout "exa.common.qcm_data.chip_layout")

*class* ChipLayout(*qubits*, *couplers*, *computational_resonators*, *qubits_without_probeline=None*, *angles=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

The chip layout contains the components, their 2D cartesian coordinates, and their angles.

The subset of qubits without any probe lines, which appears in certain constellation-type chips, are stored in the additional attribute qubits_without_probeline.

The angle is assumed to lie between the positive x-axis and the orientation vector of the component and measured in degrees.

Parameters:  
- **qubits** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – Dictionary of qubit names mapped to their 2d coordinates

- **couplers** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – Dictionary of coupler names mapped to their 2d coordinates

- **computational_resonators** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – Dictionary of computational resonators names mapped to their 2d coordinates

- **qubits_without_probeline** (*Iterable\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Iterable of qubits without a probeline

- **angles** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – Dictionary of component names mapped to their 2d coordinates

Attributes

|                            |     |
|----------------------------|-----|
| `components`               |     |
| `computational_resonators` |     |
| `couplers`                 |     |
| `qubits`                   |     |
| `qubits_without_probeline` |     |

Methods

|  |  |
|----|----|
| [`from_chip_design_record`](#exa.common.qcm_data.chip_layout.ChipLayout.from_chip_design_record "exa.common.qcm_data.chip_layout.ChipLayout.from_chip_design_record") | Construct the chip layout from a raw chip design record. |
| [`get_all_qubit_angles`](#exa.common.qcm_data.chip_layout.ChipLayout.get_all_qubit_angles "exa.common.qcm_data.chip_layout.ChipLayout.get_all_qubit_angles") | Get the angles for all qubits. |
| [`get_all_qubit_coordinates`](#exa.common.qcm_data.chip_layout.ChipLayout.get_all_qubit_coordinates "exa.common.qcm_data.chip_layout.ChipLayout.get_all_qubit_coordinates") | Get the coordinates for all qubits. |
| [`get_angle`](#exa.common.qcm_data.chip_layout.ChipLayout.get_angle "exa.common.qcm_data.chip_layout.ChipLayout.get_angle") | Get the angle for the given component. |
| [`get_coordinates`](#exa.common.qcm_data.chip_layout.ChipLayout.get_coordinates "exa.common.qcm_data.chip_layout.ChipLayout.get_coordinates") | Get the coordinates for the given component. |
| `mirror_yaxis` |  |
| [`move_origin`](#exa.common.qcm_data.chip_layout.ChipLayout.move_origin "exa.common.qcm_data.chip_layout.ChipLayout.move_origin") | Changes the origin of the Cartesian coordinate system such that all elements move into the first quadrant. |
| [`normalize_coordinates`](#exa.common.qcm_data.chip_layout.ChipLayout.normalize_coordinates "exa.common.qcm_data.chip_layout.ChipLayout.normalize_coordinates") | Rescale component coordinates |
| [`rotate_layout`](#exa.common.qcm_data.chip_layout.ChipLayout.rotate_layout "exa.common.qcm_data.chip_layout.ChipLayout.rotate_layout") | Clockwise rotation of coordinates. |

*classmethod* from_chip_design_record(*record*)  
Construct the chip layout from a raw chip design record.

Parameters:  
**record** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")) – The chip design record as returned by the executor.

Returns:  
The corresponding chip layout.

Return type:  
[*ChipLayout*](#exa.common.qcm_data.chip_layout.ChipLayout "exa.common.qcm_data.chip_layout.ChipLayout")

normalize_coordinates(*min_spacing*)  
Rescale component coordinates

Rescale all component coordinates so that the minimum distance between 2 components is min_spacing

Parameters:  
**min_spacing** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Return type:  
*None*

rotate_layout(*angle=45*)  
Clockwise rotation of coordinates.

Parameters:  
**angle** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Return type:  
*None*

move_origin()  
Changes the origin of the Cartesian coordinate system such that all elements move into the first quadrant.

If there is a component with coordinates (x_min, y_min) it will move to (0, 0).

Return type:  
*None*

get_coordinates(*component*)  
Get the coordinates for the given component.

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the component.

Returns:  
The 2D cartesian coordinates.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

get_all_qubit_coordinates()  
Get the coordinates for all qubits.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]

get_angle(*component*)  
Get the angle for the given component.

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the component.

Returns:  
The angle of the component.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

get_all_qubit_angles()  
Get the angles for all qubits.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of exa.common.qcm_data.chip_layout.ChipLayout](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-4802cbe624f5b4bacded5041f19e1fbda5598296.png)
