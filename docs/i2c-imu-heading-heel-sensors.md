# Marine I2C 9-Axis IMU Sensors: Heading & Heel Angle Evaluation

This document evaluates 9-axis Inertial Measurement Units (IMUs) and
magnetometer/gyroscope sensor breakouts for marine sailing yacht applications.
The primary objectives are providing accurate **magnetic heading** (referenced
to Magnetic North) and dynamic **angle of heel** (roll) and **pitch** (trim)
via the I2C bus to an ESP32 gateway (such as HALMET or a discrete gateway),
OpenPlotter, and Signal K / NMEA 2000 networks.

---

## 1. Marine Operating Requirements for Attitude & Heading

Sailing yachts present unique operational challenges for MEMS motion sensors
compared to land-based robotics or quadcopters:

1. **Continuous Heeling Dynamics:** Sailboats operate continuously heeled at
   angles between $10^\circ$ and $35^\circ$ for hours. An uncompensated 2D
   electronic compass suffers massive projection errors when tilted (often
   deviating by $20^\circ\text{ to }50^\circ$). The sensor must execute 3D tilt
   compensation using gravity vectors from the accelerometer to project Earth's
   magnetic flux vector into the horizontal navigational plane.
2. **Dynamic Roll & Wave Pumping:** In rolling seas, linear accelerations from
   wave action distort the apparent gravity vector. A 9-axis sensor fusion
   algorithm (Extended Kalman Filter or Madgwick/Mahony filter) is necessary to
   fuse high-rate gyroscope integration (which tracks immediate wave motion
   without accelerometer distortion) with long-term gravity settling and
   magnetic orientation.
3. **Hard & Soft Iron Magnetic Interference:** Engine blocks, keel bolts, DC
   cables carrying 30–100 A, battery banks, and winches distort the local
   magnetic field. The IMU must support robust 3D hard-iron (bias offset) and
   soft-iron (ellipsoid distortion) calibration routines that can be stored
   persistently across reboots.
4. **On-Chip AHRS Fusion vs Host Fusion:**
   - *Hardware Fusion (AHRS):* Chips like the **BNO085** run an onboard ARM
     Cortex-M0 executing proprietary Hillcrest Labs SH-2 / MotionEngine™
     firmware. They offload all complex quaternion and Euler math from the host
     microcontroller and directly output tilt-compensated quaternions.
   - *Raw IMU + Software Fusion:* Chips like the **ICM-20948** or **ISM330DHCX
     + LIS3MDL** stream raw 9-axis readings ($\omega, a, m$). The host ESP32 or
       Raspberry Pi (e.g. OpenPlotter Pypilot or SensESP) runs an open
       Madgwick/Mahony filter, giving the developer full transparent control
       over magnetic calibration matrices and filter gains.

---

## 2. Sensor Comparative Technical Specifications

| Sensor Solution | Manufacturer | Architecture & Fusion | Dynamic Heading Accuracy | Static Heel/Roll Accuracy | I2C Addresses (7-bit) | Current Draw | Marine / Sailboat Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BNO085** | CEVA / Hillcrest (Bosch MEMS) | 9-DoF with on-chip ARM Cortex-M0 (SH-2 MotionEngine) | $\pm 2.0^\circ\text{ to }3.0^\circ$ | $\pm 0.5^\circ\text{ to }1.0^\circ$ | `0x4A` (default) or `0x4B` | $\approx 15\,\text{mA}$ | **Top Pick (Plug & Play):** Autonomous AHRS, true tilt-compensated heading and heel out-of-the-box. |
| **ICM-20948** | TDK InvenSense | 9-DoF (Accel + Gyro + AK09916 Mag) + DMP | Software dependent ($\approx \pm 2^\circ$ with Madgwick) | $\pm 0.5^\circ$ | `0x69` (default) or `0x68` | $\approx 3.2\,\text{mA}$ | **Best for OpenPlotter / Pypilot:** Natively supported in Pypilot; ultra-low noise raw streams. |
| **BNO055** | Bosch Sensortec | 9-DoF with on-chip Cortex-M0 (Legacy BSX) | $\pm 3.0^\circ\text{ to }5.0^\circ$ | $\pm 1.0^\circ$ | `0x28` (default) or `0x29` | $\approx 12\,\text{mA}$ | **Not Recommended:** Unpredictable automatic recalibration jumps on moving boats; legacy chip. |
| **ISM330DHCX + LIS3MDL** | STMicroelectronics | 6-DoF Industrial IMU + 3-DoF Magnetometer | Software dependent ($\approx \pm 2^\circ$ with Madgwick) | $\pm 0.3^\circ$ (industrial stability) | `0x6B` (IMU) + `0x1E` (Mag) | $\approx 2.5\,\text{mA}$ | **Industrial Grade:** Extreme thermal and zero-rate stability; requires external software fusion. |
| **WT901 / JY901** | WitMotion | 9-DoF + onboard Kalman filter MCU | $\pm 1.5^\circ\text{ to }2.5^\circ$ | $\pm 0.2^\circ$ | `0x50` (I2C) or UART | $\approx 20\,\text{mA}$ | **Turnkey Module:** Integrated Kalman filter; pre-tuned for attitude/heel; mostly UART or Dupont I2C. |

