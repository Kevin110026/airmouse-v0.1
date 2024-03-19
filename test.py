import numpy
import pyautogui
import mouse
import tools
import copy
import openpyxl


a=numpy.array([1,2,3,4])
b=copy.deepcopy(a[:2])
print(b)
a[0]=0
print(b)

