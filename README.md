
TO-DO

* switched from typing responses to using mouse to click on lineup, to accommodate eyetracking

## Eyetracking problems

Initial calibration works but drift-correction code doesn't do anything, even though works in picture.py.
I'm guessing that the issue is that a separate graphical environment (genv) was opened for the eyetracker calibration, which got overwritten by the Psychopy stimulus graphics window.

The following code looks relevant.

````
#Request Pylink to use the PsychoPy window we opened above for calibration
pylink.openGraphicsEx(genv)
````
