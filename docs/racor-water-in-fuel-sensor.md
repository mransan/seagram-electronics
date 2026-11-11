# Racor 230R Water-in-Fuel (WIF) Sensor Integration with HALMET

This document details how to interface the Water-in-Fuel (WIF) detection probe
for the **Parker Racor 230R** spin-on fuel filter / water separator with the
**HALMET** board, and broadcast real-time alarms via **NMEA 2000** (preferred)
and **Signal K**.

---

## 1. System Overview & Sensor Architecture

The Parker Racor 200 Series (specifically the 230R spin-on filter) separates
emulsified and free water from diesel fuel. As water is denser than diesel, it
settles at the base of the transparent or metal bowl.

```
       +---------------------------------------------+
       |           Racor 230R Filter Bowl            |
       |                                             |
       |  [ Diesel Fuel Layer ] (Non-conductive)     |
       |                                             |
       | - - - - - - - - - - - - - - - - - - - - - - |
       |  [ Water Accumulation ] (Conductive)        |
       |                                             |
       |         [+] Tip           [-] Tip           |
       +----------|-------------------|--------------+
                  |   Racor RK21069   |
                  | 1/2"-20 UNF Probe |
                  +---------+---------+
                            |
                     (2-Wire Pigtail)
                            |
           [ Passive Resistive Water Bridge ]
                            |
                            v
       +---------------------------------------------+
       |         HALMET Marine Interface Board       |
       |                                             |
       |  Option A: Digital Input (D1–D4 w/ Pull-up) |
       |  Option B: Analog Input  (A1–A4 w/ Divider) |
       |                                             |
       |  - Galvanically Isolated Input Domain       |
       |  - ESP32 Firmware (SensESP / NMEA2000)      |
       +--------------------+------------------------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
     [ NMEA 2000 Bus ]              [ Signal K ]
      PGN 127489 (Engine)         propulsion.main.
      Bit 8: Water In Fuel        waterInFuel: true
```

### 1.1 The Racor RK 21069 Water Probe
* **Part Number:** **Racor RK 21069** (or RK 21069-01 / RK 21069-02).
* **Thread Fitting:** **1/2"-20 UNF** with an integrated Buna-N O-ring that
  threads into the bottom port of the Racor 230R bowl.
* **Electrical Working Principle:**
  - The probe consists of **two exposed stainless-steel electrode tips**
    separated by a fixed gap inside the bowl cavity.
  - **In Clean Diesel Fuel:** Hydrocarbons are non-polar dielectric fluids.
    Electrical resistance across the tips is virtually infinite ($R >
    10\,\text{M}\Omega$).
  - **In Water:** Water (especially marine condensation or brackish wash) is
    conductive. When water rises to bridge both electrodes, electrical
    resistance drops drastically to **$< 47\,\text{k}\Omega \text{ -- }
    100\,\text{k}\Omega$**.
* **Crucial Electrical Rule:** The RK 21069 is a **purely passive continuity
  probe with NO internal series resistor**. It must **NEVER** be connected
  directly across 12 V / 24 V battery power and ground, as that would pass
  uncontrolled current through the fuel, cause electrolytic degradation of the
  pins, and create a short-circuit hazard.

---

## 2. HALMET Hardware Interfacing Options

HALMET provides four **galvanically isolated digital inputs (D1–D4)** and four
**galvanically isolated analog inputs (A1–A4)**. The field wiring side operates
in its own isolated domain, completely protecting the ESP32 and NMEA 2000 CAN
bus from ground loops or high-voltage transients.

Two wiring configurations can be used:

### 2.1 Option 1: Digital Input (D1–D4) with Internal Pull-Up (Simplest)

HALMET's digital inputs feature Schmitt trigger buffers with a nominal
switching threshold of $\sim 1.55\,\text{V}$ and configurable solder jumpers on
the bottom side for an internal **$100\,\text{k}\Omega$ pull-up or pull-down
resistor**.

* **Wiring:**
  - Connect **Probe Lead 1** to **HALMET D1 (+)**.
  - Connect **Probe Lead 2** to **HALMET Isolated GND (-)**.
  - Enable the **$100\,\text{k}\Omega$ pull-up solder jumper** on the underside
    of HALMET for channel D1 (pulling D1 up to the isolated 3.3 V rail).

```
   Isolated 3.3V Rail
           |
          [ ] Internal 100k Pull-up (Solder Jumper enabled)
           |
           +---------------------> Schmitt Trigger (D1 Input)
           |
      (Lead 1)
     [ Racor RK21069 ]
     [  Probe Tips   ]
      (Lead 2)
           |
   Isolated Ground (GND)
```

