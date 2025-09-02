"""Shopping receipt generator with CLI, JSON input, and Decimal math.

Usage examples:
  python3 receipt_generator.py --items sample_order.json --tax 0.088
  python3 receipt_generator.py --items sample_order.json --currency "₹" --output receipt.txt

JSON schema for --items:
{
  "items": [
    {"description": "Lovely Loveseat", "price": "254.00", "quantity": 1},
    {"description": "Luxurious Lamp",   "price": "52.15",  "quantity": 1}
  ]
}
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import List, Optional


# Configure Decimal for currency-safe math
getcontext().prec = 28


@dataclass
class LineItem:
    description: str
    price: Decimal
    quantity: int = 1

    def line_total(self) -> Decimal:
        return (self.price * Decimal(self.quantity)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_items_from_json(json_path: Path) -> List[LineItem]:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    raw_items = data.get("items", [])
    items: List[LineItem] = []
    for entry in raw_items:
        description = str(entry.get("description", "Item"))
        price = Decimal(str(entry.get("price", "0")))
        quantity = int(entry.get("quantity", 1))
        items.append(LineItem(description=description, price=price, quantity=quantity))
    return items


def format_money(value: Decimal, currency_symbol: str) -> str:
    return f"{currency_symbol}{value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"


def build_receipt(items: List[LineItem], tax_rate: Decimal, currency_symbol: str) -> str:
    lines: List[str] = []
    lines.append("Items:")
    subtotal = Decimal("0")
    for item in items:
        total = item.line_total()
        lines.append(
            f"- {item.description} x {item.quantity} @ {format_money(item.price, currency_symbol)} = {format_money(total, currency_symbol)}"
        )
        subtotal += total

    tax = (subtotal * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    grand_total = (subtotal + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    lines.append("")
    lines.append(f"Subtotal: {format_money(subtotal, currency_symbol)}")
    lines.append(f"Tax ({(tax_rate*Decimal('100')).normalize()}%): {format_money(tax, currency_symbol)}")
    lines.append(f"Total: {format_money(grand_total, currency_symbol)}")

    return "\n".join(lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a shopping receipt from JSON items.")
    parser.add_argument(
        "--items",
        required=True,
        help="Path to JSON file with items (see README for schema)",
    )
    parser.add_argument(
        "--tax",
        default="0.088",
        help="Sales tax rate as decimal (e.g., 0.088 for 8.8%)",
    )
    parser.add_argument(
        "--currency",
        default="$",
        help="Currency symbol to prefix amounts (default: $)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write the receipt. If omitted, prints to stdout.",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    items_path = Path(args.items)
    if not items_path.exists():
        raise SystemExit(f"Items file not found: {items_path}")

    items = load_items_from_json(items_path)
    tax_rate = Decimal(str(args.tax))
    receipt = build_receipt(items=items, tax_rate=tax_rate, currency_symbol=args.currency)

    if args.output:
        Path(args.output).write_text(receipt + "\n", encoding="utf-8")
        print(f"Receipt written to {args.output}")
    else:
        print(receipt)


if __name__ == "__main__":
    main()
