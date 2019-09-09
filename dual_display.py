
import time

import paho.mqtt.client as mqtt

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

class Screen():

  ############################################
  # Init method 
  ###############################################
  def __init__(self, panel_rows, panel_columns, num_horiz_panels, num_vert_panels):
 
    self.total_rows = panel_rows * num_vert_panels
    self.total_columns = panel_columns * num_horiz_panels

    options = RGBMatrixOptions()
    options.rows = matrix_rows 
    options.cols = matrix_columns 
    options.chain_length = num_horiz_panels
    options.parallel = num_vert_panels 
    options.hardware_mapping = 'regular' 
    #options.gpio_slowdown = 2

    self.matrix = RGBMatrix(options = options)

    self.background = None
    self.icons = []

    self.screen = Image.new("RGB",(self.total_columns,self.total_rows))
    self.draw = ImageDraw.Draw(self.screen)

    # default frequency bin params:  one pixel bins, no averaging, mono-color
    self.num_pixels_per_freq_bin = 3
    self.num_freq_bins = self.total_columns / self.num_pixels_per_freq_bin 
    self.freq_display_style = "instant"
    
    self.set_color_palette()
    self.color = 150
    self.y_spread = 1
  ############################################
  # set_client 
  ###############################################
  def set_client(self, client):
    self.client = client

  ############################################
  # set_time_color 
  ###############################################
  def set_time_color(self, color):
    self.color = color%360 #hsl uses colors from 0-360

  ############################################
  # set_y_spread
  ###############################################
  def set_y_spread(self, y_thickness):
    self.y_spread = y_thickness 


  ############################################
  # set_color_palette
  ###############################################
  def set_color_palette(self):
    # we want our palette to go from blue to green to red across the screen.
    # this will be dependent on the number for frequency bins

    # start with an empty palette
    self.palette = []

    # Figure out the color "step size" based on the number of bins.
    # Deal with the fact our num_freq_bins may be odd (and therefore not
    # divisible by 2)
    second_half_num_bins = int(self.num_freq_bins / 2)
    first_half_num_bins = self.num_freq_bins - second_half_num_bins

    #print "first half: "+str(first_half_num_bins)
    #print "second half: "+str(second_half_num_bins)

    # The first half of the palette walks from blue (0,0,255) to green (0,255,0)
    step_size = 255 / (first_half_num_bins - 1)
    for step in range (0, first_half_num_bins):
      temp_color = (0, int(step_size * step), int(255 - (step_size * step)))
      #print temp_color
      self.palette.append(temp_color)
  
    # the second half walks from green to red...but we should already have 
    # had a mostly green one, so start one step towards red.
    step_size = 255 / (second_half_num_bins)
    for step in range (1, second_half_num_bins+1):
      temp_color = (int(step_size * step), int(255-(step_size * step)),0)
      #print temp_color
      self.palette.append(temp_color)
    
  ############################################
  # set_freq_bin_num_pixels
  ###############################################
  def set_freq_bin_num_pixels(self, bin_size):
    self.num_pixels_per_freq_bin = int(bin_size)
    self.num_freq_bins = self.total_columns / self.num_pixels_per_freq_bin 
    print "Set freq bin size to "+bin_size+" pixels"
    self.client.publish("display/freq/num_bins", str(self.num_freq_bins))
    self.set_color_palette()

  ############################################
  # send_size 
  #   broadcasts the display size 
  ###############################################
  def send_size(self):
    self.client.publish("display/columns", str(self.total_columns))
    self.client.publish("display/rows", str(self.total_rows/2)) 
    self.client.publish("display/freq/num_bins", str(self.num_freq_bins))
   
  ############################################
  # show time data 
  #   time data on the top of the screen.
  ###############################################
  def show_time_data(self,sound_data):

    #print(sound_data)

    # black out the old data
    # note time is only top half
    self.draw.rectangle((0,0,self.total_columns, self.total_rows/2),(0,0,0))

    last_x = 0
    last_y = self.total_rows / 4

    time_color ="hsl({}, 100%, 50%)".format(self.color) 
    

    for data_index in range(0,self.total_columns-1):
      new_x = last_x + 1 
      new_y = sound_data[data_index] 
      self.draw.line((last_x, last_y-self.y_spread, new_x, new_y+self.y_spread),fill=time_color) 
      last_x = new_x
      last_y = new_y

    self.matrix.SetImage(self.screen,0,0)

  ############################################
  # show freq data 
  ###############################################
  def show_freq_data(self,sound_data):

    #print(sound_data)

    # black out the old data
    top_freq_row = self.total_rows/2 
    self.draw.rectangle((0,top_freq_row,self.total_columns, self.total_rows),(0,0,0))

    for x in range(0,self.num_freq_bins):
      
      # The mic side does frequency bin averaging...don't need to worry about
      # that here.
      y = self.total_rows - sound_data[x] - 1
      if y < top_freq_row:  
        y = top_freq_row 
      if y > self.total_rows:
        y = self.total_rows  
      
      # two modes...instant and decay
      if self.freq_display_style == "instant":
        x_start = x * self.num_pixels_per_freq_bin
        x_stop = x_start + self.num_pixels_per_freq_bin - 1

        color = self.palette[x]
        self.draw.rectangle((x_start,y,x_stop,self.total_rows),outline=color)

      elif self.freq_display_style == "decay":
        print "Decay currently unimplemented"
        return
      else:
        print "Unknown frequency display style: "+self.freq_display_style
        return

    self.matrix.SetImage(self.screen,0,0)

matrix_rows = 32
matrix_columns = 32
num_hor = 5
num_vert = 3

display = Screen(matrix_rows, matrix_columns, num_hor, num_vert)

def on_message(client, userdata, message):
  global display

  #print "Message Callback"

  if message.topic == "audio/time_samples":
    sound_data = []
    for item in message.payload:
       sound_data.append(ord(item))
    display.show_time_data(sound_data) 
  elif message.topic == "audio/freq_data":
    sound_data = []
    for item in message.payload:
       sound_data.append(ord(item))
    display.show_freq_data(sound_data)
  elif message.topic == "display/freq/pixels_per_bin":
    display.set_freq_bin_num_pixels(message.payload)
  elif message.topic == "display/time/color":
    print "color change "+message.payload
    display.set_time_color(int(message.payload))
   elif message.topic == "display/time/y_spread":
    print "y_spread change"+message.payload
    display.set_y_spread(message.payload)
  else:
    print "unknown topic: "+message.topic

#broker_address="10.0.0.17"
broker_address="makerlabPi1"
client = mqtt.Client("dual_display")
client.on_message=on_message
try:
  client.connect(broker_address)
except:
  print "Unable to connect to MQTT broker"
  exit(0)

client.loop_start()
client.subscribe("audio/#")
client.subscribe("display/freq/#")
client.subscribe("display/time/color")
client.subscribe("display/time/y_spread")

display.set_client(client)
display.send_size()


try:
  print("Press CTRL-C to stop")
  while True:

    print "click!"
    time.sleep(1)

except KeyboardInterrupt:
  exit(0)
