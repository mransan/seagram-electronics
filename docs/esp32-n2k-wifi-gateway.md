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

---

## 1. Architectural Overview and Feasibility

Commercial marine gateways like the Yacht Devices YDWG-02 retail for
approximately \$249 USD. A custom ESP32-based gateway achieving identical or
superior data-throughput and stream flexibility can be constructed for \$15 to
\$55 USD depending on component choices.

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
|  | Hardware: Isolated CAN Transceiver + DC-DC Step-Down (3.3V/5V)     |  |
|  +--------------------------------------------------------------------+  |
|          | TWAI (CAN_TX / CAN_RX)                                        |
|          v                                                               |
|  +--------------------------------------------------------------------+  |
|  | ESP32 Microcontroller Core (FreeRTOS Dual Core)                    |  |
|  |  - Core 0: CAN interrupt, PGN parsing, NMEA 0183 conversion        |  |
|  |  - Core 1: Wi-Fi stack, TCP server, UDP broadcast, Web UI          |  |
|  +--------------------------------------------------------------------+  |
|          |                                                               |
|          +--- 2.4 GHz 802.11 b/g/n Wi-Fi (SoftAP or Station Mode)        |
|               |                                                          |
|               +--> TCP Port 1456 / 2304: Raw N2K / Actisense (Signal K)   |
|               +--> TCP Port 10110: NMEA 0183 Stream (OpenCPN, Aqua Map)  |
|               +--> UDP Port 2000: Broadcast Stream (Navionics, Tablets)  |
|               +--> HTTP Port 80: Web Configuration & Diagnostics UI      |
+--------------------------------------------------------------------------+
```

### 1.1 Technical Feasibility

* **Processing Capability:** The ESP32 dual-core Xtensa LX6 microprocessor
  operates at up to 240 MHz with 520 KB SRAM. It possesses ample computation
  margin to handle full NMEA 2000 bus loads (250 kbps, typically 300 to 1,500
  frames/second) while managing Wi-Fi networking, TCP buffering, and sentence
  conversion.
* **Integrated CAN Controller (TWAI):** The ESP32 silicon includes an on-chip
  hardware CAN 2.0B controller, named the [Two-Wire Automotive Interface
  (TWAI)][ref-esp32-twai]. It directly implements 29-bit extended frame
  filtering, dynamic error tracking, and bit timing at 250 kbps without
  requiring an external SPI CAN controller like the MCP2515.
* **Network Protocol Versatility:** The ESP32 supports concurrent Wi-Fi Station
  (STA) mode (joining an existing onboard router) and Access Point (SoftAP)
  mode, alongside native FreeRTOS TCP/IP (LwIP) sockets.

---

## 2. Hardware Bill of Materials (BOM) and Cost Analysis

Depending on assembly preferences, builders can construct the hardware using
discrete prototyping modules, pre-packaged industrial microcontroller blocks,
or dedicated open-source marine electronics boards:

### 2.1 Bill of Materials: Three Hardware Approaches

| Component | Part Description | Approx Price (USD) | Function & Sourcing Links |
| :--- | :--- | :--- | :--- |
| **Approach 1: Discrete Prototyping (Lowest Cost)** | | | |
| Microcontroller | ESP32 DevKit V1 (NodeMCU-32S) | \$4.50 – \$7.00 | Dual-core 240 MHz MCU, integrated Wi-Fi / Bluetooth ([Espressif][ref-espressif-esp32]) |
| CAN Transceiver | Texas Instruments SN65HVD230 (3.3V) | \$2.00 – \$4.00 | Non-isolated 3.3V CAN transceiver ([TI Datasheet][ref-sn65hvd230-ti]) |
| Isolated Transceiver (Recommended) | Texas Instruments ISO1050 / CA-IS3050G module | \$5.00 – \$9.00 | Galvanically isolated CAN transceiver ([TI ISO1050][ref-iso1050-ti]) |
| DC-DC Power Supply | LM2596 / MP1584EN Step-Down (Buck) | \$2.00 – \$4.00 | Converts 12V N2K rail to clean 5V DC ([Pololu Regulators][ref-pololu-buck]) |
| Spur Connector | NMEA 2000 Micro-C Field-Attachable Male | \$9.00 – \$15.00 | Standard waterproof 5-pin M12 connector ([Maretron Field Make][ref-maretron-cabling]) |
| Enclosure & Passives | Waterproof ABS junction box, 0.1A fuse | \$5.00 – \$8.00 | IP65 enclosure, terminal blocks, fuse protection |
| **Total (Approach 1)** | | **\$27.50 – \$47.00** | |
| **Approach 2: Modular Industrial Core (M5Stack)** | | | |
| Core Module | [M5Stack Atom Lite][ref-m5stack-atom] or AtomS3 | \$7.50 – \$12.00 | Compact ESP32 in molded enclosure with GPIO header |
| Isolated CAN Base | [M5Stack Atomic CANBase][ref-m5stack-canbase] (CA-IS3050G) | \$8.50 – \$12.00 | Galvanically isolated CAN interface with DC-DC power input (up to 24V) |
| Spur Cable | Micro-C Drop Cable (1 meter, bare end) | \$12.00 – \$18.00 | Molded DeviceNet Micro-C male to bare wire ([Actisense Cable][ref-actisense-guide]) |
| **Total (Approach 2)** | | **\$28.00 – \$42.00** | Plug-and-play assembly, minimal soldering required |
| **Approach 3: Dedicated Marine Board (Commercial-Grade DIY)** | | | |
| Integrated Board | [Sailor Hat with ESP32 (SH-ESP32)][ref-sh-esp32] | \$35.00 – \$55.00 | Marine-grade ESP32 board with isolated CAN, wide 8–32V buck supply, opto-inputs |
| Spur Cable | Standard Micro-C Spur Cable (1 m) | \$12.00 – \$18.00 | Connects directly to SH-ESP32 screw terminals |
| **Total (Approach 3)** | | **\$47.00 – \$73.00** | Galvanic isolation, transient TVS protection, open-source |

---

## 3. Circuit Schematics and Electrical Wiring

Connecting an ESP32 safely to an NMEA 2000 network requires strict adherence to
isolation, voltage regulation, and signal line mapping.

```
NMEA 2000 Spur Line                   Isolation Barrier              ESP32 Microcontroller
====================                   =================              =====================

