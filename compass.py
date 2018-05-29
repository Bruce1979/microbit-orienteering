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

MY_ID = 'BLUE'

COMPASS = [Image.CLOCK12,
           Image.CLOCK1,
           Image("00009:00090:00900:00000:00000"),
           Image.CLOCK2,
           Image.CLOCK3,
           Image.CLOCK4,
           Image("00000:00000:00900:00090:00009"),
           Image.CLOCK5,
           Image.CLOCK6,
           Image.CLOCK7,
           Image("00000:00000:00900:09000:09000"),
           Image.CLOCK8,
           Image.CLOCK9,
           Image.CLOCK10,
           Image("90000:09000:00900:00000:00000"),
           Image.CLOCK11,
           ]

checkpoints = []
mode = "compass"

radio.config(power=0)
radio.on()
compass.calibrate()

while True:
    
  # mode switching
  if button_b.is_pressed():
    mode = "showing"
    display.clear()
  elif button_a.is_pressed():
    if mode == "compass":
      mode = "checking"
    elif mode == "checking":
      mode = "compass"
    display.clear()
  
  # define modes
  if mode == "compass":
    # Try to keep the needle pointed in (roughly) the correct direction
    sleep(100)
    pos = int(((15 - compass.heading()) // 22.5)) % 16
    display.show(COMPASS[pos])       
    #pos = -int(compass.heading()/22.5)
    #display.show(COMPASS[pos])
  elif mode == "checking":
    checkpoint = radio.receive()
    if checkpoint:
      display.show(images[checkpoint])
      if checkpoint not in checkpoints:
        checkpoints.append(checkpoint)
        radio.send(MY_ID)
    sleep(200)
  elif mode == "showing":
    for cp in checkpoints:
      display.show(images[cp])
      sleep(1000)
    display.clear()
    sleep(1000)
    mode = "compass"
