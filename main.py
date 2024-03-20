import tools
import smoothHand
import mouseControl
import gesture
import fps
import copy
import numpy
import mediapipe as mp
import cv2
import time

runTimeRecorder = time.perf_counter()
print("loading dictionary")


mouseControl = mouseControl.control()
handPosSmoother = smoothHand.smoothHand(smooth=30)
handSizeSmoother = smoothHand.smoothHand(smooth=30)
MAX_FPS = 60
CAM_NUM = 0
MAX_HANDS_AMOUNT = 10

mouseControlScale = int(2.5 * mouseControl.screenSize.sum() / 2)
mouseSensitiveScale = 0.2

time.perf_counter()
print("took " + str(time.perf_counter() - runTimeRecorder) + " sec")
runTimeRecorder = time.perf_counter()
print("loading camera")

cap = cv2.VideoCapture(CAM_NUM)

if cap is None or not cap.isOpened():
    raise Exception(
        'Unable to access camera, please check README.md for more info')

print("took " + str(time.perf_counter() - runTimeRecorder) + " sec")
runTimeRecorder = time.perf_counter()
print("loading model")

mpHands = mp.solutions.hands
multiHandModel = mpHands.Hands(model_complexity=1,
                               max_num_hands=MAX_HANDS_AMOUNT,
                               min_detection_confidence=0.95,
                               min_tracking_confidence=0.05)
singleHandModel = mpHands.Hands(model_complexity=1,
                                max_num_hands=1,
                                min_detection_confidence=0.30,
                                min_tracking_confidence=0.05)

mpDraw = mp.solutions.drawing_utils

print("took " + str(time.perf_counter() - runTimeRecorder) + " sec")
runTimeRecorder = time.perf_counter()

FPS = fps.fps()
actionStatus = {
    "leftMouseHold": False,
    "rightClickHold": False,
    "doubleClicked": False,
    "ctrlZooming": False,
    "adjustingMouseSensitive": False,
}
lastSmoothHandPos = None

# handControlActivationCount = 0
handControlActivationCount = numpy.zeros((MAX_HANDS_AMOUNT))
handControlActivated = False
handControlState = "None"
handControlMatchingTarget = None

fistExitCount = 0
lastMouseStatus = 0


def mpLandmarks2ndarray(landmarks, correctScale=True, imgWidth=None, imgHigh=None):
    result = numpy.zeros((21, 3))

    if(correctScale and not (imgHigh and imgWidth)):
        raise Exception("input is not complete")
        return None

    try:
        for i in range(21):
            result[i][0] = landmarks[i].x
            result[i][1] = landmarks[i].y
            result[i][2] = landmarks[i].z
        
        if(correctScale):
            imgSize = (imgWidth+imgHigh)/2
            for i in range(21):
                result[i][0] = landmarks[i].x * imgWidth/imgSize
                result[i][1] = landmarks[i].y * imgHigh/imgSize
                result[i][2] = landmarks[i].z * imgWidth/imgSize

    except:
        pass

    return result


def handImageFilter3(img, landmarks: numpy.ndarray, mainLandmark):
    imgWidth = img.shape[1]
    imgHigh = img.shape[0]
    x1 = landmarks[mainLandmark].min(0)[0] * imgWidth
    y1 = landmarks[mainLandmark].min(0)[1] * imgHigh
    x2 = landmarks[mainLandmark].max(0)[0] * imgWidth
    y2 = landmarks[mainLandmark].max(0)[1] * imgHigh
    xc = (x1 + x2) / 2
    yc = (y1 + y2) / 2
    x1 = (x1 - xc) * 1.5 + xc
    x2 = (x2 - xc) * 1.5 + xc
    y1 = (y1 - yc) * 1.5 + yc
    y2 = (y2 - yc) * 1.5 + yc
    x1 = max(0, int(x1))
    x2 = min(imgWidth, int(x2) + 1)
    y1 = max(0, int(y1))
    y2 = min(imgHigh, int(y2) + 1)
    tmpImg = copy.deepcopy(img)
    allLandmarksCount = len(landmarks)
    for i in range(allLandmarksCount):
        if (i == mainLandmark):
            continue
        X1 = landmarks[i].min(0)[0] * imgWidth
        Y1 = landmarks[i].min(0)[1] * imgHigh
        X2 = landmarks[i].max(0)[0] * imgWidth
        Y2 = landmarks[i].max(0)[1] * imgHigh
        X1 = max(0, int(X1))
        X2 = min(imgWidth, int(X2) + 1)
        Y1 = max(0, int(Y1))
        Y2 = min(imgHigh, int(Y2) + 1)
        cv2.rectangle(img, (X1, Y1), (X2, Y2), (0, 0, 0), thickness=-1)

    img[y1:y2, x1:x2] = tmpImg[y1:y2, x1:x2]


