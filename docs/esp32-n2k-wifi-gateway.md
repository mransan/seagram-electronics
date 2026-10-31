# DIY ESP32 NMEA 2000 to Wi-Fi Gateway Guide

This engineering guide provides a complete hardware and software specification
for designing and building a DIY marine [NMEA 2000 (IEC
61162-3)][ref-nmea2000-spec] to Wi-Fi/Ethernet gateway using the Espressif
[ESP32 microcontroller][ref-espressif-esp32]. This design functions as a
low-cost, customizable alternative to commercial gateways such as the [Yacht
Devices YDWG-02][ref-ydwg02-doc].

The gateway listens passively (or interactively) on the physical NMEA 2000 CAN
bus backbone, decodes or encapsulates marine Parameter Group Numbers (PGNs),
and streams them concurrently over TCP and UDP sockets. This enables consumer
mobile devices (iPhones, iPads, Android tablets) running navigation software
(Navionics Boating, Aqua Map, OpenCPN) and shipboard servers (Signal K on
OpenPlotter) to access real-time boat telemetry over Wi-Fi.

In addition to CAN bridging, the gateway functions as an auxiliary sensor
concentrator by integrating **I2C environmental and motion sensors**
(barometric pressure, cabin humidity, boat heeling/pitch, and backup compass
heading) as well as **1-Wire temperature probes** (engine head and wet exhaust
monitoring), broadcasting this telemetry directly onto the N2K bus and Wi-Fi
data streams.

---

## 1. Architectural Overview and Feasibility

Commercial marine gateways like the Yacht Devices YDWG-02 retail for
approximately \$249 USD. A custom ESP32-based gateway achieving identical or
superior data-throughput and stream flexibility can be constructed for \$25 to
\$60 USD depending on component choices.

```
+--------------------------------------------------------------------------+
|                       System Architecture Overview                       |
|                                                                          |
|  [ NMEA 2000 Backbone ] (CAN Bus 250 kbps, 12V DC Rail)                  |
|          |                                                               |
|    [ Micro-C Spur Cable ]                                                |
|          |                                                               |
|          v                                                               |
|  +--------------------------------------------------------------------+  |
|  | Hardware: Isolated CAN Transceiver + DC-DC Step-Down (12V -> 5V)   |  |
|  +--------------------------------------------------------------------+  |
|          | TWAI (CAN_TX / CAN_RX)                                        |
|          v                                                               |
|  +--------------------------------------------------------------------+  |
|  | ESP32 Microcontroller Core (FreeRTOS Dual Core)                    |  |
|  |  - Core 0: CAN interrupt, PGN parsing, NMEA 0183 conversion        |  |
|  |  - Core 1: Wi-Fi stack, TCP server, UDP broadcast, Web UI          |  |
|  |  - Sensor Tasks: I2C (BME280 / MPU9250), 1-Wire (DS18B20 Probes)   |  |
|  +--------------------------------------------------------------------+  |
|          |                                      |                        |
|          | (Local Sensor Buses)                 | (Wi-Fi 802.11 b/g/n)   |
|          +--> I2C: Baro, Humid, Heel, Pitch     +--> TCP 1456: Raw N2K   |
|          +--> 1-Wire: Engine & Exhaust Temps    +--> TCP 10110: 0183     |
|                                                 +--> UDP 2000: Tablets   |
|                                                 +--> HTTP 80: Web UI     |
+--------------------------------------------------------------------------+
```

### 1.1 Technical Feasibility

* **Processing Capability:** The ESP32 dual-core Xtensa LX6 microprocessor
  operates at up to 240 MHz with 520 KB SRAM. It possesses ample computation
  margin to handle full NMEA 2000 bus loads (250 kbps, typically 300 to 1,500
  frames/second) while managing Wi-Fi networking, TCP buffering, sensor
  sampling routines, and sentence conversion.
* **Integrated CAN Controller (TWAI):** The ESP32 silicon includes an on-chip
  hardware CAN 2.0B controller, named the [Two-Wire Automotive Interface
  (TWAI)][ref-esp32-twai]. It directly implements 29-bit extended frame
  filtering, dynamic error tracking, and bit timing at 250 kbps without
  requiring an external SPI CAN controller like the MCP2515.
* **Network Protocol Versatility:** The ESP32 supports concurrent Wi-Fi Station
  (STA) mode (joining an existing onboard router) and Access Point (SoftAP)
  mode, alongside native FreeRTOS TCP/IP (LwIP) sockets.

### 1.2 Transceiver Selection: Isolated vs. Non-Isolated

Connecting an ESP32 safely to an NMEA 2000 network requires strict adherence to
isolation, voltage regulation, and signal line mapping:

1. **Non-Isolated Transceiver (e.g., SN65HVD230):**
   * Uses a common ground plane between the boat's battery bank and the ESP32.
   * *Limitation:* Prone to ground loops and voltage differentials when
     powering the ESP32 from a separate USB port or laptop, risking hardware
     burnout during engine cranking or high-load inverter activity.
     Non-isolated interfaces do not comply with commercial marine standards.
2. **Galvanically Isolated Transceiver (e.g., ISO1050 / CA-IS3050G):**
   * Features a silicon dielectric capacitive or magnetic isolation barrier
     rated to 1 kV DC or 2.5 kV RMS.
   * Completely isolates the differential data pair (`CAN_H` / `CAN_L`) and
     chassis grounds, preventing earth loops and electrical interference from
     migrating between the navigation backbone and the Wi-Fi gateway.

### 1.3 Power Supply, Voltage Regulation, and Dual-Power Hazards

Standard marine 12V DC power fluctuates between 11.5V and 14.8V DC (with
transient spikes up to 40V during inductive load dumps or alternator load
dumps). The ESP32 and associated sensor peripherals operate at 5.0V / 3.3V DC
logic and consume approximately 120 mA to 240 mA at 3.3V (averaging ~180 mA
during active Wi-Fi transmission). Linear regulators (e.g. LM7805 or AMS1117)
must never be used directly from 12V because dissipating $1.7\,\text{W}$ of
waste heat in an unventilated marine enclosure causes thermal shutdown. A
high-efficiency switching step-down (buck) converter is required.

