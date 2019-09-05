# PI audio experiments over MQTT

This repo holds my experiments of sending audio data over MQTT.

To make these work, you need to install Mosquitto (see my notes at https://github.com/gsalaman/mqtt_explore).

You'll need to edit the various files to point at the Mosquitto server you've set up.  Right now, they're hardcoded to my pi.

Each experiment is a file pair...one file for generating the sound data, and one for displaying it.  
Note those files *shouldn't* need to be on the same pi, but so far I've only tested it on a single pi.

## Experiment #1:  time
run mic.py and time_display.py.  Note that time_display will need sudo.

## Experiment #2:  frequency
run mic_freq.py and (sudo) freq_display.py

## Experiment #3:  dual display
run mic_full.py and (sudo) dual_display.py

## Tuning notes
I've got some of the time scaling parameters tunable..see the callback in the various mic files for the actual commands.