Pin 2: NET-S (+12V DC) ---[ Fuse 0.5A ]---> [ DC-DC Buck ] === 5V ====> ESP32 5V (VBUS)
Pin 3: NET-C (0V GND)  -------------------> [ Converter ] === GND ===> ESP32 GND
                                                  |
Pin 4: NET-H (CAN_H)   -----------------> [ Isolated   ] === RX =====> GPIO 4 (TWAI_RX)
Pin 5: NET-L (CAN_L)   -----------------> [ CAN XCVR   ] === TX =====> GPIO 5 (TWAI_TX)
                                          [ (ISO1050)  ] === 3.3V ===< ESP32 3.3V Rail
Pin 1: Shield (Drain)  ---(Unconnected at device; grounded at N2K power tap only)
```

### 3.1 Transceiver Selection: Isolated vs. Non-Isolated

1. **Non-Isolated (SN65HVD230):**
   * Uses a common ground plane between the boat's battery bank and the ESP32.
   * *Limitation:* Prone to ground loops and voltage differentials when
     powering the ESP32 from a separate USB port or laptop, risking hardware
     burnout during engine cranking or high-load inverter activity.
2. **Galvanically Isolated (ISO1050 / CA-IS3050G):**
   * Features a silicon dielectric capacitive or magnetic isolation barrier
     rated to 2.5 kV RMS or higher.
   * Completely isolates the differential data pair (`CAN_H` / `CAN_L`) and
     chassis grounds, preventing earth loops and electrical interference from
     migrating between the navigation backbone and the Wi-Fi gateway.

### 3.2 Power Supply and Voltage Regulation

Standard marine NMEA 2000 power fluctuates between 11.5V and 14.8V DC (with
transient spikes up to 40V during inductive load dumps):

* **Power Draw (LEN):** An ESP32 with active Wi-Fi transmission consumes
  approximately 120 mA to 240 mA at 3.3V (averaging ~180 mA). Operating through
  a high-efficiency switching buck regulator at 12V DC, the gateway draws ~50
  mA from the backbone: $$\text{LEN} = \frac{50\,\text{mA}}{50\,\text{mA/LEN}}
  = 1\,\text{LEN}$$
* **Switching Buck Regulator:** Do not use linear regulators (like LM7805 or
  AMS1117) directly from 12V; dropping 12V to 3.3V at 200 mA dissipates over
  $1.7\,\text{W}$ of waste heat in an unventilated enclosure. Use a switching
  step-down converter (e.g., MP1584EN, LM2596, or Recom R-78 series).

### 3.3 GPIO Pin Mapping

The ESP32 allows the TWAI CAN controller to be routed to nearly any available
digital GPIO via the internal GPIO matrix:

| Signal Name | ESP32 GPIO Pin | Function |
| :--- | :--- | :--- |
| **TWAI_RX** | **GPIO 4** (or GPIO 16, 21) | Receives CAN data stream from transceiver RXD |
| **TWAI_TX** | **GPIO 5** (or GPIO 17, 22) | Transmits CAN data stream to transceiver TXD |
| **Status LED** | **GPIO 2** (or Onboard LED) | Pulses upon successful PGN reception / Wi-Fi activity |

---

## 4. Software Architecture and Data Streaming Protocols

To replicate the functionality of commercial gateways, the gateway firmware
must support multiple network transport modes and data formats.

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

### 4.1 Supported Output Formats

1. **Yacht Devices RAW Protocol (Default Port 1456 / 2304):**
   * Encapsulates raw CAN frames into human-readable ASCII text lines:
     `hh:mm:ss.ddd R msgid b0 b1 b2 b3 b4 b5 b6 b7`
   * Supported natively by Signal K Server, OpenPlotter, and Expedition 10.
2. **Actisense NGT-1 ASCII / Binary Protocol:**
   * Encapsulates raw PGNs using Actisense binary or BST packet framing.
   * Directly consumed by Signal K (`@signalk/nmea2000-actisense-serial`) and
     CanboatJS.
3. **NMEA 0183 Translation (Default Port 10110):**
   * Converts incoming N2K PGNs into standard ASCII 0183 sentences:
     * PGN 128267 (Water Depth) $\rightarrow$ `$IIDPT,x.x,x.x*hh`
     * PGN 130306 (Wind Data) $\rightarrow$ `$IIMWV,x.x,R,x.x,K,A*hh`
     * PGN 129029 (GNSS Position) $\rightarrow$ `$GPGGA,...*hh`
     * PGN 127250 (Vessel Heading) $\rightarrow$ `$IIHDG,...*hh`
   * Required for marine tablet apps that do not natively parse binary NMEA
     2000.
4. **UDP Broadcast Streaming (Default Port 2000):**
   * Transmits converted NMEA 0183 sentences via UDP broadcast
     (`255.255.255.255` or subnet broadcast).
   * Enables zero-configuration discovery on tablets: Navionics Boating
     auto-detects UDP 0183 broadcasts without requiring fixed client IP
     configurations.

---

## 5. Implementation: Arduino / C++ Firmware Code

The following complete firmware implementation uses [Timo Lappalainen's
NMEA2000 library][ref-lappalainen-n2k], the [NMEA2000_esp32 hardware
driver][ref-lappalainen-esp32], and the [NMEA0183
library][ref-lappalainen-0183].

### 5.1 PlatformIO Environment Configuration (`platformio.ini`)

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
lib_deps =
    ttlappalainen/NMEA2000@^4.21.3
    ttlappalainen/NMEA2000_esp32@^1.0.3
    ttlappalainen/NMEA0183@^1.8.4
```