#### Power Source Options: N2K Backbone vs. 12V Distribution Panel

Builders can energize the gateway from one of two power rails:

1. **Option A: Powered from the NMEA 2000 Backbone (LEN Budgeted):**
   * Draws 12V directly from the Micro-C drop cable red/black pair.
   * Converted through an efficient switching buck regulator, the gateway draws
     $\sim 50\,\text{mA}$ from the backbone: $$\text{LEN} =
     \frac{50\,\text{mA}}{50\,\text{mA/LEN}} = 1\,\text{LEN}$$
   * *Trade-off:* Consumes power from the N2K network power tap and requires an
     inline 0.5A fast-blow fuse to protect backbone cabling.
2. **Option B: Powered from the Boat 12V DC Distribution Panel (Recommended):**
   * Connects the buck converter directly to a dedicated switched breaker or
     fuse on the boat's primary DC panel (e.g., labeled `INSTRUMENTS` or
     `GATEWAY`).
   * A pre-assembled, potted IP67 marine 12V-to-5V step-down module (e.g. with
     bare wire outputs or an integrated USB-C pigtail) offers robust vibration
     and moisture resistance.
   * *Advantages:* Contributes **zero load** to the NMEA 2000 bus ($\text{LEN}
     = 0$) and allows power cycling independently of navigation instruments.
     Because the CAN transceiver (CA-IS3050G / ISO1050) provides galvanic
     isolation, powering from the house battery panel introduces no ground
     loops onto the N2K bus. The N2K spur red wire (+12V) is simply capped and
     left disconnected.

#### Dual-Power Backfeed Hazard: USB-C vs. Grove / External 5V Rail

A critical electrical hazard arises when connecting a development computer via
USB-C while the controller is simultaneously powered from an external 5V source
(whether derived from the 12V panel or from the N2K bus through a buck
converter, Grove port, or 5V header pin):

> [!CAUTION] **No Power Multiplexing / Ideal Diode on Atom Lite & Dev Boards:**
> The 5V pin on the Grove connector, the 5V header pin, and the USB-C VBUS
> power pin are directly tied to a common `5V` power net without diode
> isolation. If external 5V power is active while a computer is plugged into
> the USB-C port, any slight voltage potential difference (e.g.
> $5.20\,\text{V}$ from the buck converter vs. $5.00\,\text{V}$ from the PC)
> will cause high reverse currents to **backfeed** directly into the computer's
> USB host controller. This can trip USB port overcurrent protection or destroy
> host motherboard ports.

To safely develop, flash firmware, or monitor serial logs without removing
hardware:

* **Method 1 (Power-Cut USB Cable / Data Blocker):** Use a USB-C data cable
  with the VBUS (+5V) wire severed or covered with tape, or insert a "data-only
  USB blocker." Data lines (D+/D-) and ground remain intact for flashing, while
  5V power is supplied exclusively by the boat system.
* **Method 2 (Panel Breaker Isolation):** When using a 12V distribution panel
  feed, switch **OFF** the gateway circuit breaker before plugging in a normal
  laptop USB-C cable. The laptop safely powers the controller and Grove sensors
  during testing. Disconnect the USB-C cable before turning the breaker back
  ON.
* **Method 3 (Inline Schottky Diode):** Install an inline low-drop Schottky
  diode (e.g., 1N5819 or SS34) on the +5V output line from the buck converter.
  The diode blocks reverse current from flowing back into the converter when
  USB-C is plugged in, while incurring an insignificant voltage drop ($\sim
  0.25\,\text{V}$) during normal operation.

### 1.4 Auxiliary Sensor Protocols: I2C and 1-Wire

Expanding the gateway to act as an environmental, motion, and engine monitor
leverages two standard microcontroller buses:

#### I2C Bus (Inter-Integrated Circuit)

I2C is a 2-wire synchronous serial protocol (SDA data, SCL clock) with open-
drain drivers and pull-up resistors (typically $4.7\,\text{k}\Omega$ to 3.3V).
It allows multiple addressable sensors to share the same bus over short wire
runs ($< 1\,\text{meter}$):

* **Environmental Monitoring (Bosch BME280):** Measures barometric pressure
  ($\pm 1\,\text{hPa}$), ambient temperature ($\pm 0.5^\circ\text{C}$), and
  relative humidity ($\pm 3\%$). Essential for tracking barometric pressure
  drops to anticipate squalls and storms.
  * *N2K Output:* Broadcasts PGN 130310 (Environmental Parameters) and PGN
    130311 (Environmental Parameters, Detailed).
* **Vessel Attitude & Heeling (InvenSense MPU-6050 / MPU-9250):** 6-axis or
  9-axis Inertial Measurement Unit (IMU) measuring roll, pitch, and angular
  rates. Provides real-time boat heeling angles for performance sailing and
  trim optimization.
  * *N2K Output:* Broadcasts PGN 127257 (Attitude: Yaw, Pitch, Roll).
* **Backup Compass Heading (QMC5883L / BNO085):** Digital 3-axis magnetometer
  providing magnetic heading as an independent redundancy for the primary
  autopilot fluxgate or gyro compass.
  * *N2K Output:* Broadcasts PGN 127250 (Vessel Heading).

#### 1-Wire Bus (Dallas / Maxim)

1-Wire is a master-slave asynchronous protocol requiring only a single data
line (plus ground and optional 3.3V/5V power) with a single
$4.7\,\text{k}\Omega$ pull-up resistor. Every 1-Wire device possesses a
factory-lasered unique 64-bit ROM address, allowing dozens of probes to be
wired in parallel along a single twisted pair:

* **Engine & Exhaust Temperature Probes (Dallas DS18B20):** Ruggedized,
  waterproof stainless-steel tubular probes rated from $-55^\circ\text{C}$ to
  $+125^\circ\text{C}$ ($\pm 0.5^\circ\text{C}$ accuracy).
  * **Engine Head / Block Probe:** Monitors engine coolant or cylinder head
    temperature for thermal saturation.
  * **Wet Exhaust Hose Probe:** Installed directly against or into the wet
    exhaust mixing elbow. A raw water impeller failure causes exhaust gas
    temperatures to spike above $80^\circ\text{C}$ within seconds, alerting the
    skipper minutes before the engine block temperature alarm triggers.
  * *N2K Output:* Broadcasts PGN 130312 (Temperature) and PGN 130316
    (Temperature, Extended Range) with source types set to Main Engine and
    Exhaust Gas.

