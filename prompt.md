# Goal 

The goal is to create a new directory called @parts and add 2 mardown files for the following 2 devices
* YDNU-02
* YDWG-02

The content for YDNU-02 is
```
# Device Identifier
* manufacturer: Yacht Devices
* part number: YDNU-02
* price (date in 16-10-2026 format): \$249.00 USD (As of 16-10-2026)
* manufacturer link: [Yacht Devices Official Site](https://www.yachtd.com/products/usb_gateway.html "NMEA to usb: NMEA 2000 USB Gateway")
* manual download link: [YDNU-02 User Manual PDF](https://www.yachtd.com/downloads/ydnu02.pdf "ydnu02.pdf")
* description: A bi-directional hardware gateway connecting NMEA 2000 networks to computers via USB. It offers galvanic isolation and supports binary pass-through, text conversion, and diagnostics logging without requiring special drivers on modern operational systems.

# Integration with other devices
This section details how the YDNU-02 links with external platforms. It operates as a local serial device using a physical connection. It has a structural dependency on the master host system for power and driver communication.

## Tablet / Phones
* **Connectivity:** Physical USB link. Requires a USB OTG (On-The-Go) adapter or a direct USB-C to USB-A data cable.
* **Configuration Steps:** Plug the adapter into the tablet/phone. Set the mobile app connection input type to "Serial" or "USB Data Connection".
* **Dependency:** The mobile app must explicitly support direct serial COM connections and feature an internal NMEA parsing engine. Most iOS devices do not natively support this serial workflow without special hardware.

## OpenPlotter (Raspberry PI)
* **Connectivity:** Standard physical connection using any free USB Type-A port on the Raspberry Pi.
* **Configuration Steps:** Connect the cable. Open the OpenPlotter Serial app, select the detected `/dev/ttyACM*` interface, name it, and label its device type as "CAN Bus" to map it cleanly.
* **Dependency:** Requires OpenPlotter's built-in Linux kernel serial stack (`slcand`) to bridge the physical USB serial port into a virtual native network interface.

## PC with OpenCPN
* **Connectivity:** Direct physical link to a laptop or desktop motherboard port.
* **Configuration Steps:** Open OpenCPN settings, navigate to Connections, select "Serial", choose the correct COM port (Windows) or `/dev/ttyUSB*` / `/dev/ttyACM*` path (Mac/Linux), and set the matching baud rate.
* **Dependency:** Depends on standard hardware manufacturer virtual COM port mapping (CDC ACM system drivers).

## Integration with OpenPlotter
The YDNU-02 functions as a local system asset. Run the **OpenPlotter CAN Bus app**, select the mapped device interface name, input your operational baud rate (typically 115200 or 230400), and hit "Add to CAN Bus". This maps raw frames directly to the local kernel socket interface (`can0`), allowing Signal K's data server engine to consume all network traffic instantly.
```

The content for YDWG-02 is
```
# Device Identifier
* manufacturer: Yacht Devices
* part number: YDWG-02
* price (date in 16-10-2026 format): \$249.00 USD (As of 16-10-2026)
* manufacturer link: [Yacht Devices Official Site](https://www.yachtd.com/products/wifi_gateway.html "Wi-Fi Gateway YDWG-02")
* manual download link: [YDWG-02 User Manual PDF](https://www.yachtd.com/downloads/ydwg02.pdf "Yacht Devices Wi-Fi Gateway manual")
* description: A bi-directional wireless gateway that transmits marine data from an NMEA 2000 backbone onto a local Wi-Fi link. It supports RAW, NMEA 0183, and TCP/UDP client streams, featuring built-in web gauge graphics accessible inside a standard mobile browser.

# Integration with other devices
This section details how the YDWG-02 links with external platforms. It operates purely as a network-based resource. It has a structural dependency on stable 2.4 GHz radio-frequency clear air paths and correct TCP/IP configuration parameters.

## Tablet / Phones
* **Connectivity:** 2.4 GHz Wi-Fi link. Devices connect wirelessly to the YDWG-02 internal hotspot or a shared boat network router.
* **Configuration Steps:** Connect to the Wi-Fi network. Open any marine app (e.g., Navionics), select a network input stream, set the connection type to TCP Client, enter the gateway IP address, and specify the port number.
* **Dependency:** Relies entirely on the app's capability to read incoming raw data frames or translated text strings via network sockets.

## OpenPlotter (Raspberry PI)
* **Connectivity:** Network connection over standard Wi-Fi. Bypasses all physical USB cabling.
* **Configuration Steps:** Connect the Raspberry Pi Wi-Fi card to the gateway access point, or join both units onto a unified boat router system. 
* **Dependency:** Requires an operational wireless network infrastructure and a persistent, unblocked network path on port 1456 or 2304.

## PC with OpenCPN
* **Connectivity:** Wi-Fi connection from the computer's built-in wireless adapter card.
* **Configuration Steps:** Open OpenCPN, navigate to Options -> Connections, click "Add Connection", change the type to "Network", choose "TCP", enter the gateway's IP address, and input the designated port.
* **Dependency:** Relies on structural stability in the operating system's wireless network manager to avoid dropping data packets under high electromagnetic interference.

## Integration with OpenPlotter
The YDWG-02 functions as a remote network stream. Do not use the OpenPlotter Serial or CAN Bus apps. Open the **Signal K Console** directly at `http://localhost:3000`, navigate to Data Connections, and create a new connection. Set the type to **TCP Client**, enter the gateway's static network IP address, type the raw stream port number, and specify **Yacht Devices RAW format** as the network parser.
```

# Contribution guideline

- create a dedicated branch in git to perform the task
- once the task initial implementation is complete, push to origin and create a pull request 
- keep lines under 80 characters 
- update the README.md file concisely after completing the task to help a coding agent understand what has been done and build on top.
