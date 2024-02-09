import tools
import numpy


class smoothHand:

    def __init__(self, smooth=30):
        self.smooth = smooth
        self.rawPosRecord = numpy.zeros((self.smooth, 2))

    def setPos(self, Pos: numpy.ndarray):
        for i in range(self.smooth):
            self.rawPosRecord[i] = Pos

    def pushPos(self, Pos: numpy.ndarray):
        for i in range(self.smooth):
            self.rawPosRecord[i] = self.rawPosRecord[i - 1]
        self.rawPosRecord[0] = Pos
        self.__smoothMove()

    def getPos(self):
        return self.rawPosRecord.sum(axis=0) / self.smooth

    def __smoothMove(self):
        parameter = 0.8
        val = 0
        center = self.getPos()
        for i in range(0, self.smooth):
            val += tools.getVectorLength(self.rawPosRecord[i] -
                                         center) * parameter**i

        val = val * (1 - parameter) + parameter**self.smooth
        # make the weight sum above always equal 1
        # provement:
        # define S = weight sum above
        # x = parameter
        # n = self.smooth
        # S-x*S = x^0 - x^n
        # S(1-x) + x^n = x^0 = 1

        val *= 50
        val -= 0.1
        val = min(1, max(0, val))
        print("val:", val)
        # bigger the val is, more rapid the change of hand position output is
        # but the output is less stable meanwhile

        for i in range(1, self.smooth):
            self.rawPosRecord[i] = self.rawPosRecord[
                0] * val + self.rawPosRecord[i] * (1 - val)