---

## 2. Hardware Options

Depending on assembly preferences, required sensor integrations, and budget,
builders can construct the gateway using one of three architectural approaches:

1. **Discrete Prototyping:** Bare-metal ESP32 dev board with discrete isolated
   transceiver and buck converter, wired via prototyping headers or breadboard.
2. **M5Stack Modular Ecosystem:** Atom Lite controller docked onto an Atomic
   PortABC base with an external isolated CANBus Unit, offering three
   dedicated, keyed Grove ports for plug-and-play wiring.
3. **Marine Integrated Board (SH-ESP32):** Commercial-grade open-source marine
   PCB featuring integrated isolated CAN, automotive-grade 8–32V power supply,
   TVS surge suppression, and built-in screw terminals for I2C and 1-Wire.

---

### 2.1 Discrete Prototyping

This approach utilizes individual off-the-shelf breakout modules. It is the
lowest-cost option and provides complete flexibility, but requires point-to-
point soldering, custom wire harnesses, and an external enclosure.

#### Bill of Materials (Discrete Prototyping)

| Component | Part Description | Approx Price (USD) | Function & Sourcing Links |
| :--- | :--- | :--- | :--- |
| **Microcontroller** | ESP32 DevKit V1 (NodeMCU-32S) | \$4.50 – \$7.00 | Dual-core 240 MHz MCU, integrated Wi-Fi / Bluetooth ([Espressif][ref-espressif-esp32]) |
| **Isolated CAN Transceiver** | TI ISO1050 / CA-IS3050G Breakout | \$5.00 – \$9.00 | 2.5 kV RMS isolated CAN transceiver with isolated DC-DC ([TI ISO1050][ref-iso1050-ti]) |
| **DC-DC Step-Down (Buck)** | MP1584EN or LM2596 Buck Converter | \$2.00 – \$4.00 | Converts 12V N2K rail to clean 5V DC ([Pololu Regulators][ref-pololu-buck]) |
| **Spur Cable** | NMEA 2000 Micro-C Drop Cable (1 m) | \$12.00 – \$18.00 | Molded DeviceNet Micro-C male to bare pigtail wires ([Actisense Cable][ref-actisense-guide]) |
| **Inline Fuse** | 0.5A fast-blow inline fuse holder | \$1.50 – \$3.00 | Protects backbone wiring against DC-DC converter short |
| **Environmental Sensor** | BME280 Breakout Module (I2C) | \$4.00 – \$8.00 | Pressure, temperature, and humidity sensor |
| **Motion / IMU Sensor** | MPU-9250 or MPU-6050 Breakout (I2C) | \$3.50 – \$7.00 | 9-axis or 6-axis gyro/accelerometer/compass |
| **Engine Temp Probes** | DS18B20 Waterproof Stainless (x2) | \$5.00 – \$8.00 | Engine block and wet exhaust temperature probes |
| **Pull-up Resistor** | $4.7\,\text{k}\Omega$ 1/4W Resistor | \$0.20 – \$0.50 | 1-Wire bus pull-up to 3.3V |
| **Enclosure & Passives** | IP65 ABS Junction Box + Glands | \$6.00 – \$10.00 | Sealed marine enclosure and cable strain reliefs |
| **Total (Discrete)** | | **\$43.70 – \$74.50** | Lowest component cost; requires manual soldering |

#### Point-to-Point Wiring Description

All connections are made via point-to-point soldering or prototype terminal
strips:

1. **NMEA 2000 Spur Cable Connections:**
   * **Red Wire (NET-S / +12V DC):** Connects to **Inline Fuse (0.5A)** input;
     the fuse output connects to **Buck Converter VIN (+)**.
   * **Black Wire (NET-C / 0V Ground):** Connects to a common ground junction
     that connects to **Buck Converter VIN (-)** and **Isolated CAN Transceiver
     Bus-Side GND (GND2)**.
   * **White Wire (NET-H / CAN High):** Connects to **Isolated CAN Transceiver
     CAN_H Terminal**.
   * **Blue Wire (NET-L / CAN Low):** Connects to **Isolated CAN Transceiver
     CAN_L Terminal**.
   * **Bare Shield Wire (Drain):** Left unconnected (floating) at the device;
     grounded exclusively at the single central N2K power insertion tap.
2. **Power Supply & ESP32 Connections:**
   * **Buck Converter VOUT (+5V):** Connects to **ESP32 DevKit 5V (VBUS) Pin**
     and **Isolated CAN Transceiver Logic-Side VCC1**.
   * **Buck Converter VOUT (GND):** Connects to **ESP32 DevKit GND Pin** and
     **Isolated CAN Transceiver Logic-Side GND1**.
3. **CAN Controller (TWAI) Signal Connections:**
   * **Isolated CAN Transceiver TXD Pin:** Connects to **ESP32 GPIO 5**
     (TWAI_TX).
   * **Isolated CAN Transceiver RXD Pin:** Connects to **ESP32 GPIO 4**
     (TWAI_RX).
4. **I2C Sensor Bus Connections (BME280 & MPU-9250):**
   * **ESP32 3.3V Out Pin:** Connects to **BME280 VCC** and **MPU-9250 VCC**.
   * **ESP32 GND Pin:** Connects to **BME280 GND** and **MPU-9250 GND**.
   * **ESP32 GPIO 21 (SDA):** Connects to **BME280 SDA** and **MPU-9250 SDA**.
   * **ESP32 GPIO 22 (SCL):** Connects to **BME280 SCL** and **MPU-9250 SCL**.
5. **1-Wire Temperature Sensor Bus Connections (DS18B20 Probes):**
   * **ESP32 3.3V Out Pin:** Connects to **DS18B20 Red Wires (VDD)** and to one
     lead of the **$4.7\,\text{k}\Omega$ Pull-up Resistor**.
   * **ESP32 GND Pin:** Connects to **DS18B20 Black Wires (GND)**.
   * **ESP32 GPIO 18 Pin:** Connects to **DS18B20 Yellow Wires (DATA)** and to
     the second lead of the **$4.7\,\text{k}\Omega$ Pull-up Resistor**.

