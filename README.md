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

## Time scaling notes
I've got some of the time scaling parameters tunable..see the callback in the various mic files for the actual commands.

## Frequency notes (pun intended)
### Display side
The display side has two main parameters:
total_columns will tell the width of the display.  It's initialized by setting the following variables at the bottom of dual_client.py:
```
matrix_rows = 64
matrix_columns = 64
num_hor = 1
num_vert = 1
```
This will then set the appropriate variables inside of our Screen class.  Note that while we send the display info over to the microphone, we do not use that info for frequency display.

The other parameter on the display side is the number of pixels per frequency "bin".  We can set this through MQTT with the topic `display/freq/pixels_per_bin`

Note that the number of frequency bins displayed is the number of total rows divided by the bin size in pixels.  We'll send this info over to the mic as `display/freq/num_bins`
### Microphone side
On the Mic side, we start by doing a raw FFT of our input samples.  We'll only send over the number of frequency bins that the display requests.  

Inside each frequency bin, we can combine FFT points to make the bins "wider" (in frequency, not in pixels).  This can be controlled with `display/freq/num_pts_per_bin`.
