#!/usr/bin/python
#
# Traffic Light Control Program
# For use with LowVoltageLabs traffic light
# Pi-Traffic light installation
#   http://wiki.lowvoltagelabs.com/pitrafficlight
# Pi-Traffic light programming example
#    http://wiki.lowvoltagelabs.com/pitrafficlight_python_example
#
# Summary: There are 3 LEDs: Green, Yellow, and Red.
# Use traffic_control.py to turn them on or off
# for various combinations and durations
#
# Author: Peter Sichel 1-Jan-2018
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT

from traffic_control import *

# Traffic Light Main execution
# Use an instance of piTrafficLight for each traffic light
# pass in the gpio pins if not using the defaults (9,10,11)
trafficL1 = piTrafficLight()
# trafficL2 = piTrafficLight(redPin=4, yellowPin=3, greenPin=2)


print("\nHello and welcome to the traffic light controller")
run = True
while(run):
    # gather input
    action = int(input("\nWhat would you lke to do next?"
        "\n1=Turn on"
        "\n2=Turn off"
        "\n3=Turn on for duration"
        "\n4=Start blinking with duration"
        "\n5=Stop blinking"
        "\n6=Sequence colors: Red, Green, Yellow"
        "\n7=Stop sequence"
        "\n8=Exit\n"))
    if action<6: 
       color = int(input("What a color?\n1=Red; 2=Yellow; 3-Green\n"))
       if action>2 and action<5:
           duration = float(input("What duration (fractional seconds)?\n"))
    # perform requested action
    if action==1:
        trafficL1.turnOnColor(color)
    elif action==2:
        trafficL1.turnOffColor(color)
    elif action==3:
        trafficL1.turnOnColorForDuration(color, duration)
    elif action==4:
        trafficL1.startBlinkingColorWithDuration(color, duration)
    elif action==5:
        trafficL1.stopBlinkingColor(color)
    elif action==6:
        trafficL1.startSequence()
    elif action==7:
        trafficL1.stopSequence()
        print("Sequence Stopped")
    elif action==8:
        if trafficL1.sequenceInProgress:
            trafficL1.stopSequence()
            print("Sequence Stopped")
        trafficL1.stopBlinkingColor(RED)
        trafficL1.stopBlinkingColor(YELLOW)
        trafficL1.stopBlinkingColor(GREEN)
        
        trafficL1.turnOffColor(RED)
        trafficL1.turnOffColor(YELLOW)
        trafficL1.turnOffColor(GREEN)

        print("Goodbye")
        run = False