---

### 2.2 M5Stack Modular Ecosystem

The M5Stack modular approach eliminates custom soldering by leveraging keyed
Grove cables, modular snap-on enclosures, and pre-packaged sensor modules. The
preferred architecture pairs an **Atom Lite** controller with an **Atomic
PortABC Base** and an external **M5Stack CANBus Unit (CA-IS3050G)**.

This arrangement breaks out three distinct, dedicated Grove ports: Port A
(I2C), Port B (GPIO / 1-Wire), and Port C (UART / CAN), completely avoiding
header conflicts and maintaining a sealed, professional installation.

```
+--------------------------------------------------------------------------+
|                  M5Stack Modular Hardware Architecture                   |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   | [ M5Stack Atom Lite ] (Top Module: ESP32-PICO-D4 Core + Wi-Fi)   |   |
|   |   - Reset button, RGB Status LED, 2.4 GHz 3D Wi-Fi antenna       |   |
|   +------------------------------------------------------------------+   |
|                                 ||                                       |
|               (9-Pin Gold Header / Socket Interface)                     |
|                                 ||                                       |
|   +------------------------------------------------------------------+   |
|   | [ Atomic PortABC Base ] (Port Expansion Base)                    |   |
|   +-----+-----------------------+----------------------+-------------+   |
|         |                       |                      |                 |
|    [ Port A: I2C ]         [ Port B: GPIO ]       [ Port C: UART/CAN ]   |
|     (GPIO 26/32)            (GPIO 23/33)           (GPIO 19/22)          |
|         |                       |                      |                 |
|         v                       v                      v                 |
|   [ M5 ENV IV Unit ]      [ 1-Wire Adapter ]     [ M5 CANBus Unit ]      |
|    (BME280 + SHT40)        (DS18B20 Probes)       (Isolated CA-IS3050G)  |
|                                                        |                 |
|                                                        v                 |
|                                                 [ NMEA 2000 Spur ]       |
+--------------------------------------------------------------------------+
```

#### Bill of Materials (M5Stack Ecosystem)

| Component | Part Description | Approx Price (USD) | Function & Sourcing Links |
| :--- | :--- | :--- | :--- |
| **Controller** | [M5Stack Atom Lite][ref-m5stack-atom] | \$7.50 – \$10.00 | ESP32-PICO-D4 in compact $24 \times 24\,\text{mm}$ housing |
| **Port Expansion Base** | [M5Stack Atomic PortABC Base][ref-m5stack-portabc] | \$5.50 – \$8.00 | Snaps to Atom Lite, breaking out Port A, Port B, Port C |
| **Isolated CAN Transceiver** | [M5Stack CANBus Unit (CA-IS3050G)][ref-m5stack-canunit] | \$9.50 – \$13.00 | Isolated CAN transceiver unit with screw terminals |
| **DC-DC Step-Down (Buck)** | Mini Buck Regulator (e.g. MP1584EN) | \$2.00 – \$4.00 | Steps 12V N2K rail down to 5.0V to power the stack |
| **Inline Fuse** | 0.5A fast-blow inline fuse holder | \$1.50 – \$3.00 | Protects backbone wiring against DC-DC converter short |
| **Spur Cable** | NMEA 2000 Micro-C Drop Cable (1 m) | \$12.00 – \$18.00 | Micro-C male connector to bare pigtail wires |
| **Environmental Sensor** | [M5Stack ENV IV Unit][ref-m5stack-env4] (I2C) | \$8.50 – \$12.00 | SHT40 + BMP280 environmental module (Grove Port A) |
| **Attitude / IMU Sensor** | [M5Stack IMU Unit][ref-m5stack-imu] (I2C) | \$6.00 – \$9.00 | 6-axis / 9-axis attitude sensor (daisy-chains on Port A) |
| **Grove I2C Hub** | [M5Stack Grove Hub][ref-m5stack-hub] (1-to-3) | \$2.50 – \$4.00 | Passive I2C splitter for multiple Grove sensors |
| **1-Wire Temperature Probes** | DS18B20 Probes + Grove Adapter | \$7.00 – \$12.00 | Engine & wet exhaust probes wired to Port B |
| **Total (M5Stack)** | | **\$62.00 – \$93.00** | Modular, no soldering, industrial plastic enclosures |

#### Point-to-Point Wiring Description

1. **NMEA 2000 Spur Cable Connections:**
   * **Red Wire (NET-S / +12V DC):** Connects to **Inline Fuse (0.5A)** input;
     the fuse output connects to **Buck Converter VIN (+)**.
   * **Black Wire (NET-C / 0V Ground):** Connects to a common terminal that
     branches to **Buck Converter VIN (-)** and **M5 CANBus Unit Terminal G
     (GND)**.
   * **White Wire (NET-H / CAN High):** Connects to **M5 CANBus Unit Terminal H
     (CAN_H)**.
   * **Blue Wire (NET-L / CAN Low):** Connects to **M5 CANBus Unit Terminal L
     (CAN_L)**.
   * **Bare Shield Wire (Drain):** Left unconnected (floating) at the gateway;
     grounded exclusively at the single central N2K power insertion tap.
2. **5V Power Distribution from Buck Converter:**
   * **Buck Converter VOUT (+5V):** Connects to **Atom Lite 5V Pin** (or
     soldered to a cut USB-C cable powering the Atom Lite port).
   * **Buck Converter VOUT (GND):** Connects to **Atom Lite GND Pin**.
   * *Note:* The Atom Lite distributes this regulated 5V through the PortABC
     base to power the CANBus Unit, I2C sensors, and 1-Wire sensors.
