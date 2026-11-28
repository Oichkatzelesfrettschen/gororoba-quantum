"""Contracts of the tile-template pin of live_run.py and its source-manifest and admission-guard companions.

A group named in live_run.TILE_TEMPLATES compiles from one embedding of its logical-edge template, so every circuit
the group routes keeps the template's couplers and the replica search, which moves the compiled pattern, keeps them in
every placed region (docs/design/pathion-kernel-map-orientation-merged.md, "Pin of the layout").
"""

from __future__ import annotations

from types import SimpleNamespace

import rustworkx as rx
from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap, Target

import live_run

GROUP = "pathion_kernel_map_orientation_merged"
TEMPLATE = ((0, 1), (0, 2), (0, 3), (1, 4), (2, 5))


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require[T](value: T | None, message: str) -> T:
    if value is None:
        raise AssertionError(message)
    return value


def _graph(coupling: CouplingMap) -> rx.PyGraph:
    graph = rx.PyGraph()
    graph.add_nodes_from(range(coupling.size()))
    graph.add_edges_from_no_data(sorted({tuple(sorted(edge)) for edge in coupling.get_edges()}))
    return graph


def test_the_merged_group_names_the_spider_template() -> None:
    _expect(live_run.TILE_TEMPLATES.get(GROUP) == TEMPLATE, "the merged group lacks its spider(2,2,1) template")
    _expect(
        set(live_run.TILE_TEMPLATES) == {GROUP},
        "a tile template for another group would move that group's compile and records",
    )


def test_template_layout_maps_every_template_edge_onto_a_coupler() -> None:
    graph = _graph(CouplingMap.from_heavy_hex(5, bidirectional=False))
    found = live_run.tile_template_layout(graph, TEMPLATE, frozenset())
    layout = _require(found, "no six-qubit embedding on a heavy-hex lattice")
    _expect(len(set(layout)) == 6, f"the embedding repeats a qubit: {layout}")
    for first, second in TEMPLATE:
        _expect(graph.has_edge(layout[first], layout[second]), f"wires {first} and {second} sit on no coupler")
    _expect(graph.has_edge(layout[1], layout[4]), "wires 1 and 4 are not adjacent")
    _expect(layout == live_run.tile_template_layout(graph, TEMPLATE, frozenset()), "the embedding is not deterministic")


def test_template_layout_avoids_excluded_qubits_and_refuses_a_region_without_an_embedding() -> None:
    graph = _graph(CouplingMap.from_heavy_hex(5, bidirectional=False))
    first = _require(live_run.tile_template_layout(graph, TEMPLATE, frozenset()), "no embedding")
    moved = live_run.tile_template_layout(graph, TEMPLATE, frozenset(first))
    _expect(moved is not None and not set(moved) & set(first), f"the embedding {moved} reuses an excluded qubit")
    path = rx.PyGraph()
    path.add_nodes_from(range(12))
    path.add_edges_from_no_data([(i, i + 1) for i in range(11)])
    _expect(
        live_run.tile_template_layout(path, TEMPLATE, frozenset()) is None,
        "a path graph holds no spider and must admit no placement",
    )


def test_missing_template_edges_name_the_couplers_a_compiled_group_leaves_unused() -> None:
    layout = [10, 11, 12, 13, 14, 15]
    used = QuantumCircuit(16)
    for first, second in TEMPLATE:
        used.cz(layout[first], layout[second])
    _expect(live_run.tile_missing_edges([used], layout, TEMPLATE) == [], "a circuit on every template edge is complete")
    partial = QuantumCircuit(16)
    for first, second in TEMPLATE[:3]:
        partial.cz(layout[first], layout[second])
    _expect(
        live_run.tile_missing_edges([partial], layout, TEMPLATE) == [(1, 4), (2, 5)],
        "the unused template edges are not named",
    )
    _expect(live_run.tile_missing_edges([partial, used], layout, TEMPLATE) == [], "the edges of the whole group count")


def test_source_manifest_binds_the_merged_module() -> None:
    _expect(
        "pathion_kernel_map_orientation_merged.py" in live_run.EXPERIMENT_SOURCE_MANIFEST,
        "the source manifest omits the merged module",
    )


def test_record_fields_state_the_template_and_flag_a_region_off_the_couplers() -> None:
    coupling = CouplingMap.from_heavy_hex(5, bidirectional=False)
    target = Target.from_configuration(basis_gates=["cz", "rz", "sx"], coupling_map=coupling)
    graph = _graph(coupling)
    layout = _require(live_run.tile_template_layout(graph, TEMPLATE, frozenset()), "no embedding")
    broken = list(layout)
    broken[4] = next(q for q in range(coupling.size()) if q not in layout and not graph.has_edge(q, layout[1]))
    replicas = [
        SimpleNamespace(index=0, mapping={q: q for q in layout}),
        SimpleNamespace(index=1, mapping=dict(zip(layout, broken, strict=True))),
    ]
    choice = SimpleNamespace(
        snap=SimpleNamespace(backend=SimpleNamespace(target=target)), layout=layout, replicas=replicas
    )
    fields = live_run._tile_template_fields(choice, TEMPLATE)  # type: ignore[arg-type]
    _expect(fields["edges"] == [list(edge) for edge in TEMPLATE], f"the template is not recorded: {fields}")
    _expect(
        [a["template_on_couplers"] for a in fields["assignments"]] == [True, False],
        f"the per-region coupler flags are wrong: {fields['assignments']}",
    )
    _expect(fields["assignments"][1]["initial_layout"] == broken, "the region's assignment is not recorded")
