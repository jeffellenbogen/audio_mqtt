
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

  ############################################
  # send_size 
  #   broadcasts the display size 
  ###############################################
  def send_size(self, client):
    client.publish("display/columns", str(self.total_columns))
    client.publish("display/rows", str(self.total_rows/2)) 
   
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

    for data_index in range(0,self.total_columns-1):
      new_x = last_x + 1 
      new_y = sound_data[data_index] 
      self.draw.line((last_x, last_y, new_x, new_y),fill=(0,0,255)) 
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

    # first iteration:  each data point is a 1-pixel rectangle (line?) going up.
    # Note the bad dependency here....I need more data than columns...
    for x in range(0,self.total_columns):
      y = self.total_rows - sound_data[x]
      if y < top_freq_row:  
        y = top_freq_row 
      if y > self.total_rows:
        y = self.total_rows  

      self.draw.line((x, self.total_columns, x, y),fill=(0,0,255)) 

    self.matrix.SetImage(self.screen,0,0)

matrix_rows = 64
matrix_columns = 64
num_hor = 1
num_vert = 1

display = Screen(matrix_rows, matrix_columns, num_hor, num_vert)

def on_message(client, userdata, message):
  global display

  #print "Message Callback"

  payload = message.payload
  sound_data = []
  for item in payload:
    sound_data.append(ord(item)) 

  if message.topic == "audio/time_samples":
    display.show_time_data(sound_data) 
  elif message.topic == "audio/freq_data":
    display.show_freq_data(sound_data)

#broker_address="10.0.0.17"
broker_address="raspberrypi_glenn"
client = mqtt.Client("time_display")
client.on_message=on_message
client.connect(broker_address)
client.loop_start()
client.subscribe("audio/#")

display.send_size(client)

try:
  print("Press CTRL-C to stop")
  while True:

    print "click!"
    time.sleep(1)

except KeyboardInterrupt:
  exit(0)