3. **M5Stack Inter-Module & Sensor Cabling (Pre-Crimped Grove Cables):**
   * **Atom Lite to PortABC Base:** Snaps directly together via the underside
     9-pin mating header.
   * **Port C (Blue Grove Port):** Connects via a 4-pin Grove cable to the
     **M5Stack CANBus Unit**. The PortABC maps **GPIO 19** to CAN_RX and **GPIO
     22** to CAN_TX.
   * **Port A (Red Grove Port):** Connects via a 4-pin Grove cable to the
     **M5Stack Grove Hub**:
     * Hub Port 1 connects to the **M5Stack ENV IV Unit** (GPIO 26 SDA, GPIO 32
       SCL, 3.3V, GND).
     * Hub Port 2 connects to the **M5Stack IMU Unit** (sharing the I2C bus).
   * **Port B (Black Grove Port):** Connects to the **1-Wire Temperature
     Probes**:
     * Port B Pin 1 (5V / 3.3V Power): Connects to **DS18B20 Red Wires (VDD)**.
     * Port B Pin 2 (GND): Connects to **DS18B20 Black Wires (GND)**.
     * Port B Pin 3 (**GPIO 23**): Connects to **DS18B20 Yellow Wires (DATA)**
       with an inline $4.7\,\text{k}\Omega$ pull-up resistor to the power wire.

---

### 2.3 Marine Integrated Board: SH-ESP32

The **Sailor Hat with ESP32 (SH-ESP32)** by Hat Labs is a purpose-built, open-
source hardware marine development board. It incorporates galvanic CAN
isolation, transient TVS overvoltage suppression, an automotive-grade
wide-input switching buck regulator, and pluggable screw terminals into a
single compact board designed for marine electrical panels.

```
+--------------------------------------------------------------------------+
|                  Sailor Hat with ESP32 (SH-ESP32) Architecture           |
|                                                                          |
|   [ N2K 12V / CAN ]          [ DC Power In ]           [ Sensors ]       |
|    NET-H, NET-L, GND          8V - 32V Input          I2C & 1-Wire       |
|           |                         |                       |            |
|           v                         v                       v            |
|   +---------------+         +---------------+       +---------------+    |
|   | Galvanically  |         | 8-32V to 5V   |       | Protected     |    |
|   | Isolated CAN  |         | Auto Buck     |       | Qwiic / Screw |    |
|   | Transceiver   |         | Converter     |       | Terminals     |    |
|   +-------+-------+         +-------+-------+       +-------+-------+    |
|           |                         |                       |            |
|       (GPIO 32/34)                (5V)                (GPIO 16/17, 4)    |
|           |                         |                       |            |
|           +-------------------------+-----------------------+            |
|                                     |                                    |
|                                     v                                    |
|                   +-----------------------------------+                  |
|                   | ESP32-WROOM-32 Controller Module  |                  |
|                   |  - 2.4 GHz Wi-Fi / Bluetooth LE   |                  |
|                   |  - Dual-core Xtensa 240 MHz MCU   |                  |
|                   +-----------------------------------+                  |
+--------------------------------------------------------------------------+
```

#### Bill of Materials (SH-ESP32)

| Component | Part Description | Approx Price (USD) | Function & Sourcing Links |
| :--- | :--- | :--- | :--- |
| **Integrated Board** | [Sailor Hat with ESP32 (SH-ESP32)][ref-sh-esp32] | \$38.00 – \$55.00 | Marine-grade ESP32 board with isolated CAN, 8–32V buck supply, opto-inputs |
| **Spur Cable** | NMEA 2000 Micro-C Drop Cable (1 m) | \$12.00 – \$18.00 | Micro-C male connector to bare pigtail wires |
| **Inline Fuse** | 0.5A fast-blow inline fuse holder | \$1.50 – \$3.00 | Protects backbone wiring against short |
| **Environmental Sensor** | SparkFun / Adafruit BME280 Qwiic | \$8.00 – \$14.00 | Plugs directly into SH-ESP32 Qwiic/I2C connector |
| **Attitude / IMU Sensor** | Adafruit 9-DOF IMU (ICM-20948 / BNO085) | \$12.00 – \$22.00 | Daisy-chains onto the Qwiic I2C bus |
| **Engine Temp Probes** | DS18B20 Waterproof Probes (x2) | \$5.00 – \$8.00 | Plugs directly into the SH-ESP32 1-Wire terminals |
| **Total (SH-ESP32)** | | **\$76.50 – \$120.00** | Professional marine grade, TVS protection, screw terminals |

#### Point-to-Point Wiring Description

1. **NMEA 2000 Spur Cable Connections:**
   * **Red Wire (NET-S / +12V DC):** Connects to **Inline Fuse (0.5A)** input;
     the fuse output connects to **SH-ESP32 VIN Screw Terminal** (accepts 8V to
     32V DC).
   * **Black Wire (NET-C / 0V Ground):** Connects to **SH-ESP32 Power GND Screw
     Terminal** and **CAN GND Terminal**.
   * **White Wire (NET-H / CAN High):** Connects to **SH-ESP32 CAN_H
     Terminal**.
   * **Blue Wire (NET-L / CAN Low):** Connects to **SH-ESP32 CAN_L Terminal**.
   * **Bare Shield Wire (Drain):** Left unconnected (floating) at the device;
     grounded exclusively at the central N2K power tap.
2. **I2C Sensor Bus Connections (BME280 & IMU):**
   * Connects via standard SparkFun Qwiic (or Adafruit STEMMA QT) 4-pin JST-SH
     cable directly to the **SH-ESP32 Qwiic Port** (or 2.54 mm screw header):
     * Pin 1 (GND): Ground.
     * Pin 2 (3V3): 3.3V Power.
     * Pin 3 (SDA): Hardwired internally on SH-ESP32 to **GPIO 16**.
     * Pin 4 (SCL): Hardwired internally on SH-ESP32 to **GPIO 17**.
3. **1-Wire Temperature Sensor Bus Connections (DS18B20 Probes):**
   * Connects directly to the dedicated 3-pin 1-Wire header on the SH-ESP32:
     * **VDD (+3.3V):** Connects to **DS18B20 Red Wires**.
     * **GND:** Connects to **DS18B20 Black Wires**.
     * **DQ (Data):** Connects to **DS18B20 Yellow Wires**. Hardwired
       internally to **GPIO 4** with an integrated onboard pull-up resistor and
       RClamp ESD surge protection.