---

## 3. European Sourcing & Stock Availability (Qwiic / STEMMA QT Breakouts)

For clean marine electrical installations (such as connecting to a HALMET or
ESP32 gateway), breakout boards featuring SparkFun Qwiic / Adafruit STEMMA QT
(JST-SH 1.0 mm) dual connectors are strongly preferred because they allow
daisy-chaining alongside barometric pressure sensors without breadboards or
soldering.

### 3.1 CEVA / Hillcrest BNO085 Breakouts
The BNO085 is the gold standard for microcontrollers needing direct heading and
heel angles without consuming host CPU cycles.
* **Adafruit 9-DOF Orientation IMU Fusion Breakout - BNO085** (Product ID:
  `4754`):
  * **Connectors:** Dual STEMMA QT / Qwiic (JST-SH 1.0 mm) + 0.1" header.
  * **EU Stock:**
    * **GoTronic (France):** Stock ref `37262` (€34.50 TTC), in stock.
    * **Mouser France (`mouser.fr`):** Part `485-4754`, in stock.
    * **DigiKey Europe (`digikey.fr`):** Part `1528-4754-ND`, in stock.
* **SparkFun VR IMU Breakout - BNO086** (Product ID: `SEN-17222`):
  * Newer revision of the BNO080/085 with updated crystal and SH-2 firmware.
  * Features dual Qwiic ports. In stock at Mouser France (`474-SEN-17222`).

### 3.2 TDK InvenSense ICM-20948 Breakouts
Preferred choice when streaming raw 9-axis data into an OpenPlotter / Pypilot
system running on a Raspberry Pi or an advanced SensESP Madgwick filter.
* **Adafruit TDK InvenSense ICM-20948 9-DoF IMU** (Product ID: `4554`):
  * **Connectors:** Dual STEMMA QT / Qwiic (JST-SH 1.0 mm) + 0.1" header.
  * **EU Stock:**
    * **GoTronic (France):** Stock ref `37238` (€24.90 TTC), in stock.
    * **Mouser France (`mouser.fr`):** Part `485-4554`, in stock.
    * **DigiKey Europe (`digikey.fr`):** Part `1528-4554-ND`, in stock.
* **SparkFun 9DoF IMU Breakout - ICM-20948 (Qwiic)** (Product ID: `SEN-15335`):
  * Dual Qwiic ports. In stock at Mouser and DigiKey.

### 3.3 STMicroelectronics ISM330DHCX + LIS3MDL (Industrial Alternative)
* **Adafruit ISM330DHCX + LIS3MDL FeatherWing or Breakout** (Product ID: `4485`
  / `4517`):
  * Combines high-accuracy 6-axis industrial accelerometer/gyro with LIS3MDL
    3-axis magnetometer.
  * In stock at Mouser and DigiKey.

---

## 4. Architectural Comparison: BNO085 vs ICM-20948 for a Sailboat

Choosing between the BNO085 and ICM-20948 depends on the system architecture:

```mermaid
flowchart TD
    subgraph Option A: Autonomous On-Chip AHRS (BNO085)
        BNO[BNO085 Breakout\nAdafruit 4754] -->|Qwiic I2C\nQuaternions / Euler| ESP[ESP32 / HALMET Gateway]
        ESP -->|SensESP / N2K| N2K_A[NMEA 2000 Bus\nPGN 127250 / 127257]
        ESP -->|Wi-Fi / Signal K| SK_A[Signal K Server\nAttitude & Heading]
    end

    subgraph Option B: Host-Based Software AHRS (ICM-20948 / Pypilot)
        ICM[ICM-20948 Breakout\nAdafruit 4554] -->|I2C Raw Accel/Gyro/Mag| PI[OpenPlotter / Raspberry Pi]
        PI -->|Pypilot Calibration &\nMadgwick Fusion| PY[Pypilot Service]
        PY -->|Signal K Native| SK_B[Signal K Server\nAttitude & Heading]
    end
```

