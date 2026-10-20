# Goal 

The goal is to add a new part in the @parts folder, the raymarine E22158. This
part is currently not in used in the seagram electronic architecture, however
it is something that is a possible upgrade to keep some items on SeaTalk1 while
other on N2K. Coupled with the
/Users/maximeransan/Documents/dev/seagram-electronics/parts/YDWG-02.md  or
/Users/maximeransan/Documents/dev/seagram-electronics/parts/YDNU-02.md it could
also allowed OpenPlotter to communicate with SeaTalk1.

Use any web resources to find the required information and follow the markdown
structure used in other parts within the @parts folder, in particular the
`Device Identifier` section must have same properties.

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

## 1. Remove With YDNU-02 / YDWG-02 sections

From what I understand those 2 sections are redundant with information already
present in those devices md files. If you confirm them remove the section.

## 2. Follow up questions regarding power isolation

if most of the network devices are seatalk1, is it possible to have the N2K bus
power source be from the seatalk1 yellow spur. are there power limitation to
this setup if indeed it is possible to do so. For instance N2K side limited
amperage from the converter

## 3. Follow up question regarding "insulating" the power cable

Can you describe more precisely what would it take to ensure the connected
cable is insulated.
