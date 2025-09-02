import json
import sys
from decimal import Decimal
from pathlib import Path

import streamlit as st
import runpy

# Ensure local repo root is importable in hosted environments
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Try normal import, then fall back to loading by path
try:
    from receipt_generator import load_items_from_json, build_receipt  # type: ignore
except Exception:  # pragma: no cover
    module_path = CURRENT_DIR / "receipt_generator.py"
    module_ns = runpy.run_path(str(module_path))
    load_items_from_json = module_ns["load_items_from_json"]
    build_receipt = module_ns["build_receipt"]


st.set_page_config(page_title="Receipt Generator", page_icon="🧾", layout="centered")
st.title("🧾 Shopping Receipt Generator")
st.write("Upload a JSON order or manually enter items to generate a receipt.")

with st.sidebar:
    st.header("Settings")
    tax = st.text_input("Tax rate (decimal)", value="0.088")
    currency = st.text_input("Currency symbol", value="$")

tab_upload, tab_manual = st.tabs(["Upload JSON", "Enter items manually"])

with tab_upload:
    uploaded = st.file_uploader("Upload items JSON", type=["json"])

example = {
    "items": [
        {"description": "Lovely Loveseat", "price": "254.00", "quantity": 1},
        {"description": "Luxurious Lamp",   "price": "52.15",  "quantity": 1}
    ]
}

with st.expander("See JSON schema and example", expanded=False):
    st.code(json.dumps(example, indent=2), language="json")

with tab_upload:
    if uploaded is not None:
        try:
            @st.cache_data(show_spinner=False)
            def _parse_json_bytes(b: bytes):
                return json.loads(b.decode("utf-8"))

            data = _parse_json_bytes(uploaded.read())
            # Build items in-memory to avoid file I/O
            items = []
            for entry in data.get("items", []):
                items.append({
                    "description": entry.get("description", "Item"),
                    "price": str(entry.get("price", "0")),
                    "quantity": int(entry.get("quantity", 1)),
                })
            tmp = Path("_mem.json")
            tmp.write_text(json.dumps({"items": items}), encoding="utf-8")
            items = load_items_from_json(tmp)
            receipt = build_receipt(items, Decimal(str(tax)), currency)
            st.subheader("Receipt")
            st.code(receipt)
            st.download_button("Download receipt.txt", receipt, file_name="receipt.txt")
        except Exception as e:
            st.error(f"Failed to generate receipt: {e}")
    else:
        st.info("Upload a JSON file to generate the receipt.")

with tab_manual:
    st.write("Build a receipt by entering items below.")
    if "rows" not in st.session_state:
        st.session_state.rows = [
            {"description": "Lovely Loveseat", "price": "254.00", "quantity": 1},
            {"description": "Luxurious Lamp", "price": "52.15", "quantity": 1},
        ]

    def add_row():
        st.session_state.rows.append({"description": "", "price": "0.00", "quantity": 1})

    def clear_rows():
        st.session_state.rows = [{"description": "", "price": "0.00", "quantity": 1}]

    c1, c2 = st.columns([1,1])
    with c1:
        st.button("➕ Add item", on_click=add_row)
    with c2:
        st.button("🧹 Clear", on_click=clear_rows)

    manual_items = []
    for idx, row in enumerate(st.session_state.rows):
        with st.expander(f"Item {idx+1}", expanded=True):
            desc = st.text_input("Description", value=row["description"], key=f"desc_{idx}")
            pcol, qcol = st.columns([1,1])
            with pcol:
                price_str = st.text_input("Unit price", value=row["price"], key=f"price_{idx}")
            with qcol:
                qty = st.number_input("Quantity", min_value=1, value=int(row["quantity"]), step=1, key=f"qty_{idx}")
            # Persist back to session
            row["description"], row["price"], row["quantity"] = desc, price_str, qty
            manual_items.append({"description": desc, "price": price_str, "quantity": qty})

    if st.button("Generate receipt", type="primary"):
        try:
            # Convert to JSON-like dict and reuse core loader for validation
            tmp = Path("manual_items.json")
            tmp.write_text(json.dumps({"items": manual_items}), encoding="utf-8")
            items = load_items_from_json(tmp)
            receipt = build_receipt(items, Decimal(str(tax)), currency)
            st.subheader("Receipt")
            st.code(receipt)
            st.download_button("Download receipt.txt", receipt, file_name="receipt.txt")
        except Exception as e:
            st.error(f"Failed to generate receipt: {e}")


