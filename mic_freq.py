# Some freq notes:
#   - 1 KHz is about the 24th bin of raw FFT data.  
#     So, 100 frequency points would give me about 4 KHz of sound data.
#   - I'm gonna start by sending it raw and have the other side just do 
#       Bars at the right place...that'll let me confirm we're linear.
#   - Later, I'm going to average the bins.  Start by averaging them 
#     on this side before sending them over...

import pyaudio
import struct
import numpy as np

import paho.mqtt.client as mqtt
import time

CHUNK = 1024 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
DEV_INDEX = 0

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input_device_index=DEV_INDEX,input=True,output=False,frames_per_buffer=CHUNK)
 
#sample_jump = CHUNK/64
sample_jump = 2
sample_scale = 100

freq_scale = 4 
num_freq_bins = 100 

total_rows = 32
total_columns = 32
sample_bias = total_rows / 2 

def on_message(client, userdata, message):
  global total_rows
  global total_columns
  global sample_bias
  global sample_jump
  global sample_scale

  if message.topic == "display/columns":
    total_columns = int(message.payload)
    print("setting total columns to "+str(total_columns))
  elif message.topic == "display/rows":
    total_rows = int(message.payload)
    sample_bias = total_rows / 2
    print("setting total rows to "+str(total_rows))
  elif message.topic == "display/x_ctl":
    if message.payload == "+":
      print "X IN"
      # zoom in by one "click"...factor of 2
      if (sample_jump > 1):
         sample_jump = sample_jump / 2
         print "new x sample zoom:  "+str(sample_jump)
      else:
         print "already zoomed in as far as we can"
    elif message.payload == "-":
      print "X OUT"
      # zoom out by one "click"...factor of 2
      sample_jump = sample_jump * 2
         
      #saturate our sample jump so that we're always displaying the max
      # number of displayable points
      if (CHUNK / sample_jump) < total_columns:
         print "Saturating sample zoom"
         sample_jump = CHUNK/total_columns

      print "setting sample jump to "+str(sample_jump)
    else:
        print "bad x_ctl payload"
        print message.payload

  elif message.topic == "display/y_ctl":
    if message.payload == "+":
      print "Y IN"
      # zoom in by one "click"...factor of 2
      sample_scale = sample_scale / 2
    elif message.payload == "-":
      print "Y OUT"
      # zoom out by one "click"...factor of 2
      sample_scale = sample_scale * 2

    print "new y sample zoom:  "+str(sample_scale)

  else:
    print("Unknown message on display topic:"+message.topic)
    print("Payload: "+message.payload)

#broker_address="10.0.0.17"
broker_address="raspberrypi_glenn"
client = mqtt.Client("Microphone")
client.on_message=on_message
client.connect(broker_address)
client.loop_start()
client.subscribe("display/#")

try:
  print("Hit ctl-c to exit")
  while (True):
    data = stream.read(CHUNK,exception_on_overflow = False)
    data_int = struct.unpack(str(CHUNK) +'h', data)  

    '''        
    scaled_data = []
 
    for point in range(0,total_columns-1):
       point_index = point*sample_jump
       scaled_point = sample_bias + data_int[point_index]/sample_scale
       if scaled_point < 0:
          scaled_point = 0
       if scaled_point > 255:
          scaled_point = 255 
       scaled_data.append(scaled_point)

    packed_data = bytearray(scaled_data)
    client.publish("audio/time_samples",packed_data) 
    '''

    # do numpy's fft
    Y_k = np.fft.fft(data_int)[0:int(CHUNK/2)]/CHUNK

    # only grab single sided spectrum
    Y_k[1:] = 2*Y_k[1:]

    # Calc magnitude, truncating to integers
    Pxx = np.abs(Y_k)
    freq_int = Pxx.astype(int)
     
    # now pack them into our sending stream.  
    scaled_freq_data = []
    point_index = 0
    for point in range(0, num_freq_bins-1):
      scaled_point = freq_int[point_index]/freq_scale
      if scaled_point < 0:
         scaled_point = 0
      if scaled_point > 255:
         scaled_point = 255
      scaled_freq_data.append(scaled_point)

      point_index += 1

    packed_data = bytearray(scaled_freq_data)
    client.publish("audio/freq_data", packed_data)



    #print("write done")
    #time.sleep(.1)
    
except KeyboardInterrupt:
  exit(0)
