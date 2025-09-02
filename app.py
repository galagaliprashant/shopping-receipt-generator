import json
import sys
from decimal import Decimal
from pathlib import Path

import streamlit as st

# Ensure local repo root is importable in hosted environments
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from receipt_generator import load_items_from_json, build_receipt


st.set_page_config(page_title="Receipt Generator", page_icon="🧾", layout="centered")
st.title("🧾 Shopping Receipt Generator")
st.write("Upload a JSON order and generate a receipt.")

with st.sidebar:
    st.header("Settings")
    tax = st.text_input("Tax rate (decimal)", value="0.088")
    currency = st.text_input("Currency symbol", value="$")

uploaded = st.file_uploader("Upload items JSON", type=["json"])

example = {
    "items": [
        {"description": "Lovely Loveseat", "price": "254.00", "quantity": 1},
        {"description": "Luxurious Lamp",   "price": "52.15",  "quantity": 1}
    ]
}

with st.expander("See JSON schema and example", expanded=False):
    st.code(json.dumps(example, indent=2), language="json")

if uploaded is not None:
    try:
        data = json.loads(uploaded.read().decode("utf-8"))
        tmp = Path("uploaded_items.json")
        tmp.write_text(json.dumps(data), encoding="utf-8")
        items = load_items_from_json(tmp)
        receipt = build_receipt(items, Decimal(str(tax)), currency)
        st.subheader("Receipt")
        st.code(receipt)
        st.download_button("Download receipt.txt", receipt, file_name="receipt.txt")
    except Exception as e:
        st.error(f"Failed to generate receipt: {e}")
else:
    st.info("Upload a JSON file to generate the receipt.")


