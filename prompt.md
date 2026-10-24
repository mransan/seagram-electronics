# Goal 

The goal is add a new file in @docs folder for the NEMA 2K marine protocol in
similar fashion as we did for the SeaTalk1 marine protocol.

The topic covered should be similar as for the SeaTalk1.

What is important is to enrich the markdown file with url links which supports
most of the statement and information provided in the file.

# Contribution guideline

- create a dedicated branch in git to perform the task
- once the task initial implementation is complete, push to origin and create a
  pull request
- keep lines under 80 characters
- update the README.md file concisely after completing the task to help a
  coding agent understand what has been done and build on top.
- include this modified @prompt.md file into the commit/pull request

# Implementation feedback

This section is to provide iterative feedback on the ongoing task
implementation.

- Created `docs/nmea2000.md` covering physical architecture, DeviceNet/Micro-C
  cable dimensions and pinouts, ISO 11898-2 differential signaling, termination
  resistor mechanics ($60\,\Omega$ bus / $120\,\Omega$ terminators), CAN 2.0B
  extended framing (29-bit identifiers), non-destructive bitwise arbitration,
  Parameter Group Numbers (PGNs) with Fast Packet transport, dynamic 64-bit
  NAME address claim negotiation (J1939-81), Load Equivalency Number (LEN)
  power budgeting and 1.67V max drop rules, PC/SBC/ESP32 interfacing,
  diagnostic matrix, and comprehensive web citation links.
- Updated `docs/nmea2000.md` with Section 1.5 detailing how to connect multiple
  instruments (cockpit instrument pod with 3 displays) via a single cable run
  using either a multi-port drop box (Maretron / Actisense) or by extending the
  terminated backbone trunk into the pod (e.g., Raymarine 5-Way A06064).

