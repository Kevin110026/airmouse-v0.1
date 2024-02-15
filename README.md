# Introduction
this is the next version of the airmouse v0.0
"supposed" to be more accurate and handy

...

don't blame me if I mess it up instead...

# before use
- python required
- install requirements first by runing `pip install -r req.txt` in command line


# how to use:
    
after the camera is activated, move your hand into the camera

curve your thumb to start controlling mouse by hand

curve all fingers to quit controlling mode(looks like a cat's paw)

the system quit controlling mode automatically once the camera can't detect any hand

## mouse moving
**thumb:**

Mouse will be dragged by your hand as long as you keep the thumb curved

## mouse left click 
**forefinger:**

Curve it to hold and uncurve it to release

Curve then uncurve it fast to click, just like common mouse
## mouse right click
**middle finger:**

Curve it to hold and uncurve it to release

Curve then uncurve it fast to click, just like common mouse, idk why do you need double right click anyway
## mouse scrolling
**ring finger:**

Curve it then move your hand to scroll.

The mouse can't be dragged while scrolling
## mouse slow moving mode
**little finger:**

Curve it to make dragging/scrolling slow down.

You still have to curve the thumb or ring finger to drag/scroll while in slow moving mode
## mouse left double click 
**forefinger( & middle finger):**

Original method: This can be done by left clicking twice fast.

Another method: Curve forefinger first then curve middle finger to double click.
        
`This additional rule is designed to make you still be able to double click under low fps, which is hard to be done by the original method`
## zooming 
**thumb & ring finger:**

curve both of them of the same time to zoom in/out the page


# Common Issues:

## camera

`Exception: Unable to access camera, please check README.md for more info`

check if the camera wasnt attached, or the permission got denied 

you can also try changing the `CAM_NUM` inside main.py(line 15) to 1 or 2 (depending on ur camera's id)
