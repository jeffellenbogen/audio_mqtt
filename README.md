# An MQTT-based audio visualizer

This repo contains the code to visualize sound data.  There are two sides:
* mic_full.py - the microphone program which samples the sound over USB
* dual_display.py - the display program which uses the RGB matrix to display both time and frequency info for the sampled audio signal.

Note these two sides don't necessarily need to be running on the same pi.

To make these work, you need to install Mosquitto (see my notes at https://github.com/gsalaman/mqtt_explore).

By default, MQTT is pointing at the mosquitto server on localhost.  If you want it to point somewhere else, make a "broker.conf" file that contains only one line: the desired hostname or ip address.  

# Public API
## vs Time Display (top)
| MQTT Topic | Payload | Description |
|---|---|---|
| display/time/x_ctl | "+" or "-" | Zooms in or out on the x-axis (time) |
| display/time/y_ctl | "+" or "-" | Zooms in or out on the y-axis (magnitude) |

## vs Frequency Display (bottom)
| MQTT Topic | Payload | Description |
|---|---|---|
| display/freq/pixels_per_bin | number | Sets the number of pixels per frequency bin for the frequency display.  Fewer pixels-per-bin means you can look at a wider frequency range, as more "bins" will fit on the screen |
| display/freq/y_ctl | "+" or "-" | Scales the y axis (magnitude) of all frequency bins |
| display/freq/num_pts_per_bin | number | This sets the number of frequency points that go into each frequency bin.  More points per bin means each bin contains more frequencies (eg is wider) and therefore you can span a longer frequency range |
  
# Design notes
## Time scaling notes
### Display side
In the display application, total_columns will tell the width of the display.  It's initialized by setting the following variables at the bottom of dual_client.py:
```
matrix_rows = 64
matrix_columns = 64
num_hor = 1
num_vert = 1
```
This will then set the appropriate variables inside of our Screen class and send them over to the microphone via the `display/columns` and `display/rows` messages.

### Microphone side
The mic application samples a chunck of 1024 concurrent samples at 44.1 KHz.
We'll send only enough samples to fill the total number of columns on the display.

Note that if the microphone starts before the display, all is good, as the display will send us over the number of columns and rows when it starts up.  However, if the display is running first, we need some way for the microphone to query that display size.  It does so via the `display/get_size` message.

The `display/time/y_ctl` topic will either zoom in or zoom out in the y dimention (magnitude) depending on whether the payload is a + or -.  Note that we can send a bigger number than the display can show, but the display will bound that number.

The `display/time/x_ctl` topic deals with the time (or x) dimension.  At the minimum bound, we'll send one sample per pixel.  As the bound increases by 1, we'll skip every other sample (effectively halving the sample rate, and showing more "time" per screen).  + zooms in, - zooms out. 

## Frequency notes (pun intended)
### Display side
The main parameter for frequency on the display side is the number of pixels per frequency "bin".  We can set this through MQTT with the topic `display/freq/pixels_per_bin`

Note that the number of frequency bins displayed is the number of total rows divided by the bin size in pixels.  We'll send this info over to the mic as `display/freq/num_bins`.  This should only be sent by the display program.  Note it does so (along with the aforementioned rows and columns) either on boot or in response to a `display/get_size` message.

### Microphone side
On the Mic side, we start by doing a raw FFT of our input samples.  We'll only send over the number of frequency bins that the display requests.  

Inside each frequency bin, we can combine FFT points to make the bins "wider" (in frequency, not in pixels).  This can be controlled with `display/freq/num_pts_per_bin`.

In addition, we can change the y axis scaling of the raw FFT output via the `display/freq/y_ctl` topic.  + zooms in, - zooms out.

## Coming soon...
| MQTT Topic | Payload | Description |
|---|---|---|
| display/time/trigger_ctl | "on" or "off" | Turns on or off triggering for the time display |
| display/time/trigger_level | number | Sets the trigger level to that number of pixels above our "bias" level. |

If the trigger never fires, we need to not hang the mic...just do the next chunk process without sending audio data.  Can still send frequency data.
