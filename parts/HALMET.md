# Device Identifier
* **manufacturer:** Hat Labs
* **part number:** HALMET
* **price (date in dd-mm-yyyy format):** €40.16 EUR / ~$44.00 USD (Current as
  of 09-11-2026)
* **manufacturer link:** [Hat Labs Official HALMET Product Page](
  https://shop.hatlabs.fi/products/halmet)
* **manual download link:** [Hat Labs Documentation Portal](
  https://docs.hatlabs.fi/halmet/)
* **description (50 words max):** HALMET (Hat Labs Marine Engine & Tank
  Interface) is an open-source ESP32 development board designed for boat
  engine, tank, and network monitoring. It features native NMEA 2000 CAN,
  isolated analog and digital inputs, wide 6–32V power input, and Wi-Fi
  telemetry streaming.

# Technical Specifications

* **Microcontroller:** Espressif ESP32-WROOM-32E (Dual-core Xtensa 32-bit LX6 @
  240 MHz, 520 KB SRAM, 4 MB Flash)
* **Wireless Connectivity:** 2.4 GHz Wi-Fi (802.11 b/g/n) and Bluetooth v4.2 /
  BLE
* **Input Supply Voltage:** 6 V to 32 V DC (compatible with nominal 12 V and 24
  V boat electrical systems)
* **Integrated Buck Power Supply:** 5 V DC switching regulator delivering up to
  2 A continuous output
* **Power Consumption:** Typical ~90 mA at 12 V DC (~1.1 W) with active Wi-Fi
* **Power Protection:**
  * 500 mA self-resetting polyfuse (PolySwitch)
  * Reverse polarity protection diode
  * Transient Voltage Suppressor (TVS) overvoltage and ESD diodes
  * Two-stage electromagnetic noise filtering
* **Galvanic Isolation:** Galvanic isolation barrier between sensor inputs
  (analog/digital inputs) and the core ESP32/power domain using digital
  isolators and an isolated DC/DC converter
* **Analog Inputs (A1–A4):**
  * 4 channels via 2-pin pluggable terminal blocks (Phoenix MC 3.81 mm)
  * 16-bit Texas Instruments ADS1115 ADC
  * Input voltage tolerance: -32 V to +32 V DC; active measurement range: 0 to
    33 V DC
  * Input low-pass filtering: 160 Hz cutoff frequency
  * Constant-Current Source (CCS): Selectable 10 mA constant-current excitation
    per channel via onboard jumper pins (for 0–300 Ω resistive sensors)
* **Digital Inputs (D1–D4):**
  * 4 channels via 2-pin pluggable terminal blocks (Phoenix MC 3.81 mm)
  * Voltage tolerance: -32 V to +32 V DC with Schmitt triggers (~1.55 V logic
    threshold)
  * Optimized for engine tachometers (alternator W-terminal), alarm contacts,
    and flow meters
* **CAN / NMEA 2000 Interface:**
  * 4-pin pluggable terminal block (Phoenix MC 3.81 mm: V+, V-, CAN_H, CAN_L)
  * Hardware transceiver tied to ESP32 TWAI (CAN TX: GPIO 19, CAN RX: GPIO 18)
  * Activity status LEDs for RX and TX
  * Selectable 120 Ω bus termination solder jumper (disabled by default)
* **Peripheral Expansion:**
  * I2C: 4-pin SparkFun Qwiic / STEMMA QT connector and 4-pin 2.54 mm header
    (SDA: GPIO 21, SCL: GPIO 22)
  * 1-Wire: 3-pin 2.54 mm header (DQ: GPIO 4) with onboard pull-up resistor and
    ESD protection
  * General GPIO: 2x10 pin 2.54 mm header breaking out 13 unused GPIOs / JTAG

# Power Architecture and NMEA 2000 Isolation

A critical design consideration when deploying HALMET as a gateway or sensor
monitor is its power architecture and adherence to NMEA 2000 isolation rules.

```
+--------------------------------------------------------------------------+
|                     HALMET Power & Isolation Architecture                |
|                                                                          |
|   [ NMEA 2000 Backbone ] (12V DC NET-S / 0V NET-C)                       |
|           |                                                              |
|           v                                                              |
|   +------------------------------------------------------------------+   |
|   | 4-Pin Phoenix Terminal (NET-S, NET-C, CAN_H, CAN_L)              |   |
|   |  - 500 mA Polyfuse, Reverse Diode, TVS Diodes, EMC Filter        |   |
|   +---------------------------------+--------------------------------+   |
|                                     |                                    |
|                                     v                                    |
|   +------------------------------------------------------------------+   |
|   | Onboard Switching Buck Regulator (6V-32V -> 5V DC @ 2A Max)      |   |
|   +---------------------------------+--------------------------------+   |
|                                     |                                    |
|              +----------------------+----------------------+             |
|              | (5V / 3.3V Logic)                           |             |
|              v                                             v             |
|   +----------------------+                     +---------------------+   |
|   | Core System Domain   |                     | Isolated DC/DC      |   |
|   |  - ESP32-WROOM-32E   |                     | Converter           |   |
|   |  - Wi-Fi / BLE Radio |                     +----------+----------+   |
|   |  - CAN Transceiver   |                                | (Iso Power)  |
|   +----------+-----------+                                v              |
|              |                             +-------------------------+   |
|              | <=== Galvanic Isolation ===>| Sensor Input Domain     |   |
|              |      (Digital Isolators)    |  - ADS1115 16-bit ADC   |   |
|              |                             |  - 10 mA CCS Current    |   |
|              |                             |  - Pluggable Terminals  |   |
|              v                             +-------------------------+   |
|   [ Wi-Fi Telemetry Out ]                                                |
|   (Air gap - 100% isolated)                                              |
+--------------------------------------------------------------------------+
```

## Power Supply Confirmation from NMEA 2000
* **Direct N2K Power Transformation:** HALMET contains an onboard wide-input
  (6–32 V) switching buck converter that steps down the +12V DC rail from the
  NMEA 2000 network (NET-S) to 5V DC logic power. No external buck regulator or
  voltage step-down module is needed.
* **Integrated Protection:** Unlike DIY prototyping setups requiring external
  fuse blocks, HALMET integrates an onboard 500 mA self-resetting polyfuse,
  reverse polarity protection, and TVS overvoltage suppression directly at the
  N2K power input connector.
* **Galvanic Isolation Validation:** HALMET implements galvanic isolation
  between its sensor inputs (analog and digital screw terminals) and the core
  microcontroller/power circuit.
* **NMEA 2000 Compliance Rules:** Per Hat Labs guidelines and community
  discussions on N2K power isolation, powering the board from NMEA 2000 is
  fully safe and compliant when:
  1. The gateway streams telemetry over Wi-Fi (the radio link provides complete
     galvanic air isolation from laptops, phones, and tablets).
  2. Connected sensors are unpowered passive elements or share isolated
     grounds.
  3. No unisolated wired connections (such as unisolated USB to a computer
     connected to a different AC or DC ground) are connected simultaneously,
     which would introduce a ground loop bypassing the N2K single-point ground.

# Integration with Resistive Tank Sensors (KUS Water Level)

Resistive float senders are the marine standard for monitoring water, waste,
and fuel levels. HALMET supports direct interfacing with these sensors using
its analog inputs (A1–A4) configured with the onboard Constant-Current Source
(CCS).

```
                      HALMET Resistive Measurement Circuit
             +----------------------------------------------------+
             | HALMET Isolated Domain                             |
             |                                                    |
             |   +---------------+                                |
             |   | 10 mA Current |  (CCS Jumper Installed)        |
             |   | Source (CCS)  |                                |
             |   +-------+-------+                                |
             |           |                                        |
             |           +-------------------+                    |
             |           |                   |                    |
             |           v                   v                    |
             |   [ Terminal An+ ]    [ ADS1115 ADC Input ]        |
             +-----------+-------------------+--------------------+
                         |                   |
                         | (Wire Lead 1)     |
                         v                   |
               +-------------------+         |
               |  KUS Tank Sender  |         |
               |  (e.g., S3 / SSS) |         |
               |  Variable R_tank  |         |
               +---------+---------+         |
                         |                   |
                         | (Wire Lead 2)     |
                         v                   |
             +-----------+-------------------+--------------------+
             |   [ Terminal An- ]                                 |
             |   (Sensor Isolated GND)                            |
             | HALMET Isolated Domain                             |
             +----------------------------------------------------+
```

## How the 10 mA Constant-Current Source Works
1. When the CCS jumper for a channel (A1, A2, A3, or A4) is bridged, HALMET
   routes an internal precision 10 mA (0.010 A) constant-current source through
   the positive input terminal `An+`.
2. The current flows down the wire lead, passes through the sender's internal
   resistor ladder, and returns via `An-` to the isolated analog ground.
3. According to Ohm's Law ($V = I \times R$), the voltage drop across the
   sensor is directly proportional to its resistance:
   * $R = 33\,\Omega \implies V = 0.010\,\text{A} \times 33\,\Omega =
     0.33\,\text{V}$
   * $R = 190\,\Omega \implies V = 0.010\,\text{A} \times 190\,\Omega =
     1.90\,\text{V}$
   * $R = 240\,\Omega \implies V = 0.010\,\text{A} \times 240\,\Omega =
     2.40\,\text{V}$
4. The 16-bit ADS1115 ADC samples this voltage drop with high precision and
   filters electrical noise with an onboard 160 Hz low-pass filter.

## Resistance Standard Comparison: US vs. European (EU) Standard

A common integration question is whether the sensor's resistance standard
matters when connecting to HALMET.

| Specification | US (American) Standard | European (EU) Standard |
| :--- | :--- | :--- |
| **Nominal Resistance Range** | 240 Ω (Empty) to 33 Ω (Full) | 0 Ω (Empty) to 190 Ω (Full) |
| **Resistance Direction** | Inverse (High R = Empty, Low R = Full) | Direct (Low R = Empty, High R = Full) |
| **Voltage at 10 mA** | 2.40 V (Empty) down to 0.33 V (Full) | 0.00 V (Empty) up to 1.90 V (Full) |
| **Max Resistance** | 240 Ω (well within HALMET's 300 Ω ceiling) | 190 Ω (well within HALMET's 300 Ω ceiling) |
| **HALMET Compatibility** | **Fully Compatible** | **Fully Compatible** |

### Does the Standard Matter?
* **Hardware Compatibility:** Both standards operate well within HALMET's
  maximum measurable resistance limit of **300 Ω** (which corresponds to 3.00 V
  at 10 mA). Neither standard exceeds the ADC dynamic range.
* **Firmware Configuration:** The only place where the standard matters is the
  software calibration curve (in SensESP or custom firmware):
  * For **EU senders (0–190 Ω)**, software maps lower voltages to empty and
    higher voltages to full using a linear interpolation (`CurveInterpolator`).
  * For **US senders (240–33 Ω)**, software maps higher voltages to empty and
    lower voltages to full. Note that KUS US senders often have a slightly
    non-linear step progression (25% = ~142 Ω, 50% = ~105 Ω, 75% = ~68 Ω),
    which is easily linearized using a multi-point SensESP calibration table.
* **Stand-Alone vs. Dual-Gauge Integration:**
  * If the KUS sender connects *only* to HALMET (no analog dashboard gauge),
    install the CCS jumper and either US or EU sensor can be selected.
  * If the KUS sender is *also shared* with an existing analog dashboard gauge,
    **do not install the CCS jumper**. The existing gauge already excites the
    sensor; HALMET measures the resulting voltage passively in parallel. In
    this shared scenario, the sensor standard must match the analog gauge.

## Wire Length, Resistance, and Potential Voltage Drop

Another critical installation factor is whether the length of the wire run
between the water tank sender and HALMET introduces significant measurement
error.

### Analysis of Constant-Current vs. Constant-Voltage Drive
In traditional constant-voltage circuits (like automotive 12V gauge circuits),
current varies with resistance, and wire resistance adds directly to the
circuit load. With HALMET's **10 mA constant-current drive**, the electrical
dynamics are as follows:

1. **Constant Current Through Series Loop:** Because HALMET forces a constant
   10 mA through the entire current loop, exactly 10 mA flows through the lead
   wires and the tank sender in series: $$V_{\text{measured}} = I \times
   (R_{\text{wire\_out}} + R_{\text{sensor}} + R_{\text{wire\_return}})$$
   $$V_{\text{measured}} = 0.010\,\text{A} \times (R_{\text{sensor}} + 2 \times
   R_{\text{wire}})$$
2. **Wire Resistance Calculations for Marine Runs:** Consider standard marine
   tinned copper wire runs typical of a 30 to 45 foot sailboat (round-trip
   cable length of 10 to 30 meters):
   * **16 AWG (1.31 mm²):** Resistance is ~13.2 mΩ/m (~0.0132 Ω/m).
     * 10 m round trip (5 m run): $R_{\text{loop}} = 0.13\,\Omega \implies
       \Delta V = 0.010 \times 0.13 = 1.3\,\text{mV}$
     * 30 m round trip (15 m run): $R_{\text{loop}} = 0.40\,\Omega \implies
       \Delta V = 0.010 \times 0.40 = 4.0\,\text{mV}$
   * **18 AWG (0.82 mm²):** Resistance is ~21.0 mΩ/m (~0.0210 Ω/m).
     * 10 m round trip (5 m run): $R_{\text{loop}} = 0.21\,\Omega \implies
       \Delta V = 0.010 \times 0.21 = 2.1\,\text{mV}$
     * 30 m round trip (15 m run): $R_{\text{loop}} = 0.63\,\Omega \implies
       \Delta V = 0.010 \times 0.63 = 6.3\,\text{mV}$
3. **Impact on Tank Measurement Accuracy:**
   * For a European sensor (0–190 Ω, span of 190 Ω / 1.90 V):
     * A 30 m 16 AWG loop adds $0.40\,\Omega$, creating an offset error of
       $0.40 / 190 \approx 0.21\%$ of full scale.
   * For an American sensor (240–33 Ω, span of 207 Ω / 2.07 V):
     * A 30 m 16 AWG loop adds $0.40\,\Omega$, creating an offset error of
       $0.40 / 207 \approx 0.19\%$ of full scale.
   * Most reed-switch tank level senders (including KUS S3/SSS series) have
     discrete magnetic reed steps spaced at 10 mm to 21 mm intervals, yielding
     a physical resolution of 3% to 5%.
   * **Conclusion:** The wire resistance error ($<0.25\%$) is more than an
     order of magnitude smaller than the sensor's physical step resolution.
     Therefore, **wire length and voltage drop do not materially affect
     measurement accuracy** on typical boat installations when using 16 or 18
     AWG marine wire.
4. **Zero-Offset Calibration in Software:** If absolute precision is desired,
   the constant wire resistance offset can be calibrated out completely in
   software by performing a 2-point calibration (empty and full) with the tank
   in place.

# Integration with External Systems

## Tablet / Phones (Navionics, Aqua Map, OpenCPN)
* **Connectivity:** 2.4 GHz Wi-Fi link. The ESP32 acts as a SoftAP or connects
  to the onboard router.
* **Configuration Steps:** Connect device to Wi-Fi. In the navigation app,
  configure a UDP connection on port 2000 or TCP connection on port 10110 (NMEA
  0183 sentences converted from N2K/sensors).
* **Dependency:** App must support NMEA 0183 over TCP/UDP.

## OpenPlotter / Signal K Server (Raspberry Pi)
* **Connectivity:** Wi-Fi connection directly to the boat router or HALMET AP.
* **Configuration Steps:** In the Signal K admin console
  (`http://localhost:3000`), navigate to **Server -> Data Connections**, click
  **Add Connection**:
  * Data Type: **NMEA 2000** or **Signal K**
  * Connection Type: **TCP Client** or **WebSockets**
  * Port: **1456** (Yacht Devices RAW format) or **80** (SensESP Signal K)
* **Dependency:** Requires Signal K node server running on the local network.

## PC with OpenCPN
* **Connectivity:** Direct Wi-Fi link to HALMET or shared boat network.
* **Configuration Steps:** In OpenCPN -> Options -> Connections -> Add
  Connection: Select **Network**, choose **TCP**, enter HALMET's IP address,
  port **10110**, and check "Receive data on this port".
* **Dependency:** Dependent on stable 2.4 GHz Wi-Fi link.
