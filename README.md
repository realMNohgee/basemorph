# basemorph 🔢
![CI](https://github.com/realMNohgee/basemorph/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Base converter and bitwise operations CLI.** Zero dependencies, pure Python stdlib.

> Part of the Systems Programming suite — number manipulation for embedded, reverse engineering, and education.

## One tool, many domains

| Domain | What basemorph does for you |
|---|---|
| 💻 **Systems Programming** | Convert between hex, binary, octal, decimal |
| 🔍 **Reverse Engineering** | Inspect bit patterns and number properties |
| 🔧 **Embedded** | Bitwise AND/OR/XOR/NOT/SHIFT operations |
| 🎓 **Education** | Learn number systems with pretty output |
| 🤖 **Agentic AI** | Programmatic number conversion in agent pipelines |

## Install

```bash
git clone git@github.com:realMNohgee/basemorph.git
cd basemorph
python3 basemorph.py --help
```

## Quick start

```bash
# Auto-detect input format (0x, 0b, 0o prefixes)
python3 basemorph.py convert 0xFF
python3 basemorph.py convert 0b1010
python3 basemorph.py convert 42

# Override base detection
python3 basemorph.py convert 1111 --from 2 --to 10

# Show number info (binary, hex, ASCII, bit count)
python3 basemorph.py info 65

# Bitwise operations
python3 basemorph.py bitwise 0xFF AND 0x0F
python3 basemorph.py bitwise 0b1100 XOR 0b1010
python3 basemorph.py bitwise 42 NOT

# JSON output for pipelines
python3 basemorph.py info 255 --format json
```

Support for negative numbers with two's complement binary display.

## License

MIT — see [LICENSE](LICENSE).

---

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)** — the open, agent-agnostic marketplace for AI agent tools.
