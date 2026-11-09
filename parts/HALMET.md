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
  isolated analog and digital inputs, wide 5–32V power input, and Wi-Fi
  telemetry streaming.

# Technical Specifications

* **Microcontroller:** Espressif ESP32-WROOM-32E (Dual-core Xtensa 32-bit LX6 @
  240 MHz, 520 KB SRAM, 16 MB Flash memory)
* **Wireless Connectivity:** 2.4 GHz Wi-Fi (802.11 b/g/n) and Bluetooth v4.2 /
  BLE
* **Input Supply Voltage:** 5 V to 32 V DC (tolerant of nominal 12 V and 24 V
  marine electrical systems; accepts 6–32 V per hardware design specs)
* **Integrated Buck Power Supply:** High-efficiency switching regulator
  delivering up to 2 A continuous output current
* **Power Consumption:** Typical ~90 mA at 12 V DC (~1.1 W) with active Wi-Fi
* **Power Protection:**
  * 500 mA self-resetting polyfuse (PolySwitch)
  * Reverse polarity protection diode
  * Transient Voltage Suppressor (TVS) overvoltage and ESD diodes
  * Two-stage electromagnetic noise filtering
* **Galvanic Isolation:** Galvanic isolation barrier between sensor inputs
  (analog inputs via ADS1115 and digital inputs D1–D4) and the core ESP32 /
  power domain using digital isolators (for I2C and digital inputs) and an
  isolated DC/DC converter
* **Analog Inputs (A1–A4):**
  * 4 channels via 2-pin pluggable terminal blocks (Phoenix MC 3.81 mm)
  * 16-bit Texas Instruments ADS1115 ADC (on the isolated section)
  * Active measurement range: 0 to 33 V DC; voltage tolerance: -32 V to +32 V
    DC
  * Built-in low-pass filtering: 160 Hz cutoff frequency
  * Constant-Current Source (CCS): Selectable 10 mA constant-current excitation
    per channel via onboard jumper pins (for 0–300 Ω resistive sensors)
  * Optional low-pass filtering: Solder jumpers on the bottom side can engage
    an additional 2.3 kHz low-pass filter
  * ADS1115 I2C address selection solder jumpers on the bottom side
* **Digital Inputs (D1–D4):**
  * 4 channels via 2-pin pluggable terminal blocks (Phoenix MC 3.81 mm)
  * ESP32 pin mappings: D1 (GPIO 23), D2 (GPIO 25), D3 (GPIO 27), D4 (GPIO 26)
  * Voltage tolerance: -32 V to +32 V DC
  * Schmitt trigger input buffers: threshold voltage ~1.55 V with ~0.7 V
    hysteresis
  * Configurable pull-up / pull-down: Solder jumpers on the bottom side allow
    enabling internal 100 kΩ pull-up or pull-down resistors per channel
  * Optimized for engine tachometers (alternator W-terminal), alarm contacts,
    and flow meters
* **CAN / NMEA 2000 Interface:**
  * 4-pin pluggable terminal block (Phoenix MC 3.81 mm: V+, V-, CAN_H, CAN_L)
  * Hardware transceiver tied to ESP32 TWAI (CAN TX: GPIO 19, CAN RX: GPIO 18)
  * Dedicated activity status LEDs for RX and TX CAN bus traffic
  * Selectable 120 Ω bus termination solder jumper (disabled by default; do not
    enable on a terminated NMEA 2000 backbone)
* **Status LEDs and Controls:**
  * Red power LED (illuminates when 3.3V rail is active)
  * Blue user-programmable LED (GPIO 2)
  * Reset button
  * Boot / download button (GPIO 0)
* **Peripheral Expansion:**
  * I2C: 4-pin SparkFun Qwiic / STEMMA QT connector and 4-pin 2.54 mm header
    (SDA: GPIO 21, SCL: GPIO 22)
  * 1-Wire: 3-pin 2.54 mm header footprint (DQ: GPIO 4 with onboard pull-up and
    ESD protection; unpopulated by default to prevent enclosure interference)
  * Isolated Power Output: Header offering isolated 3V3 and GND rails
  * General GPIO / JTAG: 2x10 pin 2.54 mm header breaking out 13 unused GPIOs
* **Enclosure Compatibility:** Form factor fits standard 100 × 68 × 50 mm
  waterproof enclosures (same footprint as Hat Labs SH-ESP32 / SH-RPi boxes)

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

## Boat Physical Installation & Sourcing Analysis (Seagram Tanks)

