# Doing audio between a mic and display over MQTT

This repo contains the code to visualize sound data.  There are two sides:
* mic_full.py - the microphone program which samples the sound over USB
* dual_display.py - the display program which uses the RGB matrix to display both time and frequency info for the sampled audio signal.

To make these work, you need to install Mosquitto (see my notes at https://github.com/gsalaman/mqtt_explore).

You'll need to edit the various files to point at the Mosquitto server you've set up.  Right now, they're hardcoded to my pi.

Note those files don't necessarily need to be on the same pi.

## Time scaling notes
### Display side
In the display application, total_columns will tell the width of the display.  It's initialized by setting the following variables at the bottom of dual_client.py:
```
matrix_rows = 64
matrix_columns = 64
num_hor = 1
num_vert = 1
```
This will then set the appropriate variables inside of our Screen class and send them over to the microphone. 

### Microphone side
The mic application samples a chunck of 1024 concurrent samples at 44.1 KHz.
We'll send only enough samples to fill the total number of columns on the display.

The `display/time/y_ctl` topic will either zoom in or zoom out in the y dimention (magnitude) depending on whether the payload is a + or -.  Note that we can send a bigger number than the display can show, but the display will bound that number.

The `display/time/x_ctl` topic deals with the time (or x) dimension.  At the minimum bound, we'll send one sample per pixel.  As the bound increases by 1, we'll skip every other sample (effectively halving the sample rate, and showing more "time" per screen).  + zooms in, - zooms out. 

## Frequency notes (pun intended)
### Display side
The main parameter for frequency on the display side is the number of pixels per frequency "bin".  We can set this through MQTT with the topic `display/freq/pixels_per_bin`

Note that the number of frequency bins displayed is the number of total rows divided by the bin size in pixels.  We'll send this info over to the mic as `display/freq/num_bins`.  This should only be sent by the display program.
### Microphone side
On the Mic side, we start by doing a raw FFT of our input samples.  We'll only send over the number of frequency bins that the display requests.  

Inside each frequency bin, we can combine FFT points to make the bins "wider" (in frequency, not in pixels).  This can be controlled with `display/freq/num_pts_per_bin`.

In addition, we can change the y axis scaling of the raw FFT output via the `display/freq/y_ctl` topic.  + zooms in, - zooms out.
