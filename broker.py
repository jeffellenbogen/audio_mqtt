
def read():
  try: 
    file = open('broker.conf','r')
   
    for line in file:
       # just get the first line
       return line
  except:
    # if no file exists, return localhost.
    return "127.0.0.1"
