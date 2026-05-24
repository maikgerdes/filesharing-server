"""Utility to read a Word (.docx) table and return it as a Python dict.

The module exposes `read_word_table_as_dict` which reads a table from a
Word document and maps one column to another as key -> value.

Usage:
    from webserver.read_word2 import read_word_table_as_dict

    d = read_word_table_as_dict("/path/to/doc.docx", key_col=0, value_col=1)
    # or using header names (if the table has a header row):
    d = read_word_table_as_dict("/path/to/doc.docx", key_col="Schlüssel", value_col="Wert", header=True)

Requirements: python-docx (add to requirements.txt if not present).
"""
from typing import Union, Dict, Any, List

from docx import Document


def _get_column_indices_from_header(header_cells: List[str], col: Union[int, str]) -> int:
    if isinstance(col, int):
        return col
    try:
        return header_cells.index(col)
    except ValueError:
        raise ValueError(f"Header column '{col}' not found in table headers: {header_cells}")


def read_word_table_as_dict(
    docx_path: str,
    key_col: Union[int, str],
    value_col: Union[int, str],
    header: bool = True,
    table_index: int = 0,
    strip: bool = True,
    ignore_empty: bool = True,
) -> Dict[Any, Any]:
    """Read a table from a .docx file and return a dict mapping key->value.

    Parameters:
    - docx_path: path to the .docx file
    - key_col: column index (int) or header name (str) to use as keys
    - value_col: column index (int) or header name (str) to use as values
    - header: whether the first row is a header (default True). If True and
      key_col/value_col are strings, the header row is used to resolve indices.
    - table_index: index of the table in the document (default 0)
    - strip: strip whitespace from cell text
    - ignore_empty: skip rows where the key is empty

    Returns:
    A dict mapping keys to values. If duplicate keys appear, the last
    occurrence wins.
    """
    doc = Document(docx_path)
    try:
        table = doc.tables[table_index]
    except IndexError:
        raise IndexError(f"No table at index {table_index} in document {docx_path}")

    rows = list(table.rows)
    if not rows:
        return {}

    start_row = 0
    header_cells_text: List[str] = []
    if header:
        hdr = rows[0]
        header_cells_text = [c.text.strip() if strip else c.text for c in hdr.cells]
        start_row = 1

    # Resolve column indices
    if isinstance(key_col, str) and not header:
        raise ValueError("key_col is a string but header=False; cannot resolve column name")
    if isinstance(value_col, str) and not header:
        raise ValueError("value_col is a string but header=False; cannot resolve column name")

    if header and isinstance(key_col, str):
        key_idx = _get_column_indices_from_header(header_cells_text, key_col)
    else:
        key_idx = int(key_col)

    if header and isinstance(value_col, str):
        value_idx = _get_column_indices_from_header(header_cells_text, value_col)
    else:
        value_idx = int(value_col)

    result: Dict[Any, Any] = {}
    for r in rows[start_row:]:
        cells = r.cells
        # Some rows may have fewer cells than expected; guard against that
        if key_idx >= len(cells) or value_idx >= len(cells):
            # skip malformed row
            continue
        raw_key = cells[key_idx].text
        raw_value = cells[value_idx].text
        k = raw_key.strip() if strip else raw_key
        v = raw_value.strip() if strip else raw_value
        if ignore_empty and (k is None or str(k).strip() == ""):
            continue
        result[k] = v

    return result


if __name__ == "__main__":
    # Quick local test example (not executed in import)
    import sys

    if len(sys.argv) < 4:
        print("Usage: python read_word2.py <docx_path> <key_col> <value_col> [header=1]")
    else:
        path = sys.argv[1]
        try:
            kc = int(sys.argv[2])
        except ValueError:
            kc = sys.argv[2]
        try:
            vc = int(sys.argv[3])
        except ValueError:
            vc = sys.argv[3]
        hdr = True if len(sys.argv) < 5 or sys.argv[4] not in ("0", "False", "false") else False
        d = read_word_table_as_dict(path, kc, vc, header=hdr)
        print(d)
