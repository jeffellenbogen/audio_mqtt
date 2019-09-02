#  This is my test program to see how to pack, transmit, and unpack array 
#  data between two MQTT clients.

import paho.mqtt.client as mqtt
import time

# Callback for simple message
def on_message(client, userdata, message):
  print "Message callback!"

  payload = message.payload
  for item in payload:
    print(ord(item))

broker_address="10.0.0.17"
client = mqtt.Client("simple")
client.on_message=on_message
client.connect(broker_address)
client.loop_start()
client.subscribe("audio")
myData = [1,2,3,4,5]
packedData = bytearray(myData)

for value in packedData:
  print(value)

client.publish("audio",packedData )

time.sleep(4)
client.loop_stop()
