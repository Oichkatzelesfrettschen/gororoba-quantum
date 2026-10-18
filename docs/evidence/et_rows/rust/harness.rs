//! Execute immutable canonical modules and export their complete ordered cell grids.
#[allow(dead_code)]
mod cdp;
#[allow(dead_code)]
mod strutted_et;

fn main() {
    for dimension in [16usize, 32, 64, 128] {
        for left in 0..dimension {
            for right in 0..dimension {
                let (index, sign) = cdp::cdp_signed_product(left, right);
                println!("B\t{dimension}\t{left}\t{right}\t{index}\t{sign}");
            }
        }
        for strut in 1..dimension / 2 {
            let table = strutted_et::create_strutted_et(dimension.ilog2() as usize, strut);
            for (row_index, row) in table.tone_row.lo.iter().enumerate() {
                println!("L\t{dimension}\t{strut}\t{row_index}\t{row}");
                for (column_index, column) in table.tone_row.lo.iter().enumerate() {
                    let cell = table.cells[row_index][column_index];
                    let occupied = cell.is_some_and(|entry| entry.is_dmz);
                    let value = cell.filter(|entry| entry.is_dmz).map_or(0, |entry| entry.emanation_value);
                    println!("C\t{dimension}\t{strut}\t{row}\t{column}\t{}\t{value}", u8::from(occupied));
                }
            }
        }
    }
}