* **Operating Behavior:**
  - **Dry / Pure Fuel ($R_{\text{probe}} = \infty$):** D1 is pulled to 3.3 V
    (Logic HIGH = Normal).
  - **Water Detected ($R_{\text{probe}} \le 47\,\text{k}\Omega$):** The voltage
    divider between the $100\,\text{k}\Omega$ pull-up and the probe resistance
    drops the input voltage below $1.05\,\text{V}$: $$V_{\text{in}} =
    3.3\,\text{V} \times \frac{47\,\text{k}\Omega}{100\,\text{k}\Omega +
    47\,\text{k}\Omega} \approx 1.05\,\text{V}$$ Because $1.05\,\text{V}$ is
    well below the Schmitt trigger input low threshold ($\sim 1.2\,\text{V}$),
    D1 flips to **Logic LOW** (Water Alarm).
* **Advantage:** Requires zero external resistors or components. Only the probe
  and two wires directly to the D1 terminal block.

### 2.2 Option 2: Analog Input (A1–A4) via Isolated 3.3 V Bias (Most Tunable)

If your boat operates with pure fresh-water condensation where water
conductivity may be slightly lower ($50\,\text{k}\Omega \text{ to }
150\,\text{k}\Omega$), an analog channel provides calibrated voltage/resistance
measurement and adjustable software thresholds.

* **Wiring:**
  - Connect **Probe Lead 1** to **HALMET A1 (+)**.
  - Connect **Probe Lead 2** to **HALMET Isolated GND (-)**.
  - HALMET's A1 input feeds a 16-bit Texas Instruments **ADS1115 ADC** on the
    isolated bus.
  - Connect a pull-up resistor ($47\,\text{k}\Omega$ to $100\,\text{k}\Omega$)
    between the **Isolated 3V3 terminal** on HALMET's power breakout and
    **HALMET A1 (+)**.
* **Firmware Calibration:**
  - Read voltage continuously via ADS1115 ($0 \text{ to } 3.3\,\text{V}$).
  - Clean fuel: reads $\sim 3.3\,\text{V}$.
  - Sludge / initial trace moisture: voltage begins to dip.
  - Threshold trigger: flag alarm when $V_{\text{in}} < 2.0\,\text{V}$ for more
    than 3 consecutive seconds (debouncing slosh).

> [!IMPORTANT] **Do NOT use the 10 mA Constant Current Source (CCS) jumpers on
> HALMET for the Racor WIF probe!** The CCS is calibrated for low-resistance
> senders ($0 \text{ to } 300\,\Omega$). Forcing 10 mA into a high-resistance
> fluid probe will saturate the input and may cause excessive current density
> on the stainless probe tips.

---

## 3. Physical Installation & Wiring Best Practice

### 3.1 Mechanical Installation on the 230R Bowl
1. Place a clean drain catch pan underneath the Racor 230R filter.
2. Unscrew the bottom drain plug or drain valve from the bottom of the bowl.
3. Inspect the Buna-N O-ring on the **Racor RK 21069** probe. Lightly coat it
   with clean engine oil or diesel fuel.
4. Hand-thread the RK 21069 into the 1/2"-20 UNF port until snug, then tighten
   an additional $1/4$ to $1/2$ turn with a wrench. **Do not over-tighten**, as
   over-torquing will strip the plastic threads of the bowl.
5. Prime the fuel filter using the primer pump on top of the 230R housing and
   check for fuel leaks before running the engine.

