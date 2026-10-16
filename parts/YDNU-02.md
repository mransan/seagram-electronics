# Device Identifier
* manufacturer: Yacht Devices
* part number: YDNU-02
* price (date in 16-10-2026 format): \$249.00 USD (As of 16-10-2026)
* manufacturer link: [Yacht Devices Official Site](
  https://www.yachtd.com/products/usb_gateway.html
  "NMEA to usb: NMEA 2000 USB Gateway")
* manual download link: [YDNU-02 User Manual PDF](
  https://www.yachtd.com/downloads/ydnu02.pdf
  "ydnu02.pdf")
* description: A bi-directional hardware gateway connecting NMEA 2000 networks
  to computers via USB. It offers galvanic isolation and supports binary
  pass-through, text conversion, and diagnostics logging without requiring
  special drivers on modern operational systems.

# Integration with other devices
This section details how the YDNU-02 links with external platforms. It
operates as a local serial device using a physical connection. It has a
structural dependency on the master host system for power and driver
communication.

## Tablet / Phones
* **Connectivity:** Physical USB link. Requires a USB OTG (On-The-Go) adapter
  or a direct USB-C to USB-A data cable.
* **Configuration Steps:** Plug the adapter into the tablet/phone. Set the
  mobile app connection input type to "Serial" or "USB Data Connection".
* **Dependency:** The mobile app must explicitly support direct serial COM
  connections and feature an internal NMEA parsing engine. Most iOS devices do
  not natively support this serial workflow without special hardware.

## OpenPlotter (Raspberry PI)
* **Connectivity:** Standard physical connection using any free USB Type-A
  port on the Raspberry Pi.
* **Configuration Steps:** Connect the cable. Open the OpenPlotter Serial app,
  select the detected `/dev/ttyACM*` interface, name it, and label its device
  type as "CAN Bus" to map it cleanly.
* **Dependency:** Requires OpenPlotter's built-in Linux kernel serial stack
  (`slcand`) to bridge the physical USB serial port into a virtual native
  network interface.

## PC with OpenCPN
* **Connectivity:** Direct physical link to a laptop or desktop motherboard
  port.
* **Configuration Steps:** Open OpenCPN settings, navigate to Connections,
  select "Serial", choose the correct COM port (Windows) or `/dev/ttyUSB*` /
  `/dev/ttyACM*` path (Mac/Linux), and set the matching baud rate.
* **Dependency:** Depends on standard hardware manufacturer virtual COM port
  mapping (CDC ACM system drivers).

## Integration with OpenPlotter
The YDNU-02 functions as a local system asset. Run the **OpenPlotter CAN Bus
app**, select the mapped device interface name, input your operational baud
rate (typically 115200 or 230400), and hit "Add to CAN Bus". This maps raw
frames directly to the local kernel socket interface (`can0`), allowing Signal
K's data server engine to consume all network traffic instantly.
