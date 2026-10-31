# Seagram Electronics

This repository collects all information regarding the current and planned
electronics for the Seagram sailing yacht.

## Directory Structure

- `docs/`: Technical protocol specifications and architectural documentation.
  - [`esp32-n2k-wifi-gateway`](docs/esp32-n2k-wifi-gateway.md): DIY ESP32 NMEA
    2000 to Wi-Fi/Ethernet gateway specification (alternative to YDWG-02), with
    I2C environmental/motion and 1-Wire engine monitoring sensors across
    discrete, M5Stack (PortABC + CANBus Unit), and SH-ESP32 hardware options.
  - [`nmea2000`](docs/nmea2000.md): NMEA 2000 (IEC 61162-3) protocol
    specification, CAN bus physical layer, ISO 11898-2 differential signaling,
    SAE J1939 framing, PGN datagrams, dynamic address arbitration, and LEN
    power budgeting.
  - [`seatalk1`](docs/seatalk1.md): SeaTalk1 protocol specification, electrical
    architecture, Wired-OR signaling, datagram structures, and N2K bridging.
- `parts/`: Specifications and integration guides for hardware components and
  gateways.
  - [`E22158`](parts/E22158.md): Raymarine SeaTalk1 to SeaTalkng Converter Kit
    (bridging SeaTalk1 instruments/autopilot to N2K, OpenPlotter via YD
    gateways).
  - [`iTC-5`](parts/iTC-5.md): Raymarine iTC-5 Instrument Transducer Converter
    (includes sensor wiring requirements and S2G course computer caveats).
  - [`M81105`](parts/M81105.md): Raymarine Rotary Rudder Reference Transducer
    (wiring, S2G vs EV-1/ACU-100 integration, SeaTalk1/N2K, and calibration).
  - [`M81190`](parts/M81190.md): Raymarine Fluxgate Compass Transducer (wiring,
    S2G integration, SeaTalk1 datagrams, and EV-1 replacement).
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