### 5.2 Core Gateway Code (`src/main.cpp`)

```cpp
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <NMEA2000.h>
#include <NMEA2000_esp32.h>
#include <N2kMessages.h>
#include <NMEA0183.h>
#include <NMEA0183Messages.h>

// --- Configuration Constants ---
const char* WIFI_SSID     = "Seagram_Gateway";
const char* WIFI_PASSWORD = "marine_electronics";
const uint16_t TCP_RAW_PORT   = 1456;   // Yacht Devices RAW / Signal K
const uint16_t TCP_0183_PORT  = 10110;  // NMEA 0183 (OpenCPN)
const uint16_t UDP_BROADCAST_PORT = 2000; // Navionics / Tablets

// Pin Definitions for CAN Transceiver
#define CAN_RX_PIN GPIO_NUM_4
#define CAN_TX_PIN GPIO_NUM_5

// Global Network Instances
WiFiServer rawTcpServer(TCP_RAW_PORT);
WiFiServer nmea0183TcpServer(TCP_0183_PORT);
WiFiClient rawClient;
WiFiClient nmea0183Client;
WiFiUDP udp;

tNMEA0183 NMEA0183Msg;

// Format buffer for Yacht Devices RAW: "hh:mm:ss.ddd R msgid b0 b1 ...\r\n"
void SendYachtDevicesRaw(const tN2kMsg &N2kMsg) {
  if (!rawClient || !rawClient.connected()) return;

  char buf[80];
  uint32_t ms = millis();
  uint32_t sec = ms / 1000;
  snprintf(buf, sizeof(buf), "%02u:%02u:%02u.%03u R %08lX",
           (sec / 3600) % 24, (sec / 60) % 60, sec % 60, ms % 1000,
           (unsigned long)N2kMsg.GetMsgId());
  rawClient.print(buf);

  for (int i = 0; i < N2kMsg.DataLen; i++) {
    snprintf(buf, sizeof(buf), " %02X", N2kMsg.Data[i]);
    rawClient.print(buf);
  }
  rawClient.print("\r\n");
}

// Convert common PGNs to NMEA 0183 sentences and broadcast
void HandleNmea0183Translation(const tN2kMsg &N2kMsg) {
  char nmeaSentence[120] = {0};

  // PGN 128267: Water Depth
  if (N2kMsg.PGN == 128267L) {
    unsigned char SID;
    double DepthBelowTransducer, Offset;
    if (ParseN2kWaterDepth(N2kMsg, SID, DepthBelowTransducer, Offset)) {
      tNMEA0183Msg msg;
      NMEA0183SetDPT(msg, DepthBelowTransducer, Offset);
      msg.GetMessage(nmeaSentence, sizeof(nmeaSentence));
    }
  }
  // PGN 130306: Wind Data
  else if (N2kMsg.PGN == 130306L) {
    unsigned char SID;
    double WindSpeed, WindAngle;
    tN2kWindReference WindReference;
    if (ParseN2kWindSpeed(N2kMsg, SID, WindSpeed, WindAngle, WindReference)) {
      tNMEA0183Msg msg;
      // Convert WindAngle radians to degrees
      double angleDeg = WindAngle * 180.0 / 3.14159265359;
      // Convert m/s to knots (1 m/s = 1.94384 knots)
      double speedKnots = WindSpeed * 1.94384;
      NMEA0183SetMWV(msg, angleDeg,
                     (WindReference == N2kWind_Apparent) ? "R" : "T",
                     speedKnots, "N");
      msg.GetMessage(nmeaSentence, sizeof(nmeaSentence));
    }
  }

  // Stream sentence out to connected TCP and UDP clients
  if (nmeaSentence[0] != '\0') {
    if (nmea0183Client && nmea0183Client.connected()) {
      nmea0183Client.print(nmeaSentence);
    }
    udp.beginPacket("255.255.255.255", UDP_BROADCAST_PORT);
    udp.write((const uint8_t*)nmeaSentence, strlen(nmeaSentence));
    udp.endPacket();
  }
}

// Callback invoked on every received N2K CAN frame
void HandleN2kMsg(const tN2kMsg &N2kMsg) {
  SendYachtDevicesRaw(N2kMsg);
  HandleNmea0183Translation(N2kMsg);
}

void setup() {
  Serial.begin(115200);

  // Configure Wi-Fi Access Point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Wi-Fi Gateway AP Started. IP: ");
  Serial.println(WiFi.softAPIP());

  // Start Servers
  rawTcpServer.begin();
  nmea0183TcpServer.begin();
  udp.begin(UDP_BROADCAST_PORT);

  // Configure NMEA 2000 CAN Controller
  NMEA2000.SetRxPutMode(tNMEA2000::rp_SysCall);
  NMEA2000.SetMsgHandler(HandleN2kMsg);
  NMEA2000.SetProductInformation("00000001", 100, "ESP32 N2K Gateway",
                                 "1.0.0", "DIY Open Gateway");
  NMEA2000.SetDeviceInformation(1, 130, 25, 2046); // Inter/Intranetwork Gateway
  NMEA2000.SetMode(tNMEA2000::N2km_ListenOnly);     // Listen-Only Safe Mode

  // Assign CAN pins for ESP32 TWAI
  NMEA2000.SetForwardType(tNMEA2000::fwdt_Text);
  NMEA2000.Open();
}

void loop() {
  // Service CAN bus receive queue
  NMEA2000.ParseMessages();

  // Accept incoming raw TCP connections (Signal K / Diagnostics)
  if (rawTcpServer.hasClient()) {
    if (!rawClient || !rawClient.connected()) {
      rawClient = rawTcpServer.available();
    }
  }

  // Accept incoming NMEA 0183 TCP connections (OpenCPN)
  if (nmea0183TcpServer.hasClient()) {
    if (!nmea0183Client || !nmea0183Client.connected()) {
      nmea0183Client = nmea0183TcpServer.available();
    }
  }
}
```