---

## 3. Software Architecture and Streaming Protocols

To replicate commercial marine gateways, the firmware manages multiple
concurrent network sockets, parses N2K CAN traffic, samples onboard sensors,
and converts data into standard formats:

```
                          +------------------------+
                          |   NMEA 2000 CAN Bus    |
                          +-----------+------------+
                                      |
                                      v
                          +------------------------+
                          | Timo Lappalainen's     |
                          | NMEA2000_esp32 Driver  |
                          +-----------+------------+
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v (Raw CAN Frames)                        v (Parsed PGN Data)
    +--------------------------+              +--------------------------+
    | Formatter: Yacht Devices |              | Translator: NMEA0183     |
    | RAW or Actisense NGT-1   |              | Library ($IIMWV, $GPGGA) |
    +------------+-------------+              +------------+-------------+
                 |                                         |
                 +--------------------+--------------------+
                                      |
                                      v
                     +------------------------------------+
                     |  Stream Multiplexer & Buffer Ring  |
                     +-----------------+------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
+------------------+         +------------------+         +------------------+
| TCP Server #1    |         | TCP Server #2    |         | UDP Broadcast    |
| Port 1456 / 2304 |         | Port 10110       |         | Port 2000        |
| (Raw Stream for  |         | (NMEA 0183 for   |         | (Navionics,      |
| Signal K)        |         | OpenCPN, AquaMap)|         | iNavX, Tablets)  |
+------------------+         +------------------+         +------------------+
```

### 3.1 Supported Output Network Protocols

1. **Yacht Devices RAW Protocol (Default Port 1456 / 2304):**
   * Encapsulates raw CAN frames into human-readable ASCII text lines:
     `hh:mm:ss.ddd R msgid b0 b1 b2 b3 b4 b5 b6 b7`
   * Supported natively by Signal K Server, OpenPlotter, and Expedition 10.
2. **Actisense NGT-1 ASCII / Binary Protocol:**
   * Encapsulates raw PGNs using Actisense binary or BST packet framing.
   * Directly consumed by Signal K (`@signalk/nmea2000-actisense-serial`) and
     CanboatJS.
3. **NMEA 0183 Translation (Default Port 10110):**
   * Converts incoming N2K PGNs and local sensor measurements into standard
     ASCII 0183 sentences:
     * PGN 128267 (Water Depth) $\rightarrow$ `$IIDPT,x.x,x.x*hh`
     * PGN 130306 (Wind Data) $\rightarrow$ `$IIMWV,x.x,R,x.x,K,A*hh`
     * PGN 129029 (GNSS Position) $\rightarrow$ `$GPGGA,...*hh`
     * PGN 127250 (Vessel Heading) $\rightarrow$ `$IIHDG,...*hh`
     * Local BME280 Pressure $\rightarrow$ `$IIMDA,...*hh` or `$IIXDR,...*hh`
   * Required for marine tablet apps that do not natively parse binary NMEA
     2000.
4. **UDP Broadcast Streaming (Default Port 2000):**
   * Transmits converted NMEA 0183 sentences via UDP broadcast
     (`255.255.255.255` or subnet broadcast).
   * Enables zero-configuration discovery on tablets: Navionics Boating
     auto-detects UDP 0183 broadcasts without requiring fixed client IP
     configurations.

### 3.2 Software Components and Library Ecosystem

Building the gateway firmware relies on mature, battle-tested open-source C++
libraries:

* **CAN Bus & NMEA 2000 Stack:**
  * **[NMEA2000 Library][ref-lappalainen-n2k] (Timo Lappalainen):** Core
    protocol handling, dynamic address negotiation (ISO 11783-5), multi-packet
    fast-packet reassembly, and PGN encoding/decoding.
  * **[NMEA2000_esp32][ref-lappalainen-esp32] (Timo Lappalainen):** Hardware
    driver binding the NMEA2000 library to the ESP32 on-chip TWAI peripheral.
* **Sentence Translation:**
  * **[NMEA0183 Library][ref-lappalainen-0183] (Timo Lappalainen):** Creates
    and encodes standard NMEA 0183 ASCII sentences ($IIDPT, $IIMWV, $IIHDG,
    $IIXDR) from binary sensor data.
* **Sensor Drivers:**
  * **Adafruit BME280 / BMP280 Library:** Configures oversampling, reads
    compensated barometric pressure, ambient temperature, and relative humidity
    over I2C.
  * **OneWire & DallasTemperature Libraries:** Manages 1-Wire discovery, ROM
    matching, scratchpad reads, and non-blocking 12-bit temperature conversions
    for DS18B20 probes.
  * **MPU9250 / BNO085 Sensor Libraries:** Implements sensor fusion (quaternion
    to Euler angles) to output stable roll, pitch, and yaw.
* **Network & Sockets:**
  * **ESP32 Arduino WiFi & WiFiUdp:** Manages concurrent SoftAP/Station modes,
    TCP servers for streaming, and UDP datagram broadcasts.

---

## 4. Integration and Client Configuration

Connecting client devices to the DIY gateway matches standard commercial
gateway workflows:

### 4.1 Navionics Boating (iPhone, iPad, Android)

1. Connect the mobile device's Wi-Fi to the gateway's network
   (`Seagram_Gateway`).
2. Open **Navionics Boating**.
3. Navigate to **Menu $\rightarrow$ Connect a Device $\rightarrow$ Add
   Device**.
4. Set the name to `ESP32 N2K Gateway`.
5. Enter IP `192.168.4.1` and Port `2000` (or select UDP). Navionics will
   automatically detect the broadcast stream and display live depth, wind, and
   AIS data overlays on charts.

### 4.2 OpenPlotter and Signal K Server (Raspberry Pi)

1. Connect the Raspberry Pi to the gateway's Wi-Fi network (or configure the
   ESP32 in Station mode to join the boat router).
