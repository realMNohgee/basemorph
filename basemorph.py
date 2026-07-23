#!/usr/bin/env python3
"""basemorph — Base converter and bitwise operations CLI.

Convert numbers between bases (hex, binary, octal, decimal), perform
bitwise operations, and inspect number properties — all from a single
zero-dependency tool.

Domains: Systems Programming · Embedded · Reverse Engineering · Education · Agentic AI.
"""
from __future__ import annotations
import argparse
import json
import sys


def detect_base(value: str) -> tuple[int, str]:
    """Auto-detect the base of a number from its prefix.

    Returns (base, cleaned_value).
    """
    v = value.strip()
    if v.startswith("0x") or v.startswith("0X"):
        return 16, v[2:]
    elif v.startswith("0b") or v.startswith("0B"):
        return 2, v[2:]
    elif v.startswith("0o") or v.startswith("0O"):
        return 8, v[2:]
    else:
        return 10, v


def parse_number(value: str, base: int | None = None) -> int:
    """Parse a number string into an integer, with optional base override."""
    if base is not None:
        return int(value, base)
    detected_base, clean = detect_base(value)
    return int(clean, detected_base)


def to_binary(n: int, bits: int | None = None) -> str:
    """Convert integer to binary string representation."""
    if n >= 0:
        b = bin(n)[2:]
        if bits:
            b = b.zfill(bits)
        return "0b" + b
    else:
        # Two's complement
        if bits is None:
            bits = max(8, (n.bit_length() + 1 + 7) // 8 * 8)
        mask = (1 << bits) - 1
        twos = n & mask
        b = bin(twos)[2:].zfill(bits)
        return "0b" + b


def to_hex(n: int) -> str:
    """Convert integer to hex string."""
    if n >= 0:
        return hex(n)
    else:
        return "-" + hex(abs(n))


def to_octal(n: int) -> str:
    """Convert integer to octal string."""
    if n >= 0:
        return oct(n)
    else:
        return "-" + oct(abs(n))


def format_info_text(n: int, args: argparse.Namespace) -> str:
    """Format number info as text."""
    lines: list[str] = []
    bits = max(8, (abs(n).bit_length() + 7) // 8 * 8)
    lines.append(f"  Decimal    : {n}")
    lines.append(f"  Hex        : {to_hex(n)}")
    lines.append(f"  Binary     : {to_binary(n, bits)}")
    lines.append(f"  Octal      : {to_octal(n)}")
    lines.append(f"  Bit count  : {abs(n).bit_length()}")
    lines.append(f"  Sign       : {'negative' if n < 0 else 'positive'}")
    if 32 <= n <= 126:
        lines.append(f"  ASCII      : '{chr(n)}'")
    lines.append(f"  UTF-8 char : {chr(n) if 0 <= n <= 0x10FFFF else 'N/A'}")
    return "\n".join(lines)


def format_info_json(n: int) -> str:
    """Format number info as JSON."""
    bits = max(8, (abs(n).bit_length() + 7) // 8 * 8)
    data = {
        "input": n,
        "decimal": n,
        "hex": to_hex(n),
        "binary": to_binary(n, bits),
        "octal": to_octal(n),
        "bit_count": abs(n).bit_length(),
        "sign": "negative" if n < 0 else "positive",
    }
    if 32 <= n <= 126:
        data["ascii"] = chr(n)
    if 0 <= n <= 0x10FFFF:
        data["utf8_char"] = chr(n)
    return json.dumps(data, indent=2)


def format_convert_text(value: str, from_base: int | None, to_base: int | None, n: int) -> str:
    """Format conversion result as text."""
    lines: list[str] = []
    if from_base is not None:
        lines.append(f"Input: {value} (base {from_base})")
    else:
        detected_base, _ = detect_base(value)
        lines.append(f"Input: {value} (auto-detected base {detected_base})")
    lines.append("")
    lines.append("Conversions:")
    for base_name, base_val, prefix in [
        ("Decimal", 10, ""),
        ("Hex", 16, "0x"),
        ("Binary", 2, "0b"),
        ("Octal", 8, "0o"),
    ]:
        if to_base is not None and base_val != to_base:
            continue
        if base_val == 16:
            val = to_hex(n)
        elif base_val == 8:
            val = to_octal(n)
        elif base_val == 2:
            val = to_binary(n, None)
        else:
            val = str(n)
        lines.append(f"  {base_name:<10}: {val}")
    return "\n".join(lines)


def format_convert_json(value: str, from_base: int | None, to_base: int | None, n: int) -> str:
    """Format conversion result as JSON."""
    detected_base, _ = detect_base(value)
    result: dict = {
        "input": value,
        "auto_detected_base": detected_base if from_base is None else None,
        "from_base": from_base,
        "to_base": to_base,
        "decimal": n,
        "hex": to_hex(n),
        "binary": to_binary(n, None),
        "octal": to_octal(n),
    }
    if from_base is not None:
        del result["auto_detected_base"]
    return json.dumps(result, indent=2)


def cmd_convert(args: argparse.Namespace) -> int:
    """Convert a number between bases."""
    try:
        n = parse_number(args.value, args.from_base)
    except ValueError as e:
        print(f"Error: Cannot parse '{args.value}': {e}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(format_convert_json(args.value, args.from_base, args.to_base, n))
    else:
        print(format_convert_text(args.value, args.from_base, args.to_base, n))

    return 0


BITWISE_OPS: dict[str, str] = {
    "AND": "&",
    "OR": "|",
    "XOR": "^",
    "NOT": "~",
    "LSHIFT": "<<",
    "RSHIFT": ">>",
}


def cmd_bitwise(args: argparse.Namespace) -> int:
    """Perform bitwise operations."""
    op = args.op.upper()
    if op not in BITWISE_OPS:
        print(f"Error: Unknown operation '{args.op}'. Use: {', '.join(BITWISE_OPS)}", file=sys.stderr)
        return 1

    try:
        a = parse_number(args.a, None)
    except ValueError as e:
        print(f"Error: Cannot parse operand A '{args.a}': {e}", file=sys.stderr)
        return 1

    if op == "NOT":
        result = ~a
        b_val = None
    else:
        try:
            b = parse_number(args.b, None)
        except ValueError as e:
            print(f"Error: Cannot parse operand B '{args.b}': {e}", file=sys.stderr)
            return 1
        b_val = b
        op_symbol = BITWISE_OPS[op]
        if op == "AND":
            result = a & b
        elif op == "OR":
            result = a | b
        elif op == "XOR":
            result = a ^ b
        elif op == "LSHIFT":
            result = a << b
        elif op == "RSHIFT":
            result = a >> b
        else:
            result = 0

    if args.format == "json":
        output: dict = {
            "operation": op,
            "a": a,
            "a_hex": to_hex(a),
            "a_binary": to_binary(a, None),
        }
        if b_val is not None:
            output["b"] = b_val
            output["b_hex"] = to_hex(b_val)
            output["b_binary"] = to_binary(b_val, None)
        output["result"] = result
        output["result_hex"] = to_hex(result)
        output["result_binary"] = to_binary(result, None)
        output["result_decimal"] = result
        print(json.dumps(output, indent=2))
    else:
        print(f"  A        : {a} ({to_hex(a)} / {to_binary(a, None)})")
        if b_val is not None:
            print(f"  B        : {b_val} ({to_hex(b_val)} / {to_binary(b_val, None)})")
        print(f"  Operation: {op}")
        print(f"  Result   : {result} ({to_hex(result)} / {to_binary(result, None)})")

    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Show detailed information about a number."""
    try:
        n = parse_number(args.value, None)
    except ValueError as e:
        print(f"Error: Cannot parse '{args.value}': {e}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(format_info_json(n))
    else:
        print(format_info_text(n, args))

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="basemorph",
        description="Base converter and bitwise operations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    s_conv = sub.add_parser("convert", parents=[common], help="Convert a number between bases")
    s_conv.add_argument("value", help="Number to convert (prefixes: 0x, 0b, 0o, or plain decimal)")
    s_conv.add_argument("--from", dest="from_base", type=int, choices=[2, 8, 10, 16],
                        help="Override auto-detected base")
    s_conv.add_argument("--to", dest="to_base", type=int, choices=[2, 8, 10, 16],
                        help="Output base (default: show all)")
    s_conv.set_defaults(func=cmd_convert)

    s_bit = sub.add_parser("bitwise", parents=[common], help="Perform bitwise operations")
    s_bit.add_argument("a", help="First operand")
    s_bit.add_argument("op", help="Operation: AND, OR, XOR, NOT, LSHIFT, RSHIFT")
    s_bit.add_argument("b", nargs="?", default=None, help="Second operand (not needed for NOT)")
    s_bit.set_defaults(func=cmd_bitwise)

    s_info = sub.add_parser("info", parents=[common], help="Show number information")
    s_info.add_argument("value", help="Number to inspect")
    s_info.set_defaults(func=cmd_info)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