def mouseExit(actionStatus=actionStatus):
    if (actionStatus["leftMouseHold"]):
        mouseControl.mouseUp(button="left")
        actionStatus["leftMouseHold"] = False
    if (actionStatus["rightClickHold"]):
        mouseControl.mouseUp(button="right")
        actionStatus["rightClickHold"] = False
    if (actionStatus["ctrlZooming"]):
        mouseControl.keyUp(button="ctrl")
        actionStatus["ctrlZooming"] = False

    # if (curGesture[4]):
    #     mouseControl.keyUp(button="ctrl")


class handSmoother:
    # translate landmarks into smooth hand status

    def __init__(self) -> None:
        self.landmarkSmoother = numpy.ndarray(
            (21), dtype=object)
        for i in range(21):
            self.landmarkSmoother[i] = smoothHand.smoothHand(smooth=30)



    def set(self, handLandmarks: numpy.ndarray((21, 3))) -> None:
        # set by 1:1:1 scale 3d landmarks
        for i in range(21):
            self.landmarkSmoother[i].setPos(handLandmarks[i])


    def push(self, handLandmarks: numpy.ndarray((21, 3))) -> None:
        # push in 1:1:1 scale 3d landmarks
        for i in range(21):
            self.landmarkSmoother[i].pushPos(handLandmarks[i])

    
    def get(self) -> numpy.ndarray:
        # return smooth landmarks
        result = numpy.zeros((21, 3))
        for i in range(21):
            result[i] = self.landmarkSmoother[i].getPos()
        return result



class handControl:
    # control mouse by hand status

    def __init__(self) -> None:
        self.lastMousePos = numpy.zeros((2))
        self.curMousePos = numpy.zeros((2))
        self.actionStatus = {
            "leftMouseHold": False,
            "rightClickHold": False,
            "doubleClicked": False,
            "ctrlZooming": False,
            "adjustingMouseSensitive": False,
        }

    def push(self, handLandmarks: numpy.ndarray((21, 3))) -> None:
        # push in 1:1:1 scale 3d landmarks

        self.__control

    def set(self, handLandmarks: numpy.ndarray((21, 3))) -> None:
        # set by 1:1:1 scale 3d landmarks


        self.__control

    def __control(self) -> None:

        mouseControl.addDis()

        # work here later

    def mouseExit(actionStatus=actionStatus) -> None:
        if (actionStatus["leftMouseHold"]):
            mouseControl.mouseUp(button="left")
            actionStatus["leftMouseHold"] = False
        if (actionStatus["rightClickHold"]):
            mouseControl.mouseUp(button="right")
            actionStatus["rightClickHold"] = False
        if (actionStatus["ctrlZooming"]):
            mouseControl.keyUp(button="ctrl")
            actionStatus["ctrlZooming"] = False


controlHandSmoother = handSmoother()

