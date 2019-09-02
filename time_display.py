
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

    self.screen = Image.new("RGBA",(self.total_columns,self.total_rows))

  ############################################
  # send_size 
  #   broadcasts the display size 
  ###############################################
  def send_size(self, client):
    client.publish("display/columns", str(self.total_columns))
    client.publish("display/rows", str(self.total_rows)) 
   
matrix_rows = 64
matrix_columns = 64
num_hor = 1
num_vert = 1

display = Screen(matrix_rows, matrix_columns, num_hor, num_vert)

def display_data(sound_data):

  print(sound_data)

'''
    last_x = 0
    last_y = 32

    for data_index in range(0,64):
      new_x = last_x + 1 
      try:
        new_y = sound_data[data_index] 
      except:
        err_count = err_count+1
        print("sound data index issue"+str(err_count))
        continue
      draw.line((last_x, last_y, new_x, new_y),fill=blue) 
      last_x = new_x
      last_y = new_y

    matrix.SetImage(image,0,0)
'''

def on_message(client, userdata, message):
  print "Message Callback"

  payload = message.payload
  sound_data = []
  for item in payload:
    sound_data.append(ord(item)) 

  display_data(sound_data) 

broker_address="10.0.0.17"
client = mqtt.Client("time_display")
client.on_message=on_message
client.connect(broker_address)
client.loop_start()
client.subscribe("audio/time_samples")

display.send_size(client)

try:
  print("Press CTRL-C to stop")
  while True:

    print "click!"
    time.sleep(1)

except KeyboardInterrupt:
  exit(0)
