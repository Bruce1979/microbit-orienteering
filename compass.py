""" compass.py

Author: Bruce Fuda
Developed for the microbit-orienteering project at Telopea Park School
to assist with teaching Digital Technologies content in Year 8 integrated PE
License: CC-BY-4.0

This module is uploaded to the "compasses" that will be used by students
completing the orienteering course.  Compasses operate in three modes:
    - 'compass' mode is the default and displays the current directional
      reading as detected by the micro:bit's magnetometer.
    - 'checking' mode is used to activate the radio and scan for nearby signals
      from flags.  This is a separate mode to the compass to help minimise
      power usage.
    - 'showing' mode is used to display the flags that the compass has visited
      on the given course.  After displaying them all, it automatically reverts
      to 'compass' mode.

Comments prefaced with ## are descriptive to explain the code's purpose to the
teacher/student.  They would normally be written in a more succinct way, but
are kept long form to assist with clarity for non-programmers.

"""

## import everything from the microbit module for Python
from microbit import *
## import radio module so that calling radio functions is easier
import radio

## create a dictionary that maps the IDs for each of the flag images
## to the images. This is used in communication and must be present
## in both the compass and flag to ease sending/receiving messages.
## REMEMBER THAT IF THIS LIST IS ALTERED, CHANGES MUST BE REFLECTED IN THE
## CORRESPONDING IMAGES LIST IN THE flag.py FILE.
images = {  # image IDs must be letter strings
  'A' : Image.HAPPY,
  'B' : Image.SAD,
  'C' : Image.GIRAFFE,
  'D' : Image.RABBIT,
  'E' : Image.DUCK,
  'F' : Image.GHOST,
  'G' : Image.DIAMOND,
  'H' : Image.SWORD,
  'I' : Image.PACMAN,
  'J' : Image.HOUSE
}

## Set the ID for the compass and the course it is currently completing
MY_ID = 'BLUE'   # must be unique across all compasses participating
MY_COURSE = '1'  # must be a single digit
MY_TYPE = 'C'    # must be C to indicate 'C'ompass

## Creates a dictionary of images that reflect the position of the needle
## to be shown on the micro:bit display.  The key is used to determine how
## many positions the angle to Magnetic North is from the current position,
## as determined by the bearing reading of the built-in magnetometer.
## NOTE: since decimal numbers can be problematic in computer representation,
## we use integers that count how many intervals of 22.5 degrees we are from
## magnetic north, and use this to display the correct compass arm.
COMPASS = {0 : Image("00900:00900:00900:00000:00000"),
           1 : Image("00090:00090:00900:00000:00000"),
           2 : Image("00009:00090:00900:00000:00000"),
           3 : Image("00000:00099:00900:00000:00000"),
           4 : Image("00000:00000:00999:00000:00000"),
           5 : Image("00000:00000:00900:00099:00000"),
           6 : Image("00000:00000:00900:00090:00009"),
           7 : Image("00000:00000:00900:00090:00090"),
           8 : Image("00000:00000:00900:00900:00900"),
           9 : Image("00000:00000:00900:09000:09000"),
           10 : Image("00000:00000:00900:09000:90000"),
           11 : Image("00000:00000:00900:99000:00000"),
           12 : Image("00000:00000:99900:00000:00000"),
           13 : Image("00000:99000:00900:00000:00000"),
           14 : Image("90000:09000:00900:00000:00000"),
           15 : Image("09000:09000:00900:00000:00000")
           }

## create a list that will track the checkpoints in the order they are visited
checkpoints = []

## configure the radio to transmit at its weakest strength, saving power
## and reducing the range of the broadcast signal so that compasses must
## get close for it to be detected
radio.config(power=0)
radio.on()

## set the starting mode for the compass - it will begin in 'compass' mode
mode = "compass"

## force compass calibration each time the micro:bit is restarted to maximise
## accuracy of the magnetometer
compass.calibrate()