2. Open the **Signal K Admin Console** at `http://localhost:3000`.
3. Navigate to **Server $\rightarrow$ Data Connections $\rightarrow$ Add**.
4. Configure the connection parameters:
   * **Data Type:** `NMEA 2000`
   * **Enabled:** `Yes`
   * **ID:** `ESP32-Gateway`
   * **NMEA 2000 Source:** `Yacht Devices RAW` (or `Actisense NGT-1 over TCP`)
   * **Connection Type:** `TCP Client`
   * **Server / Host:** `192.168.4.1` (Gateway IP)
   * **Port:** `1456`
5. Click **Apply**. Signal K will begin streaming and parsing all bus PGNs into
   standard JSON delta keys (`environment.depth.belowTransducer`,
   `environment.wind.speedApparent`, `propulsion.mainEngine.temperature`).

### 4.3 OpenCPN (PC, Mac, Linux)

1. Open OpenCPN $\rightarrow$ **Options (Wrench icon) $\rightarrow$ Connections
   $\rightarrow$ Add Connection**.
2. Select **Network**.
3. Protocol: **TCP** (or UDP).
4. Address: `192.168.4.1`, DataPort: `10110`.
5. Check **Receive Input on this Port**.
6. Click **Apply**. OpenCPN's dashboard instrument panels will populate with
   depth, heading, barometric pressure, and wind indicators.

---

## 5. Community Ecosystem, Open-Source Projects, and Social Groups

The open-source marine electronics community maintains an extensive library of
tested firmware, reference designs, and peer troubleshooting networks:

### 5.1 Key Open-Source GitHub Repositories

* **Core Libraries:**
  * [ttlappalainen/NMEA2000][ref-lappalainen-n2k]: Foundation C++ library for
    NMEA 2000 message parsing, packetizing, and address management.
  * [ttlappalainen/NMEA2000_esp32][ref-lappalainen-esp32]: Hardware CAN driver
    adapting Timo's library directly to the ESP32 TWAI peripheral.
  * [ttlappalainen/NMEA0183][ref-lappalainen-0183]: Bidirectional translation
    engine between NMEA 2000 PGNs and legacy NMEA 0183 ASCII sentences.
* **Complete Gateway Implementations:**
  * [AK-Homberger/NMEA2000WifiGateway-with-ESP32][ref-ak-homberger]: A mature,
    full-featured gateway supporting concurrent TCP/UDP streaming, web
    dashboard monitoring, and analog engine sensor inputs.
  * [wellenvogel/esp32-nmea2000][ref-wellenvogel-esp32]: Modular N2K Wi-Fi/USB
    multiplexer developed within the OpenBoatProjects initiative.
  * [SignalK/SensESP][ref-sensesp-main]: Modern sensor development framework
    for ESP32, including native Signal K over WebSocket and N2K gateway
    extensions.

### 5.2 Marine Electronics Developer Communities & Forums

* **[OpenBoatProjects.org][ref-openboatprojects]:** The premier German/European
  open-source marine electronics collective, providing open-hardware schematics
  for ESP32 gateways, isolated CAN transceivers, and multifunction displays.
* **[OpenMarine Community Forum][ref-openmarine-forum]:** Official support
  forum for OpenPlotter, PyPilot, and Signal K integrations with custom ESP32
  nodes.
* **[Yacht Devices Application Guides][ref-yachtd-articles]:** Technical
  articles detailing raw N2K packet formats, Wi-Fi latency mitigation, and
  ground isolation.

### 5.3 Facebook Groups and Social Maker Collectives

* **[OpenSource Marine Electronics (Facebook
  Group)][ref-fb-opensource-marine]:** Active international forum for sailors
  and engineers building custom ESP32 gateways, engine monitors, and Raspberry
  Pi nav stations.
* **[OpenPlotter / Signal K Users (Facebook Group)][ref-fb-openplotter]:**
  Focuses on connecting custom hardware gateways to shipboard servers and
  tablet apps.
* **[Boat Electronics & Marine DIY (Facebook Group)][ref-fb-boatelectronics]:**
  Broad boating community troubleshooting NMEA 2000 drop cables, transceiver
  schematics, and wireless bridging setups.

---

## 6. Troubleshooting and Diagnostic Reference

| Symptom | Probable Cause | Verification & Corrective Action |
| :--- | :--- | :--- |
| **No CAN messages received (`N2K.ParseMessages() == 0`)** | CAN_TX and CAN_RX swapped, or missing bus power | Invert CAN TX/RX pin definitions. Verify +12V rail and $60\,\Omega$ bus resistance between CAN_H and CAN_L. |
| **ESP32 resets continuously when engine starts** | Non-isolated ground loop or high inductive spike | Replace non-isolated transceiver with galvanically isolated unit (ISO1050/CA-IS3050G). Install 0.5A fast-blow fuse on 12V supply. |
| **Navionics drops connection intermittently** | Excessive TCP buffer bloat or high Wi-Fi retransmission | Switch tablet feed from TCP to UDP broadcast (Port 2000). Set ESP32 Wi-Fi TX power to maximum (`WiFi.setTxPower(WIFI_POWER_19_5dBm)`). |
| **Signal K reports CRC / Framing Errors** | CAN transceiver baud rate mismatch | Verify that the TWAI controller bit timing is locked to 250 kbps with 29-bit extended framing. |
| **High voltage on ESP32 3.3V pin** | Defective buck regulator or 5V connected to 3.3V logic | Measure regulator output with multimeter before attaching ESP32. Ensure buck output is calibrated to 5.0V on VBUS (or 3.3V on 3V3). |
| **1-Wire Temperature Probes read -127°C** | Missing pull-up resistor or severed data line | Verify $4.7\,\text{k}\Omega$ pull-up resistor between 1-Wire DQ data line and 3.3V power rail. |
| **I2C Sensor detection fails (NACK on bus scan)** | SCL/SDA lines swapped or insufficient pull-up | Check SDA and SCL pin assignments. Ensure lines have pull-ups enabled internally or on sensor breakout board. |

---

## 7. References and Documentation

* [Yacht Devices YDWG-02 Wi-Fi Gateway Specification][ref-ydwg02-doc]:
  Commercial reference device specifications and network architecture.
* [NMEA 2000 Protocol Specification and Engineering Guide][ref-nmea2000-spec]:
  Comprehensive internal guide to N2K physical layer, framing, and PGNs.