### 4.1 When to Choose BNO085 (Autonomous On-Chip Fusion)
- **Direct ESP32 / HALMET integration:** If your ESP32 gateway connects
  directly to the NMEA 2000 backbone without requiring a Raspberry Pi running
  24/7.
- The onboard Cortex-M0 continuously computes:
  - **Angle of Heel (Roll):** Derived from gravity vector projection.
  - **Trim (Pitch):** Fore-and-aft pitch angle.
  - **Magnetic Heading (Yaw):** Fully tilt-compensated magnetic heading.
- Saves CPU cycles and RAM on the ESP32, avoiding real-time floating-point
  Kalman matrix operations.

### 4.2 When to Choose ICM-20948 (Host Fusion / Pypilot)
- **OpenPlotter & Autopilot integration:** If you are running OpenPlotter with
  the **Pypilot** autopilot package.
- Pypilot includes built-in interactive 3D visual calibration routines:
  - Steer the boat in two full circles to map hard/soft-iron distortions.
  - Calibrate accelerometer bias on 6 orthogonal faces.
- Transparent mathematical pipeline with zero black-box firmware lockups.

---

## 5. Integration with HALMET Gateway (Qwiic Bus)

Both the Adafruit BNO085 (`4754`) and Adafruit ICM-20948 (`4554`) can be
daisy-chained directly into HALMET's JST-SH Qwiic port alongside a barometric
pressure sensor (such as the LPS35HW or BMP384).

### 5.1 I2C Address Map & Bus Compatibility
HALMET's onboard peripheral and daisy-chained breakout addresses:

| Device | Default Address | Alternate Address | Conflict with HALMET ADS1115 (`0x48`)? |
| :--- | :--- | :--- | :--- |
| **HALMET Built-in ADC** | `0x48` | Fixed | None |
| **Adafruit LPS35HW Barometer** | `0x5D` | `0x5C` | None |
| **SparkFun BMP384 Barometer** | `0x77` | `0x76` | None |
| **Adafruit BNO085 IMU** | `0x4A` | `0x4B` | **None** (Fully compatible) |
| **Adafruit ICM-20948 IMU** | `0x69` | `0x68` | **None** (Fully compatible) |

All devices operate comfortably on the shared 3.3V I2C bus at 100 kHz or 400
kHz standard clock rates.

### 5.2 NMEA 2000 & Signal K Data Mapping

Once the ESP32 (running SensESP) reads the orientation data, it maps the values
to the standard N2K PGNs and Signal K paths:

1. **Magnetic Heading:**
   - **Signal K Path:** `navigation.headingMagnetic` (in radians).
   - **NMEA 2000 PGN:** **PGN 127250** (Vessel Heading)
     - `Heading Sensor Reading`: Magnetic heading in radians ($0\dots 2\pi$).
     - `Deviation`: Magnetic deviation based on boat calibration curve.
     - `Heading Reference`: Magnetic (`0x00`).
2. **Angle of Heel & Pitch (Attitude):**
   - **Signal K Path:** `navigation.attitude`
     - `roll`: Heel angle in radians (negative = port, positive = starboard).
     - `pitch`: Trim angle in radians (positive = bow up, negative = bow down).
     - `yaw`: Heading/yaw angle.
   - **NMEA 2000 PGN:** **PGN 127257** (Attitude)
     - `Roll`: Resolution $0.0001\,\text{rad}$ ($\approx 0.0057^\circ$).
     - `Pitch`: Resolution $0.0001\,\text{rad}$.
     - `Yaw`: Resolution $0.0001\,\text{rad}$.

---

## 6. Sourcing Recommendation

1. **For HALMET ESP32 Gateway (Standalone N2K & Wi-Fi Gateway):**
   - **Recommended:** **Adafruit BNO085** (Adafruit `4754` / GoTronic `37262`).
   - In stock at GoTronic France (€34.50 TTC) and Mouser France.
   - Dual STEMMA QT / Qwiic ports plug directly into the LPS35HW / BMP384
     barometer and HALMET with zero soldering.
   - Generates stabilized, tilt-compensated heading and heel out-of-the-box.
2. **For OpenPlotter / Raspberry Pi with Pypilot:**
   - **Recommended:** **Adafruit ICM-20948** (Adafruit `4554` / GoTronic
     `37238`).
   - In stock at GoTronic France (€24.90 TTC) and Mouser France.
   - Full native compatibility with Pypilot's calibration and filtering tools.
