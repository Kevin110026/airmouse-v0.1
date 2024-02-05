import time


class fps:

    def __init__(self):
        self.lastTime = time.time()

    def get(self):
        curTime = time.time()
        try:
            ans = 1 / (curTime - self.lastTime)
        except:
            ans = float('inf')
        self.lastTime = curTime
        return ans
