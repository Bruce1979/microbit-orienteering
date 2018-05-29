from microbit import *
import radio

images = {
  '0' : Image.HAPPY,
  '1' : Image.SAD,
  '2' : Image.GIRAFFE,
  '3' : Image.RABBIT,
  '4' : Image.DUCK,
  '5' : Image.GHOST,
  '6' : Image.DIAMOND,
  '7' : Image.SWORD,
  '8' : Image.PACMAN,
  '9' : Image.HOUSE
}

MY_ID = '0'
visitors = []
radio.config(power=0)
radio.on()
mode="flag"

while True:
    
  # mode switching
  if button_a.is_pressed():
    if mode == "flag":
      mode = "visitors"
    elif mode == "visitors":
      mode = "flag"
    display.clear()
  
  # define modes
  if mode == "flag":  
    display.show(images[MY_ID])
    radio.send(MY_ID)
    visitor = radio.receive()
    if visitor:
      if visitor not in visitors:
        visitors.append(visitor)
    sleep(1000)
  elif mode == "visitors":
    for v in visitors:
      display.scroll(v)
      sleep(1000)
    display.clear()
    sleep(1000)
    mode = "flag"
    