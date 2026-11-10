# Marine I2C Barometric Pressure Sensors: Architecture & Availability Guide

This engineering guide evaluates digital barometric air pressure sensors for
marine environmental telemetry and integration with the ESP32-based **HALMET**
gateway. It details sensing architectures, media-protective packaging
(gel-filled vs. open-cavity), precision performance, I2C bus integration, and
real-world European stock availability across authorized distributors.

---

## 1. Marine Operating Environment & Why Sensor Packaging Matters

Unlike consumer electronics or indoor weather stations, boat electronics
operate in harsh marine atmospheres characterized by:
* High relative humidity and continuous salt-air exposure.
* Condensation cycles during diurnal cabin temperature shifts.
* Potential bilge or locker water splashes.

### 1.1 Open-Cavity MEMS Sensors (Vulnerable to Marine Failure)
Standard MEMS barometric pressure sensors (such as the classic Bosch
**BMP280**, **BMP388**, or **BME280**) use an open vent hole in their metal lid
exposing the bare silicon piezoresistive diaphragm directly to the ambient air.
Over 1–2 marine seasons, moisture deposition, salt crystallization, and
atmospheric contaminants cause zero-point drift, measurement degradation, or
physical membrane corrosion unless enclosed in a sealed chamber with an ePTFE
(Gore-Tex) breathable membrane patch.

### 1.2 Gel-Protected MEMS Sensors (Marine Grade)
Ruggedized marine barometers (such as the **Bosch BMP384**, **Bosch BMP585**,
**Infineon DPS368**, and **ST LPS35HW / LPS33HW**) encapsulate the sensing
cavity with a specialized inert silicone gel.
* **Working Principle:** The flexible gel hermetically seals the MEMS diaphragm
  from corrosive salt ions, water droplets, and dust, while faithfully
  transmitting hydrostatic and pneumatic pressure changes to the piezoresistive
  bridge.
* **Outcome:** Provides long-term reliability without drifting when exposed to
  marine air or water splashes.

---

## 2. Sensor Comparative Technical Specifications

| Sensor IC | Manufacturer | Protective Design | RMS Noise (Resolution) | Relative Accuracy | Absolute Accuracy | I2C Address (7-bit) | Operating Pressure |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BMP384** | Bosch Sensortec | **Gel-filled cavity** (Splash/humidity proof) | $0.08\,\text{Pa}$ ($\approx 0.0008\,\text{hPa}$) | $\pm 0.09\,\text{hPa}$ ($\pm 9\,\text{Pa}$) | $\pm 0.5\,\text{hPa}$ | `0x77` (or `0x76`) | 300 to 1250 hPa |
| **BMP585** | Bosch Sensortec | **Gel-filled cavity** (IPX8, salt/chemical proof) | $0.08\,\text{Pa}$ ($\approx 0.0008\,\text{hPa}$) | $\pm 0.06\,\text{hPa}$ ($\pm 6\,\text{Pa}$) | $\pm 0.3\,\text{hPa}$ | `0x47` (or `0x46`) | 300 to 1250 hPa |
| **LPS35HW** | STMicroelectronics | **Gel-filled ceramic** (Water-resistant, 10 bar) | $0.75\,\text{Pa}$ ($\approx 0.0075\,\text{hPa}$) | $\pm 0.10\,\text{hPa}$ ($\pm 10\,\text{Pa}$) | $\pm 0.5\,\text{hPa}$ | `0x5D` (or `0x5C`) | 260 to 1260 hPa |
| **LPS33HW** | STMicroelectronics | **Gel-filled + O-ring metal nozzle** | $0.75\,\text{Pa}$ ($\approx 0.0075\,\text{hPa}$) | $\pm 0.10\,\text{hPa}$ ($\pm 10\,\text{Pa}$) | $\pm 0.5\,\text{hPa}$ | `0x5D` (or `0x5C`) | 260 to 1260 hPa |
| **DPS368** | Infineon Technologies | **Gel-filled package** (IPx8, 50 m waterproof) | $0.50\,\text{Pa}$ ($\approx 0.0050\,\text{hPa}$) | $\pm 0.06\,\text{hPa}$ ($\pm 6\,\text{Pa}$) | $\pm 1.0\,\text{hPa}$ | `0x77` (or `0x76`) | 300 to 1200 hPa |
| **BMP388** | Bosch Sensortec | Open vent cavity (Bare silicon) | $0.08\,\text{Pa}$ ($\approx 0.0008\,\text{hPa}$) | $\pm 0.08\,\text{hPa}$ ($\pm 8\,\text{Pa}$) | $\pm 0.5\,\text{hPa}$ | `0x77` (or `0x76`) | 300 to 1250 hPa |
| **BME280** | Bosch Sensortec | Open vent cavity (Temp + Humid + Press) | $0.20\,\text{Pa}$ ($\approx 0.0020\,\text{hPa}$) | $\pm 0.12\,\text{hPa}$ ($\pm 12\,\text{Pa}$) | $\pm 1.0\,\text{hPa}$ | `0x76` (or `0x77`) | 300 to 1100 hPa |

---

## 3. European Sourcing & Stock Availability (Qwiic / STEMMA QT Breakouts)

While raw sensor ICs (such as the bare 8-pin LGA DPS368XTSA1 on RS Components)
are widely stocked, soldering a $2.0 \times 2.5\,\text{mm}$ chip requires
stencil reflow equipment. For clean marine electrical panel assembly,
pre-assembled breakout boards with standard 2.54 mm headers or SparkFun Qwiic /
Adafruit STEMMA QT 4-pin JST-SH connectors are preferred.

