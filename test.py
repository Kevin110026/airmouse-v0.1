import numpy
import pyautogui
import mouse

import fps
FPS = fps.fps()

for i in range(10):
    pyautogui.scroll(1,_pause=False)
    print(FPS.get())
    
    
for i in range(10):
    mouse.wheel(1)
    print(FPS.get())