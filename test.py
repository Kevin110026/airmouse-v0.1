import numpy
import pyautogui
import mouse
import tools
import copy

a = numpy.array([[1, 2], [3, 4]])
b=a.copy()
b[0] = a[0]
a[1] = b[0]
print(a)