### 3.2 Cable Selection & Routing
* **Environment:** The engine room is a hot, oily, high-vibration environment.
* **Recommended Cable:** A marine-grade 2-conductor shielded cable:
  - Wire Gauge: **20 AWG** ($0.5\,\text{mm}^2$) or **22 AWG**
    ($0.34\,\text{mm}^2$).
  - Shielding: Tinned copper braid or foil shield to reject alternator and
    starter motor electrical noise.
  - [GoTronic Shielded 2-Conductor Cable (Ref CBR222)](
    https://www.gotronic.fr/art-cable-blinde-cbr222-15142.htm).
* **Connection at Probe:**
  - The Racor probe comes with an 8-inch 2-wire pigtail.
  - Splice using **marine adhesive heat-shrink butt connectors** (such as
    heat-shrink solder sleeves or crimp splices) to ensure a gas-tight,
    fuel-proof seal in the bilge.
  - Ground the cable drain wire **at the HALMET enclosure only** (isolated
    GND); leave the shield floating at the fuel filter to prevent ground loop
    currents.

---

## 4. Software Implementation: NMEA 2000 & Signal K

### 4.1 NMEA 2000 PGN 127489 (Engine Parameters, Dynamic)
The official NMEA 2000 standard provides a dedicated alarm bit for **Water in
Fuel** inside **PGN 127489 (Engine Parameters, Dynamic)** under **Engine
Discrete Status 1** (`tN2kEngineDiscreteStatus1`):
* **Field:** `Status1.Bits.WaterInFuel`
* **Bit Assignment:** Bit 8 of the 16-bit status word.
* **Compatibility:** Setting this bit triggers the native "Water in Fuel" alarm
  banner and audible buzzer on Raymarine Axiom, Garmin GPSMAP, B&G Zeus, and
  Furuno MFDs.

#### C++ / SensESP Implementation Snippet:
```cpp
#include <Arduino.h>
#include <NMEA2000.h>
#include <N2kMessages.h>

const int PIN_WIF_DIGITAL = 23; // HALMET D1 (GPIO 23)
bool waterInFuelAlarm = false;
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY_MS = 2500; // Filter out fuel sloshing

void setup() {
  pinMode(PIN_WIF_DIGITAL, INPUT); // Bottom jumper configured for 100k pull-up
}

void loop() {
  // Reading LOW means resistance dropped due to water bridging the probe
  bool reading = (digitalRead(PIN_WIF_DIGITAL) == LOW);

  if (reading != waterInFuelAlarm) {
    if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY_MS) {
      waterInFuelAlarm = reading;
    }
  } else {
    lastDebounceTime = millis();
  }

  // Send N2K PGN 127489 at regular 1 Hz interval
  static unsigned long lastSend = 0;
  if (millis() - lastSend >= 1000) {
    lastSend = millis();

    tN2kMsg N2kMsg;
    tN2kEngineDiscreteStatus1 status1;
    tN2kEngineDiscreteStatus2 status2;

    status1.Status = 0;
    status2.Status = 0;
    status1.Bits.WaterInFuel = waterInFuelAlarm ? 1 : 0;

    SetN2kEngineDynamicParam(
      N2kMsg,
      0,               // Engine Instance (0 = Single / Port)
      N2kDoubleNA,     // Oil pressure
      N2kDoubleNA,     // Oil temp
      N2kDoubleNA,     // Coolant temp
      N2kDoubleNA,     // Alternator voltage
      N2kDoubleNA,     // Fuel rate
      N2kDoubleNA,     // Engine hours
      N2kDoubleNA,     // Coolant pressure
      N2kDoubleNA,     // Fuel pressure
      N2kInt8NA,       // Engine load
      N2kInt8NA,       // Engine torque
      status1,         // Engine Discrete Status 1 (Water In Fuel at Bit 8)
      status2          // Engine Discrete Status 2
    );

    NMEA2000.SendMsg(N2kMsg);
  }
}
```

### 4.2 Signal K Delta Mapping
Over Wi-Fi, HALMET's SensESP firmware can output standard Signal K deltas:
* **Path:** `propulsion.main.waterInFuel` (or `propulsion.port.waterInFuel`)
* **Type:** Boolean (`false` = normal, `true` = water detected)
* **Alert Path:** `notifications.propulsion.main.waterInFuel`
  - Normal: `{"state": "normal", "method": []}`
  - Alarm: `{"state": "alarm", "method": ["visual", "sound"], "message": "Water
    detected in Racor 230R primary fuel filter!"}`

---

## 5. Bill of Materials & French Sourcing

| Item | Manufacturer & Part Number | Key Specifications | Sourcing in France |
| :--- | :--- | :--- | :--- |
| **Racor Water Probe** | Parker Racor **RK 21069** | 1/2"-20 UNF threads, 2-wire pigtail, passive stainless tips | • [Tyboat (Ref RK21069)](https://www.tyboat.com/achat/P-3620-racor-detecteur-de-presence-d-eau-1-2-20-unf-rk21069.html)<br>• [H2R Equipements (Ref 3052)](https://www.h2r-equipements.com/filtre-a-carburant-bateau/3052-parker-racor-sonde-eau-rk21069.html) |
| **Monitoring Board** | Hat Labs **HALMET** | ESP32, N2K CAN, isolated digital/analog inputs | [Hat Labs Store](https://shop.hatlabs.fi/products/halmet) |
| **2-Wire Shielded Cable** | CBR222 | 2x 0.22 mm² (or 0.34 mm²), shielded, PVC marine jacket | [GoTronic Ref 15142](https://www.gotronic.fr/art-cable-blinde-cbr222-15142.htm) |
| **Waterproof Splices** | Adhesive Heat-shrink Butt Splices | 22–18 AWG adhesive-lined waterproof crimp sleeves | Local marine chandlers or hardware stores |
