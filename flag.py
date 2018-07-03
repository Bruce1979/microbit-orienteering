""" flag.py

Author: Bruce Fuda
Developed for the microbit-orienteering project at Telopea Park School
to assist with teaching Digital Technologies content in Year 8 integrated PE
License: CC-BY-4.0

This module is uploaded to the "flags" that will be the destination points
for the orienteering course.  Flags operate in two modes:
    - 'flag' mode is the default and displays the flag's identifier image and
      transmits that flag's presence to nearby compasses.  It performs a
      cyclical broadcast of its identifier, prepended with each of the courses
      on which it is present.  This is used by receiving compasses to determine
      if the flag is on their course and, if it is, to identify the flag as a
      recipient for the compass id.  Flags store compass ids and the course that
      compass is on so that they can be displayed when in 'vistors' mode.
    - 'visitors' mode is used to display the compasses that have visited the
      flag for any given course.  After displaying the list of visitors for a
      chosen course, it automatically reverts to 'flag' mode.

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
## CORRESPONDING IMAGES LIST IN THE compass.py FILE.
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

## Set the ID for the flag and the courses this flag is part of
MY_ID = 'A'   # must be key in list of images and unique across all flags
MY_COURSES = ['1','2','5']  # must be a list of single digits

## create a list that will track the visitors in the order they arrive
visitors = []

## configure the radio to transmit at its weakest strength, saving power
## and reducing the range of the broadcast signal so that compasses must
## get close for it to be detected
radio.config(power=0)
radio.on()

## set the starting mode for the flag - it will begin in 'flag' mode
mode = "flag"

## This loop ensures that the code runs as long as the flag has power
while True:

  # define modes
  ## flag mode broadcasts the flag ID and tracks visitors
  if mode == "flag":
    ## if button A is pressed/held down while in this mode, the flag switches
    ## into visitors mode and the display is cleared.
    if button_a.is_pressed():
      mode = "visitors"
      display.clear()
    ## otherwise, we begin transmission/receiving of data
    else:
      ## when in flag mode, we display the flag's identity so it is visible
      display.show(images[MY_ID])
      ## we need to transmit not just the flag's ID, but the courses it is
      ## a part of.  The message sent consists of the flag's ID prepended with
      ## the course it is a part of.  Where it is on multiple courses, we need
      ## to rotate through the list of courses, and transmit each combination
      ## separately.
      for course in MY_COURSES:
        ## construct the message to be sent, using the current course and the
        ## flag ID.  Send it using the radio protocol.
        radio.send(course+MY_ID)
        ## attempt to catch any receiving message from a visitor if they are
        ## on the correct course.
        visitor = radio.receive()
        if visitor:
          ## if the visitor sent a response, check to see which course it is on
          ## by extracting the first character of its message
          visitor_course = visitor[0]
          ## if the visitor is on one of the courses the flag is on...
          if visitor_course in MY_COURSES:
            ## and if the visitor hasn't already visited this flag on this
            ## course
            if visitor not in visitors:
              ## add the visitor to the list of visitors.  Note we store the
              ## whole message including the course number, since a visitor
              ## may visit the flag multiple times for different courses and
              ## we need to be able to distinguish between them.
              visitors.append(visitor)
        ## pause code execution for a short time between each transmission
        sleep(600)
  ## visitors mode displays the visitors from the selectec course
  elif mode == "visitors":
    ## we need to identify which course to display.  By default, we'll extract
    ## the course id that appears first in the list of courses.  This always
    ## has an index of 0.
    course_to_view = 0 # index of course to display
    ## while in this mode, we'll continuously wait for a button press.  We can
    ## do this with an infinite loop, which we'll break from when we return
    ## to flag mode
    while True:
      ## button B will be used to cycle through the list of courses this flag
      ## is a part of - it does this by advancing the index by 1 through the
      ## list, and rotating back to 0 if we end up "off the end" by advancing
      ## to the length of the list
      if button_b.is_pressed():
        course_to_view += 1
        ## if the index stored in course_to_view ever gets to the length of the
        ## lst, it has gone too far and should be set to 0 (the start) instead.
        if course_to_view >= len(MY_COURSES):
          course_to_view = 0
        ## Show which course is currently selected on the micro:bit display
        display.show(MY_COURSES[0])
        sleep(600)
      ## button A will be used to show the visitors for the selected course
      if button_a.is_pressed():
        ## We will iterate over the visitors list, which will preserve the
        ## order they visited the flag.
        for v in visitors:
          ## extract the course id from the data that is stored so that we only
          ## show visitors for the chosen course
          visitor_course = v[0]
          ## compare the visitors course with the chosen course and, if they
          ## match, we'll display the visitor's id
          if visitor_course == course_to_view:
            ## the data stored includes the course as the first character in the
            ## data string, so the visitor's id is everything from the second
            ## character (the character at index 1) through to the end.  Extract
            ## this and then scroll in on the micro:bit display.
            visitor_id = v[1:]
            display.scroll(visitor_id)
            ## pause for one second after each so that we can distinguish
            ## between them all
            sleep(1000)
        ## once we've displayed all of the relevant visitors, clear the display
        ## switch to flag mode and exit this loop to revert to the main loop
        display.clear()
        mode = "flag"
        break