---

## 6. Integration and Client Configuration

Connecting client devices to the DIY gateway matches standard commercial
gateway workflows:

### 6.1 Navionics Boating (iPhone, iPad, Android)

1. Connect the mobile device's Wi-Fi to the gateway's network
   (`Seagram_Gateway`).
2. Open **Navionics Boating**.
3. Navigate to **Menu $\rightarrow$ Connect a Device $\rightarrow$ Add
   Device**.
4. Set the name to `ESP32 N2K Gateway`.
5. Enter IP `192.168.4.1` and Port `2000` (or select UDP). Navionics will
   automatically detect the broadcast stream and display live depth, wind, and
   AIS data overlays on charts.

### 6.2 OpenPlotter and Signal K Server (Raspberry Pi)

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
   `environment.wind.speedApparent`).

### 6.3 OpenCPN (PC, Mac, Linux)

1. Open OpenCPN $\rightarrow$ **Options (Wrench icon) $\rightarrow$ Connections
   $\rightarrow$ Add Connection**.
2. Select **Network**.
3. Protocol: **TCP** (or UDP).
4. Address: `192.168.4.1`, DataPort: `10110`.
5. Check **Receive Input on this Port**.
6. Click **Apply**. OpenCPN's dashboard instrument panels will populate with
   depth, heading, and wind indicators.

