import numpy
import pyautogui
import mouse
import tools
import copy

box = {"a": 1, "b": 2, "c": {"x": 3, "y": 4}}
print(box)
print(box["a"])
print(box["c"]["x"])
box2 = copy.deepcopy(box)
box2["a"] = 5
print(box["a"])