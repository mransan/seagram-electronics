# Seagram Electronics

This repository collects all information regarding the current and planned
electronics for the Seagram sailing yacht.

## Directory Structure

- `parts/`: Specifications and integration guides for hardware components and
  gateways.
  - [`iTC-5`](parts/iTC-5.md): Raymarine iTC-5 Instrument Transducer Converter
    (includes sensor wiring requirements and S2G course computer caveats).
  - [`M81190`](parts/M81190.md): Raymarine Fluxgate Compass Transducer (wiring,
    S2G integration, SeaTalk1 datagrams, and calibration).
  - [`YDNU-02`](parts/YDNU-02.md): Yacht Devices NMEA 2000 to USB Gateway.
  - [`YDWG-02`](parts/YDWG-02.md): Yacht Devices NMEA 2000 to Wi-Fi Gateway.
- `scripts/`: Development and maintenance helper scripts.
  - `format_markdown.py`: Formatter enforcing line length limits on markdown.

## Markdown Formatting

All markdown documentation must adhere to the 80-character line length limit.
Run `scripts/format_markdown.py` to make markdown files compliant:

```bash
# Format specific files in-place:
./scripts/format_markdown.py parts/YDNU-02.md README.md

# Format all markdown files in a directory:
./scripts/format_markdown.py parts/

# Verify compliance without modifying files:
./scripts/format_markdown.py --check parts/ README.md
```
