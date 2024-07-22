EyetrackertestBasedOnPicture.py (main folder) does the following:

- imports Eyelink code from eyetrackingCode subfolder
- Asks for file name to save the data
- Tries to create eyetrackingtest_results folder
- creates a folder for current session, including current time
- Tries to connect to eyelink via ethernet cable
- Tries to open EDF file on Host PC
- Tries to add header text to EDF file
- Puts tracker in offline mode
- Asks tracker for what version it is
- Sets up pyglet window to draw stimuli
- 