Below is the verified stock status across European and international
distributors (e.g. Mouser France, DigiKey Europe, RS Components, GoTronic):

### 3.1 Bosch BMP384 Breakouts
* **Primary Board:** **SparkFun Pressure Sensor - BMP384 (Qwiic)** (SKU:
  `SEN-19662`)
* **Physical Connectors:** Dual SparkFun Qwiic (JST-SH) connectors + 0.1"
  through-holes.
* **Marine Suitability:** High. Gel-filled cavity designed for harsh/humid
  environments.
* **EU Distributor Stock:**
  * **Mouser France (`mouser.fr`):** Regularly stocked (Mouser part:
    `474-SEN-19662`).
  * **DigiKey Europe (`digikey.fr`):** In stock with direct EU shipping.
  * **Local French Retailers (GoTronic / Kubii):** Special order or low stock;
    Mouser/DigiKey is the most reliable supplier.

### 3.2 Bosch BMP585 Breakouts
* **Primary Boards:**
  * **DFRobot Fermion: BMP585 Breakout** (SKU: `SEN0666`)
  * **DFRobot Gravity: BMP585 Sensor Module** (SKU: `SEN0664`)
* **Physical Connectors:** 2.54 mm solder pin header (Fermion) or 4-pin Gravity
  PH2.0 connector (Gravity).
* **Marine Suitability:** Outstanding. Next-generation IPX8 gel protection
  resistant to liquid water and chemicals with industry-leading 1 cm noise
  resolution.
* **EU Distributor Stock:**
  * **GoTronic France (`gotronic.fr`):** In stock in France. Code `39527`
    (SEN0664, €15.90 TTC) and Code `39529` (SEN0666, €12.30 TTC).
  * **Mouser France (`mouser.fr`):** In stock. Mouser part `426-SEN0664` and
    `426-SEN0666`.

### 3.3 STMicroelectronics LPS35HW / LPS33HW Breakouts
* **Primary Boards:**
  * **Adafruit LPS35HW STEMMA QT / Qwiic** (Adafruit PID: `4258`)
  * **Adafruit LPS33HW STEMMA QT with Port Nozzle** (Adafruit PID: `3424`)
* **Physical Connectors:** Dual STEMMA QT / Qwiic (JST-SH 4-pin) connectors +
  0.1" through-holes.
* **Marine Suitability:** Very High. Protective gel bath inside a rugged
  ceramic package. The LPS33HW variant includes a metal nozzle allowing tubing
  connection to an external air vent or sealed chamber.
* **EU Distributor Stock:**
  * **GoTronic France (`gotronic.fr`):** In stock in France. Code `36398`
    (ADA4258, €19.80 TTC).
  * **Mouser France / DigiKey Europe:** Broadly stocked with large inventory.

### 3.4 Infineon DPS368 (Status Note)
* **Raw IC Chip (`DPS368XTSA1`):** In stock at RS Components France (Code:
  `236-3647`, ~€2.16 HT) and Mouser/DigiKey.
* **Evaluation Breakout Board (`S2GOPRESSUREDPS368TOBO1`):** **Discontinued /
  End of Life** by the manufacturer.
* **Evaluation Kit (`KITDPS3682GOTOBO1`):** Stocked at RS Components France
  (Code: `285-076`, ~€14.50 HT), but consists of a full USB development kit
  rather than a clean plug-and-play Qwiic sensor breakout.

---

## 4. Summary & Recommendation for Seagram Gateway

```
+--------------------------------------------------------------------------+
|                    Recommended Marine Barometer Matrix                  |
|                                                                          |
|  [ First Choice: Plug-and-Play Qwiic ]                                   |
|    SparkFun BMP384 (SEN-19662)                                           |
|    - Gel-filled moisture protection                                      |
|    - Dual Qwiic ports for direct daisy-chaining with HALMET              |
|    - Stocked at Mouser France and DigiKey Europe                         |
|                                                                          |
|  [ Second Choice: French Local Stock + Solderless STEMMA QT ]             |
|    Adafruit LPS35HW (PID 4258 / GoTronic 36398)                          |
|    - Gel-filled ceramic body                                             |
|    - Dual STEMMA QT ports (100% Qwiic cable compatible)                  |
|    - In stock locally in France at GoTronic (€19.80 TTC)                 |
|                                                                          |
|  [ Third Choice: Maximum Precision & Chemical Robustness ]               |
|    DFRobot BMP585 (SEN0666 / GoTronic 39529)                            |
|    - IPX8 gel protection, 0.08 Pa RMS noise                             |
|    - Requires basic pin header soldering (no native Qwiic port)          |
|    - In stock locally in France at GoTronic (€12.30 TTC)                 |
+--------------------------------------------------------------------------+
```

### 4.1 Implementation with HALMET
* **Electrical Link:** Connect via standard 4-pin Qwiic cable from HALMET's
  Qwiic port to the sensor board.
* **Bus Arbitration:**
  * SparkFun BMP384 (`0x77`) or Adafruit LPS35HW (`0x5D`) coexists seamlessly
    with HALMET's internal ADS1115 ADC (`0x48`) on the same I2C bus lines (GPIO
    21 SDA / GPIO 22 SCL).
  * No I2C multiplexer is needed.
* **Software Telemetry:**
  * Sample pressure in Pascals and broadcast onto the NMEA 2000 backbone via
    **PGN 130310** (Environmental Parameters) and **PGN 130314** (Actual
    Pressure).
  * Stream to Signal K on key `environment.outside.pressure`.
