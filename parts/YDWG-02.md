# Device Identifier
* manufacturer: Yacht Devices
* part number: YDWG-02
* price (date in 16-10-2026 format): \$249.00 USD (As of 16-10-2026)
* manufacturer link: [Yacht Devices Official Site](
  https://www.yachtd.com/products/wifi_gateway.html
  "Wi-Fi Gateway YDWG-02")
* manual download link: [YDWG-02 User Manual PDF](
  https://www.yachtd.com/downloads/ydwg02.pdf
  "Yacht Devices Wi-Fi Gateway manual")
* description: A bi-directional wireless gateway that transmits marine data
  from an NMEA 2000 backbone onto a local Wi-Fi link. It supports RAW, NMEA
  0183, and TCP/UDP client streams, featuring built-in web gauge graphics
  accessible inside a standard mobile browser.

# Integration with other devices
This section details how the YDWG-02 links with external platforms. It operates
purely as a network-based resource. It has a structural dependency on stable
2.4 GHz radio-frequency clear air paths and correct TCP/IP configuration
parameters.

## Tablet / Phones
* **Connectivity:** 2.4 GHz Wi-Fi link. Devices connect wirelessly to the
  YDWG-02 internal hotspot or a shared boat network router.
* **Configuration Steps:** Connect to the Wi-Fi network. Open any marine app
  (e.g., Navionics), select a network input stream, set the connection type to
  TCP Client, enter the gateway IP address, and specify the port number.
* **Dependency:** Relies entirely on the app's capability to read incoming raw
  data frames or translated text strings via network sockets.

## OpenPlotter (Raspberry PI)
* **Connectivity:** Network connection over standard Wi-Fi. Bypasses all
  physical USB cabling.
* **Configuration Steps:** Connect the Raspberry Pi Wi-Fi card to the gateway
  access point, or join both units onto a unified boat router system.
* **Dependency:** Requires an operational wireless network infrastructure and a
  persistent, unblocked network path on port 1456 or 2304.

## PC with OpenCPN
* **Connectivity:** Wi-Fi connection from the computer's built-in wireless
  adapter card.
* **Configuration Steps:** Open OpenCPN, navigate to Options -> Connections,
  click "Add Connection", change the type to "Network", choose "TCP", enter the
  gateway's IP address, and input the designated port.
* **Dependency:** Relies on structural stability in the operating system's
  wireless network manager to avoid dropping data packets under high
  electromagnetic interference.

## Integration with OpenPlotter
The YDWG-02 functions as a remote network stream. Do not use the OpenPlotter
Serial or CAN Bus apps. Open the **Signal K Console** directly at
`http://localhost:3000`, navigate to Data Connections, and create a new
connection. Set the type to **TCP Client**, enter the gateway's static network
IP address, type the raw stream port number, and specify **Yacht Devices RAW
format** as the network parser.
