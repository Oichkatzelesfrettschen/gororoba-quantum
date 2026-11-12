"""Recompute selected-array bounds for the memory-bounded W8 degree-6, N=19 route.

This is not an RSS forecast: Python objects, sparse multiplication tables, allocator state and file cache are outside
the model. It is an upper bound for the named dense arrays, derived from the retained v11 preflight terms and the
retained standard-monomial degree counts. Product and closure stages are reported separately because the streamed
generator operator is released before the echelon bases are constructed.

The products stage counts the two adjacent operator layers, the retained uint16 product rows and the walk and tile
temporaries (`streamed_chunk_bytes` of fiber_rank_v14.py). The accumulate line of `streamed_generator_product` adds
10 bytes per prefix row element, `10 * prefix_rows * block_max`, where `prefix_rows` is the largest row count of one
generator call; that count comes from the receipt's wanted tuples (`streamed_prefix_peak`), which the retained v11
terms do not carry, so `model(prefix_peak_rows=None)` leaves the term out and reports the largest count under which
the stage still fits. The closure stage adds the panel transient of one compact insertion
(`insert_panel_bytes` of modular_echelon_compact.py).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

QUOTIENT_DIMENSION = 235_543
BLOCKS = 4
DEGREE_COUNTS = [
    1,
    7,
    28,
    84,
    209,
    455,
    896,
    1_632,
    2_793,
    4_543,
    7_084,
    10_652,
    15_457,
    21_560,
    28_609,
    35_448,
    39_922,
    38_752,
    27_411,
]

# Exact terms printed by the retained v11 preflight. Its generator blocks use float64, so dividing by eight gives
# sum_b c_b^2. Its product-row term is four times the compact route's two uint16 copies.
V11_GENERATOR_BLOCK_BYTES = 110_961_608_648
V11_PRODUCT_ROW_BYTES = 14_953_585_152
CHUNK = 64
# Constants of modular_echelon_compact.py and fiber_rank_v14.py that the transient terms use.
COMPACT_COLS = 1024
COMPACT_INNER = 4096
ROW_TILE = 128


def insert_panel_bytes(block_size: int, chunk: int) -> int:
    """`modular_echelon_compact.insert_panel_bytes`: panel and coefficient transients of one compact insertion."""
    tiles = 8 * (ROW_TILE * COMPACT_INNER + COMPACT_INNER * COMPACT_COLS + 3 * ROW_TILE * COMPACT_COLS)
    return 2 * COMPACT_COLS * (3 * block_size + chunk) + 4 * block_size * chunk + tiles


def streamed_chunk_bytes(chunk: int, widest: int) -> int:
    """`fiber_rank_v14.streamed_chunk_bytes`: walk temporaries and the float64 tiles of one tiled product."""
    return 4 * 8 * chunk * widest + 8 * (chunk * 4096 + 4096 * 1024 + 3 * chunk * 1024)


def model(prefix_peak_rows: int | None = None) -> dict[str, object]:
    sum_squares = V11_GENERATOR_BLOCK_BYTES // 8
    mean = QUOTIENT_DIMENSION / BLOCKS
    squared_deviation = sum_squares - QUOTIENT_DIMENSION**2 / BLOCKS
    # If one deviation is x, the other three sum to -x and their squared sum is at least x^2/3. Hence the total
    # squared deviation is at least 4x^2/3. The ceiling is a valid integral upper bound for every block size.
    block_max = math.ceil(mean + math.sqrt(3 * squared_deviation / 4))
    adjacent_rows = max(a + b for a, b in zip(DEGREE_COUNTS[:-1], DEGREE_COUNTS[1:], strict=True))
    streamed_operator = 2 * adjacent_rows * block_max
    product_rows = V11_PRODUCT_ROW_BYTES // 4
    compact_echelon = sum_squares // 2
    closure_temporaries = 3 * 8 * CHUNK * block_max
    insert_panels = insert_panel_bytes(block_max, CHUNK)
    walk_temporaries = streamed_chunk_bytes(CHUNK, block_max)
    product_stage = streamed_operator + product_rows + walk_temporaries
    loop_arrays = None if prefix_peak_rows is None else 10 * prefix_peak_rows * block_max
    if loop_arrays is not None:
        product_stage += loop_arrays
    closure_stage = product_rows + compact_echelon + closure_temporaries + insert_panels
    memory_limit = 16 * 2**30
    # Largest prefix row count whose accumulate-line arrays still leave the products stage inside the limit.
    fit_rows = max(0, (memory_limit - (product_stage - (loop_arrays or 0))) // (10 * block_max))
    return {
        "schema": "a5-w8-n19-memory-model-v1",
        "inputs": {
            "quotient_dimension": QUOTIENT_DIMENSION,
            "blocks": BLOCKS,
            "sum_block_squares": sum_squares,
            "degree_counts": DEGREE_COUNTS,
            "v11_generator_block_bytes": V11_GENERATOR_BLOCK_BYTES,
            "v11_product_row_bytes": V11_PRODUCT_ROW_BYTES,
            "chunk": CHUNK,
            "prefix_peak_rows": prefix_peak_rows,
        },
        "derived": {
            "maximum_block_size_upper_bound": block_max,
            "maximum_adjacent_degree_rows": adjacent_rows,
            "full_uint16_generator_operator_bytes": V11_GENERATOR_BLOCK_BYTES // 4,
            "streamed_operator_layers_bytes": streamed_operator,
            "uint16_product_rows_bytes": product_rows,
            "compact_echelon_ceiling_bytes": compact_echelon,
            "closure_chunk_temporaries_bytes": closure_temporaries,
            "compact_insert_panels_bytes": insert_panels,
            "streamed_walk_temporaries_bytes": walk_temporaries,
            "streamed_loop_arrays_bytes": loop_arrays,
            "max_prefix_rows_that_fit": fit_rows,
        },
        "stage_peaks": {
            "products_selected_arrays_bytes": product_stage,
            "closure_selected_arrays_bytes": closure_stage,
            "selected_array_peak_bytes": max(product_stage, closure_stage),
            "selected_array_headroom_at_16_gib_bytes": memory_limit - max(product_stage, closure_stage),
        },
        "streamed_loop_arrays_status": (
            "included"
            if loop_arrays is not None
            else "hypothesis: the products stage omits the accumulate-line arrays of streamed_generator_product, "
            "10 * prefix_rows * block_max bytes (contribution plus two uint32 temporaries per element); the figure "
            "fits 16 GiB only when the largest per-call prefix row count of the N = 19 receipt is at most "
            "max_prefix_rows_that_fit. fiber_rank_v14.py reports the term streamed_loop_arrays "
            "(10 * prefix_rows * block size) in preflight_terms once the receipt is loaded and refuses a run whose "
            "stage exceeds --max-gb; "
            "that preflight, or an instrumented run, settles it."
        ),
        "boundary": (
            "Upper bounds for the named dense arrays only; sparse tables, Python objects, the flint entry lists of "
            "each insertion, allocator state and file cache require an instrumented acceptance run. A nonpositive "
            "headroom or measured process-group RSS above 16 GiB falsifies this host route."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    text = json.dumps(model(), indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