### Vessel Tank Context
* **Tanks:** Two onboard fresh water tanks.
* **Inspection / Sensor Port:** Each tank is fitted with a female **1.5" NPT
  (National Pipe Taper)** threaded port intended for fluid level senders.
* **Sealing Principle:** 1.5" NPT is a tapered thread that seals via thread
  interference and thread sealant (e.g. PTFE marine thread tape or Loctite 567
  thread sealant).

### Evaluation of Sensor Sourcing Options

#### Option 1: USA (KUS S5U Series via Amazon)
* **Candidate Links:**
  * [KUS USA SSS / S5U Fuel & Water Level Sensor (Amazon B00Y831WPM)](
    https://www.amazon.com/KUS-USA-Water-Level-Sensor/dp/B00Y831WPM)
  * [KUS S5U Threaded Water Level Sensor (Amazon B0CHK2M85K)](
    https://www.amazon.com/dp/B0CHK2M85K)
* **Mechanical Fit:** **Direct Fit (Recommended)**. The KUS S5U series features
  a male 1.5" NPT threaded body that screws directly into the tank's 1.5" NPT
  bung without requiring any adapter flange or drilling.
* **Electrical Compatibility:** Typically supplied in the American standard
  (240–33 Ω). Fully compatible with HALMET's 10 mA CCS input (operating range
  0.33 V to 2.40 V, well below HALMET's 300 Ω / 3.00 V ceiling).
* **Verdict:** **Works directly without extra adapters.**

#### Option 2: France (SVB Marine KUS Sensor + Mounting Flange)
* **Candidate Links:**
  * [SVB Marine KUS Capteur Eau/Carburant](
    https://www.svb-marine.fr/fr/kus-capteurs-eau-carburant.html)
  * [SVB Marine KUS Bride de Montage](
    https://www.svb-marine.fr/fr/kus-bride-de-montage-pour-jauge-de-reservoir-a-eau-ou-carburant.html)
* **Mechanical Fit:** **Incompatible without an NPT-to-BSP adapter**.
  * European SVB KUS sensors use **1-1/4" BSP (British Standard Pipe)** male
    threads (approx 41.9 mm OD, 55° thread angle, parallel thread sealing with
    a flat NBR gasket).
  * The SVB mounting flange is a weld-in or bolt-on collar with internal 1-1/4"
    BSP threads designed to be fastened onto a flat tank top with 5 sheet metal
    screws. It cannot thread into a 1.5" NPT bung.
  * A 1.5" NPT male thread (approx 48 mm OD, 60° taper) is physically larger
    and has a different thread pitch than 1-1/4" BSP.
  * *To make this option work:* You would need a **1.5" NPT male to 1-1/4" BSPP
    female marine brass/stainless adapter bushing**.
* **Electrical Compatibility:** Standard European 0–190 Ω curve (0.00 V to 1.90
  V @ 10 mA). Fully compatible with HALMET.
* **Verdict:** **Electrically compatible, but mechanically incompatible unless
  an external 1.5" NPT to 1-1/4" BSP adapter is added.**

#### Option 3: China (AliExpress 1.5" NPT or SAE 5-Hole Senders)
* **Candidate Links:**
  * [AliExpress Marine Fuel / Water Level Sender](
    https://fr.aliexpress.com/item/1005012387264252.html)
* **Mechanical Fit:** **Conditional on Ordering Variant**.
  * If selected with the **1.5" NPT (or 1-1/2" NPT) threaded mount**, it screws
    directly into the tank bung (identical to Option 1).
  * If selected with the standard **SAE 5-hole flange**, it cannot screw into
    the 1.5" NPT bung directly; it requires an adapter such as a **1.5" NPT
    male to SAE 5-hole flange adapter** (e.g. Maretron TA-5H-1.5NPT or Boyd
    Welding aluminum adapter).
* **Electrical Compatibility:** Available in both 0–190 Ω (EU) and 240–33 Ω
  (US). Both work natively with HALMET's CCS jumper enabled.
* **Verdict:** **Works directly if and only if ordered with the 1.5" NPT
  threaded mount variant; otherwise requires an SAE 5-hole adapter.**

### Comparison Summary for Seagram Installation

| Option | Vendor / Source | Mechanical Interface | Additional Adapters Needed? | HALMET Electrical Fit |
| :--- | :--- | :--- | :--- | :--- |
| **Option 1 (USA)** | Amazon (KUS S5U) | 1.5" NPT male thread | **None** (direct screw-in) | **100% (240–33 Ω)** |
| **Option 2 (France)** | SVB Marine | 1-1/4" BSP male thread | **Yes** (1.5" NPT to 1-1/4" BSP bushing) | **100% (0–190 Ω)** |
| **Option 3 (China)** | AliExpress | 1.5" NPT (if selected) | **None** if 1.5" NPT; **Yes** if SAE 5-hole | **100% (EU or US)** |

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
               | Variable R(tank)  |         |
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
   (R_{\text{wire,out}} + R_{\text{sensor}} + R_{\text{wire,return}})$$
   $$V_{\text{measured}} = 0.010\,\text{A} \times (R_{\text{sensor}} + 2 \times
   R_{\text{wire}})$$
2. **Target Scenario Analysis (4 m One-Way Run / 22 AWG):**
   * **Wire Gauge & Physical Characteristics:** 22 AWG tinned copper marine
     wire (approx 0.33 mm² conductor cross-section) has a typical resistance of
     ~53.0 mΩ/m (~0.053 Ω/m / 16.14 Ω per 1,000 ft at 20°C).
   * **Round-Trip Length:** A 4 m one-way run produces an 8 m total loop
     length: $$R_{\text{loop}} = 8\,\text{m} \times 0.053\,\Omega/\text{m}
     \approx 0.424\,\Omega$$
   * **Induced Voltage Drop:** At a constant current of 10 mA: $$\Delta
     V_{\text{wire}} = 0.010\,\text{A} \times 0.424\,\Omega = 4.24\,\text{mV}$$
3. **Impact on Tank Level Accuracy:**
   * **European (EU) Sensor Standard (0–190 Ω, 190 Ω span / 1.90 V span):**
     * An additional $0.424\,\Omega$ loop resistance creates an offset error
       of: $$\text{Error} = \frac{0.424\,\Omega}{190\,\Omega} \times 100\%
       \approx 0.22\%$$
   * **American (US) Sensor Standard (240–33 Ω, 207 Ω span / 2.07 V span):**
     * An additional $0.424\,\Omega$ loop resistance creates an offset error
       of: $$\text{Error} = \frac{0.424\,\Omega}{207\,\Omega} \times 100\%
       \approx 0.20\%$$
   * **Comparison with Sensor Physical Resolution:**
     * Marine float level senders using magnetic reed switches (such as KUS S3
       or SSS series) have discrete float reed positions typically spaced
       between 10 mm and 21 mm apart.
     * On a standard tank sender, each discrete step corresponds to roughly 3%
       to 5% of tank volume.
     * The induced electrical error from the 22 AWG wire run ($\approx 0.21\%$)
       is approximately 15 to 25 times smaller than the sensor's physical step
       resolution.
4. **General Wire Gauge Comparison Table (for 4 m One-Way / 8 m Loop):**

| Wire Gauge | Conductor Area | Loop Resistance (8 m) | Voltage Drop (10 mA) | Error (EU 0–190 Ω) | Error (US 240–33 Ω) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **22 AWG** | 0.33 mm² | ~0.42 Ω | 4.2 mV | ~0.22% | ~0.20% |
| **20 AWG** | 0.52 mm² | ~0.26 Ω | 2.6 mV | ~0.14% | ~0.13% |
| **18 AWG** | 0.82 mm² | ~0.17 Ω | 1.7 mV | ~0.09% | ~0.08% |
| **16 AWG** | 1.31 mm² | ~0.11 Ω | 1.1 mV | ~0.06% | ~0.05% |

5. **Conclusion & Recommendations for 22 AWG:**
   * **Electrical Suitability:** 22 AWG is electrically excellent for this
     application. The voltage drop ($\approx 4.2\,\text{mV}$) and resistance
     offset ($0.42\,\Omega$) are negligible and well within acceptable
     measurement tolerances.
   * **Mechanical Considerations:** In marine environments, ABYC standards
     generally suggest 16 or 18 AWG for unsheathed wiring due to mechanical
     pull strength and vibration resistance. When using 22 AWG to reduce weight
     and cost, use a multi-conductor shielded or sheathed cable (e.g.,
     marine-rated shielded paired cable) with proper strain relief and secure
     clipping to prevent mechanical fatigue or snagging.
6. **Zero-Offset Calibration in Software:** If absolute precision is desired,
   the constant $0.42\,\Omega$ wire offset can be completely eliminated in
   software by performing a 2-point calibration (empty and full) inside SensESP
   or custom gateway firmware.

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
