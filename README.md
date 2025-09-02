# Shopping Receipt Generator

A CLI tool to generate receipts from JSON input using currency-safe Decimal math.

## Quick start
```bash
python3 receipt_generator.py --items sample_order.json --tax 0.088
```

## JSON schema
```json
{
  "items": [
    {"description": "string", "price": "decimal string", "quantity": integer}
  ]
}
```

## Examples
```bash
# Print to stdout
python3 receipt_generator.py --items sample_order.json --tax 0.088

# Write to a file with custom currency
python3 receipt_generator.py --items sample_order.json --tax 0.088 --currency "₹" --output receipt.txt
```

## Notes
- Python 3.8+
- No external dependencies
- Uses Decimal for money-safe rounding (ROUND_HALF_UP)