## This loop ensures that the code runs as long as the flag has power
while True:

  # mode switching
  ## switchign modes operates differently on the compass since none of the
  ## modes require any direct user input / manipulation.  Thus, we start
  ## by checking for button presses and, if they are detected, we trigger
  ## the relevant mode switch
  ## pressing button B at any point will switch the micro:bit into 'showing'
  ## mode.  We clear the display of anything as we switch.
  if button_b.is_pressed():
    mode = "showing"
    display.clear()
  ## button A is used to switch between compass and checking modes, so we
  ## check which mode we are currently in and switch to the other if it is
  ## pressed.  Again, clear the display of the current info as we switch.
  elif button_a.is_pressed():
    if mode == "compass":
      mode = "checking"
    elif mode == "checking":
      mode = "compass"
    display.clear()

  # define modes
  ## in compass mode, we get a heading from the compass and then calculate the
  ## relevant bearing to north that we will be showing on our display.  There
  ## is a bit of maths going on here, so we'll do it step by step.
  if mode == "compass":
    ## We get the current heading as calculated from the built-in magnetometer/
    ## compass.  This will be an integer between 0 and 360. Since North is
    ## at zero and we are using regions of 22.5 degress between each measurable
    ## reading, we subtract our heading from 11 (half of 22.5, rounded down) to
    # get a bearing to North.
    north_bearing = 11 - compass.heading()
    ## We now need to convert this into one of the values in our COMPASS
    ## dictionary.  To do this, we divide by 22.5, which is our angle
    ## between each of our displayable compass points. This tells us how many
    ## multiples of 22.5 we are from North, and we round this down to the
    ## nearest integer by using the integer division (//) and converting
    ## to int(). We then use modulus arithmetic to convert it to a positive
    ## value between 0 and 15 by finding % 16
    points_from_north = int((north_bearing // 22.5) % 16)
    ## Point the needle to the nearest "cardinal point" bearing towards
    ## Magnetic North by displaying the correct image from our dictionary
    display.show(COMPASS[points_from_north])
    ## Pause momentarily before getting another reading
    sleep(100)
  ## once we enter checking mode, we'll begin looking for a radio signal from
  ## a nearby checkpoint
  elif mode == "checking":
    ## attempt to catch any messages being sent from nearby checkpoints
    message = radio.receive()
    if message:
      ## before we do anything, we need to check to see if this message came
      ## from a checkpoint (it may be a broadcast from a nearby compass)
      message_type = message[0]
      if message_type == 'F':
        ## Now, check that it is on our course.  The second character from the
        ## message is the checkpoint's course - compare that to ours
        checkpoint_course = message[1]
        if checkpoint_course == MY_COURSE:
          ## if this checkpoint is on our course, then we need to get the
          ## checkpoints id from its message, which is every everything after the
          ## second character (i.e. everything in the message from index 2 onwards)
          checkpoint_id = message[2:]
          ## we then show the relevant image by looking it up in our images
          ## dictionary
          display.show(images[checkpoint_id])
          ## Next, we see if we have recorded this checkpoint before and, if we
          ## haven't already stored its id in our list of checkpoints, we add it
          if checkpoint_id not in checkpoints:
            checkpoints.append(checkpoint_id)
            ## Once we've added the checkpoint into our list of visited
            ## checkpoints, send a message to the checkpoint to indicate which
            ## course we are doing and what our id is so it can store this
            ## information.  We send a message containing our id, prepended with
            # the course we are currently doing and the fact we are a compass.
            radio.send(MY_TYPE+MY_COURSE+MY_ID)
    ## pause for a moment so we don't spam the radio signals in the area
    ## too much
    sleep(100)
  ## in showing mode, we iterate over the checkpoints we've saved and display
  ## them one at a time, for one second each.  This preserves the order they
  ## were visited / saved
  elif mode == "showing":
    for cp in checkpoints:
      display.show(images[cp])
      sleep(1000)
    ## after showing them all on the display, clear the display and switch back
    ## to compass mode, after a short delay.
    display.clear()
    sleep(1000)
    mode = "compass"
