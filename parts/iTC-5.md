# Device Identifier
* **manufacturer:** Raymarine
* **part number:** iTC-5
* **price (date in dd-mm-yyyy format):** $369.99 USD / €329.95 (Current as of
  17-10-2026)
* **manufacturer link:** [Raymarine Official iTC-5 Product Page](
  https://www.raymarine.com/en-us/our-products/marine-instruments/instrument-accessories/itc-5-transducer-converter)
* **manual download link:** [Raymarine Manuals & Documentation Download Port](
  https://www.raymarine.com/en-gb/download/itc-5-manuals)
* **description (50 words max):** The Raymarine iTC-5 is a compact
  analog-to-digital converter hub. It converts legacy analog signals from wind,
  speed, depth, temperature, and rudder transducers into digital NMEA 2000
  (SeaTalkng) data, allowing old sensors to stream seamlessly to modern
  chartplotters, instrument displays, and network viewer apps.

# Integration with input sensors

The iTC-5 is designed to act as a bridge for legacy 5-wire or 3-wire analog
sensors. Under its protective clip-on cover, the unit features dedicated,
color-coded spade-connector termination strips for five distinct analog marine
sensors:

1. **Wind Transducer:** Accepts standard 5-wire mechanical masthead wands
   (measuring apparent wind speed and angle via raw voltage pulses).
2. **Speed (Paddlewheel):** Connects the standard 4-wire paddlewheel lines used
   to track Speed-Through-Water (STW).
3. **Depth Transducer:** Supports acoustic depth pings (150kHz or 200kHz
   traditional depth transducers).
4. **Sea Temperature:** Thermistor lines integrated within the speed or depth
   hull fittings.
5. **Rudder Angle & Compass Reference:** Terminal connections to ingest analog
   resistive rudder reference units and legacy fluxgate compass data.

**How to connect:** Transducer cables are routed through the internal rubber
cable gland at the base of the iTC-5. Strip the raw wire ends, crimp 1/8” spade
terminals onto each core, and slide them onto the corresponding color-coded
physical pins on the main circuit board. The iTC-5 then hooks directly into
your powered NMEA 2000 / SeaTalkng backbone network using a single spur cable
drop.

# Calibration of instrument

## Intro
Historically, legacy Raymarine systems operated under a distributed
intelligence system: raw, analog sensor data went straight to the cockpit, and
the calibration profile (offsets, multi-point curves) was calculated and stored
locally inside the physical memory of individual **ST60 cockpit displays**.

With the **iTC-5**, this paradigm shifts. The ST60 displays are eliminated, and
the iTC-5 itself becomes the centralized digitization hub. The *calibration
profile is saved directly into the internal non-volatile memory of the iTC-5
device*. However, because the iTC-5 has zero buttons, dials, or screen
interfaces, it cannot generate these profiles on its own, nor can third-party
N2K viewing apps trigger calibration routines. You must temporarily or
permanently utilize a compatible Raymarine device to program the unit.

## I70s option
The **Raymarine i70s Instrument Display** is the native tool for calibrating
the iTC-5. Because it shares the software ecosystem of the converter, a single
i70s screen can configure every sensor wired to the iTC-5.

To execute calibration, connect the i70s to the same SeaTalkng network.
Navigate to `Menu` > `Set-up` > `Transducers Set-up` > `Continue`. Select the
**iTC-5** from the discovered network device menu. From here, you can step
through each transducer:
* **Wind:** Spin the boat in a slow circle to let the software automatically
  calculate wind speed linearization, and manual alignment adjustments to match
  the vane to the bow line.
* **Speed:** Perform a single or multi-point calibration curve or click to
  automatically calculate speed adjustments relative to your network's SOG
  (Speed Over Ground).
* **Depth:** Key in a positive or negative structural depth offset to dictate
  if your readings start from the waterline or the keel tip.

Once completed, the calculations are automatically written back down the
backbone cable to the iTC-5's onboard memory chip, allowing you to disconnect
the i70s display afterward if desired.

## eS97 chartplotter option
Because the **eS97** belongs to an older hardware lineage running legacy
architecture, it cannot calibrate an iTC-5 on its factory operating software
(LightHouse II). It must first undergo a software system transition to act as
your calibration tool.

1. **Software Update:** Format a 1GB–32GB MicroSD card to FAT32. Visit the
   Raymarine Download Portal, navigate to the retired MFD section, and download
   the specialized legacy variant of **LightHouse 3 (v3.11.42 "Cannes")**
   compiled for eS-Series units. Place the extracted file onto the root folder
   of the card.
2. **Flashing the Unit:** Turn the eS97 off, insert the card, boot the system,
   and confirm the firmware overwrite via `Set-up` > `Maintenance` > `Check
   Card for updates`. Once finished, complete a comprehensive Factory Reset via
   settings to scrub configuration remnants.
3. **Executing Calibration:** Once your eS97 is running LightHouse 3, go to the
   homescreen and navigate to `Settings` > `Network`. Discovered hardware will
   map out on screen. Select your **iTC-5 Converter** from the hardware array,
   tap `Calibrate`, and select the individual transducer type you wish to
   adjust. The eS97 will then use the same network logic as an Axiom plotter,
   pushing depth offsets, wind alignment, and paddlewheel correction tables
   down to save permanently inside the iTC-5.