while True:

    curFps = FPS.get(limitFps=MAX_FPS)
    avgFps = FPS.avgFps()
    # print(round(avgFps))

    ret, img = cap.read()

    if (ret):
        # cv2.imshow("img1", img)
        imgHigh = img.shape[0]
        imgWidth = img.shape[1]
        imgSize = (imgHigh + imgWidth) / 2

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if (handControlState != "Activated"):
            # finding the hand to control

            lastSmoothHandPos = None

            # modelProcessTimeRecorder1 = time.perf_counter()
            result = multiHandModel.process(imgRGB)
            # modelProcessTimeRecorder2 = time.perf_counter()
            # modelProcessTime = modelProcessTimeRecorder2 - modelProcessTimeRecorder1
            # print("model process took",round(modelProcessTime*1000),"ms!")
            # print("=",round(1/modelProcessTime),"fps")

            try:
                allLandmarksCount = len(result.multi_hand_landmarks)
            except:
                allLandmarksCount = 0

            allLandmarks = numpy.zeros((allLandmarksCount, 21, 3))
            allLandmarksCorrected = numpy.zeros((allLandmarksCount, 21, 3))
            allGestures = numpy.zeros((allLandmarksCount, 5))

            for i in range(MAX_HANDS_AMOUNT):
                if (i < allLandmarksCount):
                    for j in range(21):
                        allLandmarks[i] = mpLandmarks2ndarray(result.multi_hand_landmarks[i].landmark, correctScale=False)
                        allLandmarksCorrected[i] = mpLandmarks2ndarray(result.multi_hand_landmarks[i].landmark, correctScale=True, imgWidth=imgWidth, imgHigh=imgHigh)

                    allGestures[i] = gesture.analize(allLandmarksCorrected[i])
                    if ((allGestures[i] == numpy.array([1, 0, 0, 0,
                                                        0])).all()):
                        handControlActivationCount[i] += 1
                        if (handControlActivationCount[i] > 10):
                            handControlActivationCount[i] = 10
                    else:
                        handControlActivationCount[i] = 0
                        if (handControlActivationCount[i] < 0):
                            handControlActivationCount[i] = 0

                else:
                    handControlActivationCount[i] = 0

            if (handControlActivationCount.max() < 5):
                handControlState = "None"
                handControlMatchingTarget = None
            else:
                for i in range(allLandmarksCount):
                    if (handControlActivationCount[i] >= 5):
                        handControlState = "Matching"
                        handControlMatchingTarget = i
                        break

            if (handControlState == "Matching"):

                imgOneHand = copy.deepcopy(img)
                handImageFilter3(imgOneHand, allLandmarks,
                                 handControlMatchingTarget)
                resultOneHand = singleHandModel.process(imgOneHand)

                cv2.imshow("Matching", imgOneHand)

                if (resultOneHand.multi_hand_landmarks):
                    handControlState = "Activated"
                    controlHand = resultOneHand.multi_hand_landmarks[0].landmark
                    controlHand = mpLandmarks2ndarray(controlHand, correctScale=True, imgWidth=imgWidth, imgHigh=imgHigh)
                    controlHandSmoother.set(controlHand)
            try:
                for handLms in result.multi_hand_landmarks:
                    mpDraw.draw_landmarks(img, handLms,
                                          mpHands.HAND_CONNECTIONS)
            except:
                pass
            cv2.putText(img, "fps: " + str(int(curFps)), (0, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
            cv2.imshow("Searching", img)

        else:
            # controlling
            
            resultOneHand = singleHandModel.process(img)

            if (resultOneHand.multi_hand_landmarks):
                mainLandmark = resultOneHand.multi_hand_landmarks[0]

                mainLandmark = numpy.zeros((21, 3))
                mainLandmarkCorrected = numpy.zeros((21, 3))

                mainLandmark = mpLandmarks2ndarray(resultOneHand.multi_hand_landmarks[0].landmark, correctScale=False)
                mainLandmarkCorrected = mpLandmarks2ndarray(resultOneHand.multi_hand_landmarks[0].landmark, correctScale=True, imgWidth=imgWidth, imgHigh=imgHigh)
                controlHandSmoother.push(mainLandmarkCorrected)
                smoothControlHand = controlHandSmoother.get()

                curGesture = gesture.analize(smoothControlHand)
                curGestureName = gesture.gesturesName(curGesture)

                # print(curGesture)
                # print(curGestureName)

                handX = mainLandmarkCorrected[9][0]
                handY = mainLandmarkCorrected[9][1]

                rawHandPos = numpy.array((1 - handX, handY))

                # print(handControlActivationCount, fistExitCount)

                if (curGestureName == "fist"):
                    fistExitCount += 1
                    if (fistExitCount >= 5):
                        lastSmoothHandPos = None
                        handControlActivated = False
                        handControlState = "None"
                        mouseExit(actionStatus=actionStatus)
                        handControlActivationCount.fill(0)
                else:
                    fistExitCount = 0

                if (handControlState == "Activated" and not fistExitCount):
                    rawHandSize = tools.getLength(smoothControlHand[5] -
                                                  smoothControlHand[17])

                    if (curGesture[0] == 1 or curGesture[3] == 1):
                        handPosSmoother.pushPos(rawHandPos)
                        handSizeSmoother.pushPos(numpy.array([rawHandSize, 0]))
                        smoothHandPos = handPosSmoother.getPos()[:2]
                        smoothHandSize = handSizeSmoother.getPos()[0]
                        if (type(lastSmoothHandPos) != type(None)):
                            deltaHandPosition = smoothHandPos - lastSmoothHandPos
                            deltaMousePos = deltaHandPosition * mouseControlScale * (
                                mouseSensitiveScale / smoothHandSize)
                            deltaMousePos *= curFps / avgFps
                            # slow mode
                            if (curGesture[4] == 1):
                                deltaMousePos *= 0.1

                            # adjusting mouse sensitive
                            if (curGesture[2] and curGesture[3]):
                                actionStatus["adjustingMouseSensitive"] = True
                                mouseSensitiveScale += -(deltaHandPosition[1] /
                                                         smoothHandSize) * 0.1
                                showingSensitive = numpy.zeros((200, 600, 3),
                                                               numpy.uint8)
                                showingSensitive.fill(255)
                                cv2.putText(showingSensitive,
                                            str(mouseSensitiveScale), (0, 50),
                                            cv2.FONT_HERSHEY_SIMPLEX, 2,
                                            (0, 0, 0), 2)
                                cv2.imshow("sensitive", showingSensitive)
                            else:
                                actionStatus["adjustingMouseSensitive"] = False
                                try:
                                    cv2.destroyWindow("sensitive")
                                except:
                                    pass

                            # zooming
                            if (curGesture[0] and curGesture[3]):
                                if (not actionStatus["ctrlZooming"]):
                                    mouseControl.keyDown(button="ctrl")
                                    actionStatus["ctrlZooming"] = True
                            else:
                                if (actionStatus["ctrlZooming"]):
                                    mouseControl.keyUp(button="ctrl")
                                    actionStatus["ctrlZooming"] = False

                            # moving or scrolling
                            if (actionStatus["adjustingMouseSensitive"]):
                                pass
                            elif (curGesture[3] == 1):
                                mouseControl.scroll(deltaMousePos[1])
                                mouseControl.hscroll(deltaMousePos[0])
                            else:
                                mouseControl.addDis(deltaMousePos)
                        else:
                            handPosSmoother.setPos(rawHandPos)
                            handSizeSmoother.setPos(
                                numpy.array([rawHandSize, 0]))
                            smoothHandPos = handPosSmoother.getPos()[0:2]
                            smoothHandSize = handSizeSmoother.getPos()[0]

                        lastSmoothHandPos = smoothHandPos
                    else:
                        lastSmoothHandPos = None

                    # left mouse click
                    if (curGesture[1]):
                        if (not actionStatus["leftMouseHold"]):
                            mouseControl.mouseDown(button="left")
                            actionStatus["leftMouseHold"] = True

                        # left mouse double click
                        if (curGesture[2]):
                            if (not actionStatus["doubleClicked"]):
                                mouseControl.mouseDoubleClick(button="left")
                                actionStatus["doubleClicked"] = True

                                # print("double clicked!")
                        else:
                            actionStatus["doubleClicked"] = False

                    else:
                        actionStatus["doubleClicked"] = False
                        if (actionStatus["leftMouseHold"]):
                            mouseControl.mouseUp(button="left")
                            actionStatus["leftMouseHold"] = False

                    # right mouse click
                    if (curGesture[2]):
                        if (not actionStatus["rightClickHold"]
                                and not actionStatus["doubleClicked"]
                                and not actionStatus["adjustingMouseSensitive"]):
                            # print("rightClick")
                            mouseControl.mouseDown(button="right")
                            actionStatus["rightClickHold"] = True
                    else:
                        if (actionStatus["rightClickHold"]):
                            mouseControl.mouseUp(button="right")
                            actionStatus["rightClickHold"] = False

                else:
                    lastSmoothHandPos = None

                for handLms in resultOneHand.multi_hand_landmarks:
                    mpDraw.draw_landmarks(img, handLms,
                                          mpHands.HAND_CONNECTIONS)

                cv2.putText(img, "fps: " + str(int(curFps)), (0, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

                cv2.imshow("Controlling", img)

            else:
                lastSmoothHandPos = None
                handControlState = "None"
                handControlActivated = False
                mouseExit(actionStatus=actionStatus)
                handControlActivationCount.fill(0)

    cv2KeyEvent = cv2.waitKey(1)
    if (cv2KeyEvent == ord('q')):
        break

    if (cv2KeyEvent == 27):
        break

cap.release()