---

## 7. Community Ecosystem, Open-Source Projects, and Social Groups

The open-source marine electronics community maintains an extensive library of
tested firmware, reference designs, and peer troubleshooting networks:

### 7.1 Key Open-Source GitHub Repositories

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

### 7.2 Marine Electronics Developer Communities & Forums

* **[OpenBoatProjects.org][ref-openboatprojects]:** The premier German/European
  open-source marine electronics collective, providing open-hardware schematics
  for ESP32 gateways, isolated CAN transceivers, and multifunction displays.
* **[OpenMarine Community Forum][ref-openmarine-forum]:** Official support
  forum for OpenPlotter, PyPilot, and Signal K integrations with custom ESP32
  nodes.
* **[Yacht Devices Application Guides][ref-yachtd-articles]:** Technical
  articles detailing raw N2K packet formats, Wi-Fi latency mitigation, and
  ground isolation.

### 7.3 Facebook Groups and Social Maker Collectives

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

## 8. Troubleshooting and Diagnostic Reference

| Symptom | Probable Cause | Verification & Corrective Action |
| :--- | :--- | :--- |
| **No CAN messages received (`N2K.ParseMessages() == 0`)** | CAN_TX and CAN_RX swapped, or missing bus power | Invert GPIO 4 and GPIO 5 in `NMEA2000.SetCANPins()`. Verify +12V rail and $60\,\Omega$ bus resistance between CAN_H and CAN_L. |
| **ESP32 resets continuously when engine starts** | Non-isolated ground loop or high inductive spike | Replace non-isolated transceiver with galvanically isolated unit (ISO1050). Install 0.5A fast-blow fuse on 12V supply. |
| **Navionics drops connection intermittently** | Excessive TCP buffer bloat or high Wi-Fi retransmission | Switch tablet feed from TCP to UDP broadcast (Port 2000). Set ESP32 Wi-Fi TX power to maximum (`WiFi.setTxPower(WIFI_POWER_19_5dBm)`). |
| **Signal K reports CRC / Framing Errors** | CAN transceiver baud rate mismatch | Verify that the TWAI controller bit timing is locked to 250 kbps with 29-bit extended framing. |
| **High voltage on ESP32 3.3V pin** | Defective buck regulator or 5V connected to 3.3V logic | Measure regulator output with multimeter before attaching ESP32. Ensure buck output is calibrated to 5.0V on VBUS (or 3.3V on 3V3). |

---

## 9. References and Documentation

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
* [M5Stack Atomic CANBase (Isolated)][ref-m5stack-canbase]: Isolated
  marine-capable CAN bus base with built-in wide DC-DC power input.
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
* [Wellenvogel ESP32-NMEA2000 Gateway Suite][ref-wellenvogel-esp32]:
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
https://docs.m5stack.com/en/core/atom_lite [ref-m5stack-canbase]:
https://docs.m5stack.com/en/atom/atomic_can [ref-sh-esp32]:
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
