# Goal 

I would like to make a similar doc as the @docs/bilge-pump-monitoring.md  but
this time I woud like to architect the integration of a bluetooth remote
control with the HAMLET board (which will be connected to N2K) so that it can
control the auto pilot. In particular I would like the remote control to
provide the classic +1/-1 +10/-10 and tack  (equivalent to the +1 combined with
+10 or -1 combined with -10 command for raymarine control head).

# Contribution guideline

- create a dedicated branch in git to perform the task
- once the task initial implementation is complete, push to origin and create a
  pull request
- keep lines under 80 characters
- update the README.md file concisely after completing the task to help a
  coding agent understand what has been done and build on top.
- include this modified @prompt.md file into the commit/pull request (in other
  do not do git restore).
