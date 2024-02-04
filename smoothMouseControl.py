import mouse
import numpy
import pyautogui
import screeninfo


def mousePosScale(Pos, scale):
    Pos -= 0.5
    Pos *= scale
    Pos += 0.5
    Pos[0] = max(0, min(1, Pos[0]))
    Pos[1] = max(0, min(1, Pos[1]))
    return Pos


class control:

    def __init__(self, smooth=5):
        self.smooth = smooth
        self.screenMonitors = screeninfo.get_monitors()
        self.screenSize = numpy.array(
            (self.screenMonitors[0].width, self.screenMonitors[0].height))
        self.setToMousePos()
        self.avgScreenSize = self.screenSize.sum() / 2

    def setToMousePos(self):
        self.mousePosRecord = numpy.array(pyautogui.position() * self.smooth)
        self.mousePosRecord.resize((self.smooth, 2))

    def speedMove(self):
        if (((self.mousePosRecord[0] - self.getPos())**2).sum()**0.5
                >= 0.05 * self.avgScreenSize):
            for i in range(1, self.smooth):
                self.mousePosRecord[i] = self.mousePosRecord[0]

    def setPos(self):
        self.speedMove()
        x, y = self.getPos()
        x = int(x)
        y = int(y)
        mouse.move(x, y)

    def getPos(self):
        self.curPos = self.mousePosRecord.sum(axis=0) / self.smooth
        return self.curPos

    def pushPos(self, Pos, setPos=True):
        newPos = numpy.array(Pos)
        newPos[0] = max(0, min(self.screenSize[0] - 1, newPos[0]))
        newPos[1] = max(0, min(self.screenSize[1] - 1, newPos[1]))
        for i in range(self.smooth - 1, 0, -1):
            self.mousePosRecord[i] = self.mousePosRecord[i - 1]
        self.mousePosRecord[0] = newPos
        if setPos:
            self.setPos()

    def pushDis(self, Dis, setPos=True):
        newPos = numpy.array(Dis + self.mousePosRecord[0])
        self.pushPos(newPos, setPos)

    def mouseDown(self, button):
        pyautogui.mouseDown(button=button)

    def mouseUp(self, button):
        pyautogui.mouseUp(button=button)

    def keyDown(self, button):
        pyautogui.keyDown(button)

    def keyUp(self, button):
        pyautogui.keyUp(button)

    def scroll(self, val):
        mouse.wheel(int(val / 50))
        # pyautogui.scroll(int(val))