* [Espressif ESP32 Technical Reference Manual (TWAI
  Controller)][ref-esp32-twai]: Official Espressif silicon register reference
  for the on-chip CAN controller.
* [Texas Instruments SN65HVD230 3.3V CAN Transceiver
  Datasheet][ref-sn65hvd230-ti]: Electrical specifications for 3.3V
  non-isolated CAN bus physical interface.
* [Texas Instruments ISO1050 Galvanically Isolated
  Transceiver][ref-iso1050-ti]: Technical reference for isolated CAN
  communications in marine environments.
* [Pololu Step-Down Voltage Regulators][ref-pololu-buck]: High-efficiency
  marine power regulation modules.
* [M5Stack Atom Lite Development Kit][ref-m5stack-atom]: Ultra-compact ESP32
  development module.
* [M5Stack Atomic PortABC Base][ref-m5stack-portabc]: Port expansion base
  breaking out Port A (I2C), Port B (GPIO), and Port C (UART).
* [M5Stack CANBus Unit (CA-IS3050G)][ref-m5stack-canunit]: Isolated
  marine-capable CAN bus transceiver unit with screw terminals.
* [M5Stack ENV IV Unit (SHT40 + BMP280)][ref-m5stack-env4]: Compact I2C
  environmental sensor module.
* [M5Stack IMU Unit][ref-m5stack-imu]: 6-axis / 9-axis attitude and motion
  sensor module.
* [M5Stack Grove Hub][ref-m5stack-hub]: Passive 1-to-3 I2C Grove splitter.
* [Sailor Hat with ESP32 (SH-ESP32)][ref-sh-esp32]: Open-source marine ESP32
  development board with isolated CAN and wide-input power supply.
* [Timo Lappalainen NMEA2000 Library on GitHub][ref-lappalainen-n2k]: Primary
  C++ library for N2K protocol handling on microcontrollers.
* [Timo Lappalainen NMEA2000_esp32 Hardware Driver][ref-lappalainen-esp32]:
  ESP32 TWAI integration layer for NMEA2000.
* [Timo Lappalainen NMEA0183 Library][ref-lappalainen-0183]: NMEA 0183 protocol
  generation and parsing library.
* [AK-Homberger NMEA2000 Wi-Fi Gateway with ESP32][ref-ak-homberger]:
  Open-source firmware for ESP32 N2K to Wi-Fi bridging.
* [wellenvogel/esp32-nmea2000 Gateway Suite][ref-wellenvogel-esp32]:
  OpenBoatProjects multiplexer and gateway software.
* [Signal K SensESP Sensor Framework][ref-sensesp-main]: Open-source marine
  sensor and gateway development toolkit for ESP32.
* [OpenBoatProjects.org Marine Maker Hub][ref-openboatprojects]: European
  marine electronics maker portal.
* [OpenMarine Community Forum][ref-openmarine-forum]: Support forums for
  open-source marine computing and navigation.
* [Yacht Devices Technical Application Notes][ref-yachtd-articles]: Network
  bridging and marine diagnostics documentation.
* [Maretron NMEA 2000 Cable and Wiring Technical Guide][ref-maretron-cabling]:
  Field-attachable connectors, Micro-C pinouts, and drop cable limits.
* [Actisense NMEA 2000 Ultimate Networking Guide][ref-actisense-guide]: Marine
  backbone design, power budgeting, and LEN rules.
* [Facebook OpenSource Marine Electronics Group][ref-fb-opensource-marine]:
  Peer community for DIY boat electronics projects.
* [Facebook OpenPlotter & Signal K Users Group][ref-fb-openplotter]: Community
  group for OpenPlotter hardware and gateway setups.
* [Facebook Boat Electronics & DIY Group][ref-fb-boatelectronics]: Community
  discussions on marine wiring, gateways, and sensor installations.

[ref-ydwg02-doc]: ../parts/YDWG-02.md [ref-nmea2000-spec]: nmea2000.md
[ref-espressif-esp32]: https://www.espressif.com/en/products/socs/esp32
[ref-esp32-twai]:
https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf
[ref-sn65hvd230-ti]: https://www.ti.com/product/SN65HVD230 [ref-iso1050-ti]:
https://www.ti.com/product/ISO1050 [ref-pololu-buck]:
https://www.pololu.com/category/136/voltage-regulators [ref-m5stack-atom]:
https://docs.m5stack.com/en/core/atom_lite [ref-m5stack-portabc]:
https://docs.m5stack.com/en/atom/atomic_portabc [ref-m5stack-canunit]:
https://docs.m5stack.com/en/unit/can [ref-m5stack-env4]:
https://docs.m5stack.com/en/unit/env4 [ref-m5stack-imu]:
https://docs.m5stack.com/en/unit/imu [ref-m5stack-hub]:
https://docs.m5stack.com/en/unit/hub [ref-sh-esp32]:
https://hatlabs.github.io/sh-esp32/ [ref-lappalainen-n2k]:
https://github.com/ttlappalainen/NMEA2000 [ref-lappalainen-esp32]:
https://github.com/ttlappalainen/NMEA2000_esp32 [ref-lappalainen-0183]:
https://github.com/ttlappalainen/NMEA0183 [ref-ak-homberger]:
https://github.com/AK-Homberger/NMEA2000WifiGateway-with-ESP32
[ref-wellenvogel-esp32]: https://github.com/wellenvogel/esp32-nmea2000
[ref-sensesp-main]: https://github.com/SignalK/SensESP [ref-openboatprojects]:
https://open-boat-projects.org/ [ref-openmarine-forum]:
https://forum.openmarine.net/ [ref-yachtd-articles]:
https://www.yachtd.com/products/wifi_gateway.html [ref-maretron-cabling]:
https://www.maretron.com/support/knowledgebase/phpkbv7/article.php?id=38
[ref-actisense-guide]: https://actisense.com/education-centre/nmea-2000-ebook/
[ref-fb-opensource-marine]:
https://www.facebook.com/groups/opensource.marine.electronics/
[ref-fb-openplotter]: https://www.facebook.com/groups/openplotter/
[ref-fb-boatelectronics]: https://www.facebook.com/groups/boatelectronics/
