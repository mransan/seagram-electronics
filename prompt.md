# Goal 

The goal is add a new file in @docs folder to describe how to implement an
ESP32 based N2K listener part (aka wired) and create a TCP/UDP server so that
iphone, tablets, or even OpenPlotter SignalK can connect and read the data.

This is essentially building a DIY version of the @parts/YDWG-02.md

The goal is to understand the feasibility from a hardware and software point of
view. What part to purchase and their prices, how they should be connected,
major pieces of software to code and a ton of reference from existing similar
project. The latter should include website, facebook post (lots of ESP32 or
boat electronics group on Facebook) and github projects.


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
implementation. This should only be edited by the prompter.

## 1. Expanding scope and better structure

### 1.a Scope expansion: I2C sensors and 1-wire sensors

We will add to the requirement that the ESP32 can support I2C sensors with a
primary focus on accurate environment monitoring (temperature, humidity and
barometric pressure) as well as gyro sensor to monitor boat heeling, and
finally a compass heading as a backup for the existing raymarine compass.

We will also add the requirement to support 1-wire sensors with a concrete
focus on temperature probes for the engine.

### 1.b restructure 

- section 1. is unchanged in scope as it is generic
- section 2. should be renamed hardware options. After a brief overview there
  should be 3 subsection, one for each of the hardware options
  - 2.1 Discrete prototyping: each component is as bare bone as possible and
    integration requires soldering or development board
  - 2.2 M5Stack: leverage the M5Stack ecosystem of controller, sensors and  and
    components. The prefered solution for this one, should be using the PortABC
    + CANBus unit approach.
  - 2.3 Marine integrated board: SH-ESP32

For each of the subsection 2.1, 2.2, 2.3 follow a consistent sub structure and
content
 - bill of material
 - wiring description: do attempt to draw schematic using ASCI, rather for each
   component and their pin/wire, indicate to which other component it should be
   connected. While verbose it's the most accurate.

The existing 3.1 and 3.2 could be put into the section 1 as those technical
details applies to all 3 hardware solutions.

Section 1 should now contain information regarding the I2C and 1-wire protocols
and sensors.

Section 4. should be folded into 2.2 after taking into account the latest
choice of compoents.

Section 6 can be removed, as those low level code detail should be left to
implementation plan which is not yet in scope. Let's limit this document to
software component and capabilities (library + protocol supported).



