# Goal 

The goal is to add a new folder @docs where we will collect knowledge about
seagram electronics such as protocol specification, etc. 

We will start by adding a file in the folder for explaining the SeaTalk1 protocol. 

I have already researched some information which I am summarizing below:
```

Comprehensive Technical Guide: SeaTalk1 Network Architecture, Electrical Specifications, and Modern Bridging

This comprehensive reference document covers the electrical architecture, physical signaling protocols, hardware constraints, and modern integration strategies for legacy Raymarine SeaTalk1 (ST1) marine networks.

1. Physical Architecture and Cable Infrastructure

The SeaTalk1 network utilizes a multi-master, daisy-chained bus architecture where both operational power and digital communication are bundled into a single, continuous, three-core cable.

Wire Color Mapping and Functional Allocation

Standard SeaTalk1 infrastructure relies on three distinct conductors running in parallel to every device across the network:
• Red Wire (+12V DC Power): Delivers primary DC operational current to energize instrument microprocessors, control heads, sensor pods, and display backlighting.
• Black or Uninsulated/Shield Wire (0V / Ground Reference): Serves the dual purpose of acting as the negative return path for the +12V power supply loop and providing the absolute zero-volt reference point for data pulses.
• Yellow Wire (Data Line): The dedicated single-conductor pathway carrying proprietary asynchronous serial communication packets between all connected network nodes.

Bus Design and Exceptions

• Shared Infrastructure: Unlike modern industrial protocols that separate backbone lines from drop lines, SeaTalk1 devices are hooked up sequentially in a daisy chain. The red, black, and yellow conductors remain unbroken and continuous as the cable jumps from one node to the next.
• Power-Only Topologies: In scenarios where a node requires power but does not exchange data (such as standalone display repeaters or legacy remote transducer pods operating locally), the red and black/ground wires are wired to the bus while the yellow data wire is left disconnected.

2. Voltage Protocols and Logic Specifications

The SeaTalk1 data wire implements a 12V asynchronous serial protocol built upon a hardware architecture known as a Wired-OR (pull-down) configuration. This design differs fundamentally from standard computer serial standards (like RS-232).

Electrical Signaling Levels

Rather than using positive logic, SeaTalk1 uses an inverted voltage scheme relative to ground:
• Idle / Mark / Logic 1 State: +12V DC
• Active / Space / Logic 0 State: 0V (Ground)
Diagnostic Note: Because the network sits at +12V when quiet, a standard digital multimeter measuring an actively communicating, healthy SeaTalk1 network (measuring from the yellow data wire to the black ground wire) will register a fluctuating average reading between 10V and 11V DC. This slight dip is caused by the high-speed data pulses pulling the voltage to zero.

Asynchronous Data Frame Specifications

The electrical pulses broadcast across the yellow data wire map to standard serial characters structured with the following framing parameters:

Parameter	Specification / Value
Baud Rate	4800 Baud
Bit Duration	208 Microseconds (μ s)
Total Bits per Character	11 Bits
Start Bit	1 Bit (Actively driven down to 0V)
Data Bits	8 Bits (Transmitted Least Significant Bit [LSB] first)
Command / Parity Bit	1 Bit (Driven high on the first character of a command packet to signal a new message header)
Stop Bit	1 Bit (Transmitter releases line, allowing it to return to +12V)


3. The Wired-OR Architecture and Internal Pull-Ups

To allow multiple devices to talk on a single wire without damaging each other, Raymarine bypassed active high/low output stages in favor of a passive-pull-up/active-pull-down topology.

The Internal Device Circuit

Every individual device connected to the SeaTalk1 bus features a mirrored hardware interface connected directly to the yellow data line:
text
       +12V Power Rail (Red Wire)
             │
           [ 10k Ω Pull-Up Resistor ]
             │
             ├─────────────── To Internal Microprocessor (Receiver Input)
             │
   Yellow Data Wire Bus Line
             │
        [ Transistor Switch ] (The Emitter Stage)
             │
       0V Ground Rail (Black / Shield Wire)
Use code with caution.
1. The Idle State (Logic 1): When no device on the vessel is transmitting, every internal transistor switch across all devices remains open (turned off). Current from the +12V Red wire passes through the internal 10kΩ pull-up resistors inside every instrument. Because the circuit has no path to ground, voltage fills the entire continuous length of the yellow wire. Receivers sense +12V and read it as an idle network or a binary 1.
2. The Active State (Logic 0): When an instrument needs to transmit a binary 0, it briefly closes its internal transistor switch. This creates a direct path from the yellow wire to the black ground wire inside that specific device. The voltage on the continuous yellow wire drops instantly to 0V along its entire length. Any listening device on the bus detects this voltage drop relative to ground and registers a binary 0.

System Sizing and Resistor Sizing Constraints

The selection of a 10kΩ (10,000 ohm) value for the internal pull-up resistors represents a deliberate engineering balance:
• The Power Dissipation Lower Bound: When a device clamps the data line to ground, current flows through the resistor. Using Ohm's Law (I = V/R), a single 10kΩ resistor at 12V draws just 1.2 mA of current (I = 12 / 10,000). Power dissipation (P = V²/R) is only 14.4 mW. This permits the use of cheap, compact, low-power 1/4-watt resistors that generate virtually zero thermal load.
• The RC Time Constant Upper Bound: If a much larger resistance value were used (e.g., 100kΩ) to save power, the line's inherent cable capacitance would cause the voltage to climb too slowly when a bit is released. At 4800 baud, a bit lasts only 208μ s. A slow voltage rise would round off the square waves and corrupt the data. The 10kΩ value ensures sharp, clean rising edges.
• Parallel Bus Accumulation Constraint: Because all devices are wired in parallel, adding devices drops the total equivalent bus resistance.
\(\frac{1}{R_{\text{total}}}=\frac{1}{R_{1}}+\frac{1}{R_{2}}+\dots +\frac{1}{R_{n}}\)

Number of Nodes	Combined Bus Resistance	Current Sunk by a Single Talker
1 Device	10,000 Ω	1.2 mA
5 Devices	2,000 Ω	6.0 mA
10 Devices	1,000 Ω	12.0 mA
20 Devices	500 Ω	24.0 mA

By dimensioning each resistor at 10kΩ, a large network of 20 devices still maintains a combined bus resistance of 500Ω. A single device's small internal switching transistor (like a standard 2N7000) can easily sink the resulting 24 mA to ground without overheating. If the resistors were sized too small (e.g., 1kΩ each), 20 devices would drop total resistance to 50Ω, demanding a massive 240 mA sink capacity that would require bulky power-transistors inside every display. Standard networks generally peak out at 20 to 30 devices before the combined parallel pull-ups make it difficult to pull the line cleanly down to absolute 0V.

Engineering Advantages of the Wired-OR Concept

• Short-Circuit Immunity: If multiple devices experience a collision and attempt to talk at the exact same millisecond, they are all simply closing their internal transistors to ground. No hardware shorts occur, preventing component burnouts.
• Bus Redundancy: Because pull-ups are decentralized across every device instead of sitting inside a single master unit, cutting the physical network cable in half creates two smaller, fully functional independent networks.
• Noise Immunity: The accumulation of multiple parallel pull-up resistors continuously stiffens the voltage on the long yellow wire. This protects the data line from electromagnetic interference (EMI) generated by marine alternators, starter motors, and VHF radios.

4. Power Source Rules and Voltage Tolerances

Legacy SeaTalk1 hardware features a broad operational power tolerance, successfully operating across a voltage range of 9V DC to 16V DC.
• Ratio-Metric Logic Following: Because the logic high state on the yellow wire is established by the pull-up resistors tied to the red wire, the data wire's idle voltage mirrors the network's supply line. If line drop lowers the power line to 11.5V, the logic high state drops to 11.5V. The receivers use wide enough threshold tolerances to process this seamlessly.
• Low Voltage Hazards: If cumulative line drop across long daisy chains causes the supply voltage to dip below 11.8V under load, microprocessors at the end of the run can crash, drop packets, or lock into reboot loops, throwing system errors like STLINK FAIL or NO DATA.
• The Single Source Rule: In a standard, standalone SeaTalk1 installation, multiple devices (like an autopilot course computer and an auxiliary fused line) can feed 12V onto the shared red rail in parallel. However, all power feeds must originate from the exact same breaker circuit and battery bank. If separate breakers are used, turning one breaker off will fail to de-energize the network; power will back-feed through the thin SeaTalk1 wires from the active circuit, risking melted insulation or component failure.

5. Bridging SeaTalk1 to SeaTalkng (NMEA 2000) and Ground Loop Mitigation

Integrating older SeaTalk1 equipment with modern SeaTalkng / NMEA 2000 (CAN bus) backbones requires the Raymarine E22158 Converter Block. This device serves as an active protocol translator, converting low-speed 4800-baud single-ended SeaTalk1 messages into high-speed 250,000-baud differential CAN bus packets.

The Mechanics of a Ground Loop

Inside the molded casing of the E22158 converter block, the Black/Shield Ground pin of the yellow SeaTalk1 port is directly tied to the common ground plane of the white and blue SeaTalkng backbone ports.
If an installer connects the converter into an existing SeaTalk1 loop without modifying the power layout, a ground loop is created:
text
  [ House Battery Main Ground Bus ]
     │                              │
     │ (Heavy DC Negative Cable)    │ (Heavy DC Negative Cable)
     ▼                              ▼
[ Autopilot / Old System ] ───► [ E22158 Converter ] ───► [ Modern Backbone (STng) ]
     ▲                                                          ▲
     └───────────── ACCIDENTAL LOOP PATHWAY ────────────────────┘
                  (Through thin ST1 Ground Wires)
Use code with caution.
Because electricity follows the path of least resistance, structural ground currents from high-load devices (like an autopilot drive unit or engine starter motor) can bypass heavy battery negative cables and travel through the thin shield wires of the data communication lines.

System Anomalies Caused by Ground Loops

• Data Corruption: The stray current flowing through the communication ground shifts the absolute zero-volt reference point upward (e.g., to 0.8V or 1.2V). When a SeaTalk1 device pulls the yellow line down to 0V, the converter perceives the elevated ground voltage as an ambiguous state, dropping packets and causing data dropouts.
• Hardware Destruction: If the primary engine ground strap or main negative bus bar degrades, hundreds of amps of engine cranking current will search for an alternative path back to the battery. It will surge down the SeaTalk1 cable, vaporizing the internal circuits of the E22158 converter and destroying any attached instrument displays.

The Isolation Solution

To safely run dual-powered systems—where both the SeaTalk1 loop and the SeaTalkng backbone have independent, dedicated power supplies—you must follow a strict isolation protocol:
text
[ Powered ST1 Loop ] ────( YELLOW Data Connected )────► [ E22158 Converter ]
(e.g., Autopilot)     ────( BLACK Ground Connected )───► (Tied to STng Power)
                      xxxx( RED +12V WIRE SEVERED )xxxx
Use code with caution.
1. Sever the Red Wire: You must physically cut, disconnect, or isolate the Red (+12V) wire inside the SeaTalk1 cable link immediately before it plugs into the yellow port of the E22158 converter block.
2. Maintain Data and Ground: The Yellow (Data) and Black/Shield (Ground) wires must remain fully intact and connected through to the converter.
3. Resulting Stability: The legacy network continues to draw its high-amperage operating power locally from its original source (like the autopilot course computer), while the modern SeaTalkng backbone safely powers the converter block. Because the red power connection is broken, no current can back-feed or loop between the two 12V supplies, while the shared black wire preserves the essential 0V reference point needed for the yellow data line to function reliably.
Would you like to examine the specific data sentences that the E22158 translates between SeaTalk1 and NMEA 2000 (such as wind, depth, or navigation commands), or do you need help designing a microcontroller interface circuit using optocouplers?

```

Use this as a starting point and also an example of how detail and verbose I am 
expecting those documention file to be. Perform your own research on the topic, 
verify the accuracy of the content and expand on more details if necessary. Do not
attempt at summarizing or condensing this content as the level of detail is 
important. This is meant to be in-depth. Focus on verifying the accuracy, 
and expending (if relevant) the knowledge with more details, examples, links, 
etc. 

It is important to me to inline web resources that support the various information
provided in this document. 

# Contribution guideline

- create a dedicated branch in git to perform the task
- once the task initial implementation is complete, push to origin and create a
  pull request
- keep lines under 80 characters
- update the README.md file concisely after completing the task to help a
  coding agent understand what has been done and build on top.
- include this modified @prompt.md file into the commit/pull request

# Implementation feedback

This section is to provide iterative feedback on the ongoing task
implementation.
