# Goal 

The goal is to update the iTC-5 part description with an important caveat about which sensor
should be connected to it. See information below:

```
Raymarine’s strict system requirement is that autopilot critical sensors must wire directly into the course computer (S2G), not an external network converter.
1. Safety and Latency: The S2G needs immediate, sub-millisecond analog feedback from the compass and rudder to calculate course corrections. Running that data through an iTC-5 and onto a busy network introduces a processing delay that can cause your autopilot to oversteer or fail completely.
2. Network Bridging: As confirmed before, your S2G is already publishing this data. By adding a simple bridge or a Raymarine SeaTalk to SeaTalkng Converter, that data will automatically populate on your NMEA 2000 (N2K) network anyway.
```


# Contribution guideline

- create a dedicated branch in git to perform the task
- once the task initial implementation is complete, push to origin and create a
  pull request
- keep lines under 80 characters
- update the README.md file concisely after completing the task to help a
  coding agent understand what has been done and build on top.
