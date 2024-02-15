import cv2
import mediapipe as mp
import numpy
import copy

import fps
import gesture
import mouseControl
import smoothHand
import tools

mouseControl = mouseControl.control()
handSmoother = smoothHand.smoothHand(smooth=30)
MAXFPS = 60
CAM_NUM = 0


mouseControlScale = int(2.5 * mouseControl.screenSize.sum() / 2)

cap = cv2.VideoCapture(CAM_NUM)

if cap is None or not cap.isOpened(): 
    raise Exception('Unable to access camera, please check README.md for more info')

mpHands = mp.solutions.hands
handsModel = mpHands.Hands(model_complexity=1,
                           max_num_hands=1,
                           min_detection_confidence=0.95,
                           min_tracking_confidence=0.01)
mpDraw = mp.solutions.drawing_utils

FPS = fps.fps()
actionStatus = {
    "leftMouseHold": False,
    "rightClickHold": False,
    "doubleClicked": False
}
lastSmoothHandPos = None

fistExitCount = 0
lastMouseStatus = 0

handControlActivated = False


def mouseExit(actionStatus=actionStatus):
    if (actionStatus["leftMouseHold"]):
        mouseControl.mouseUp(button="left")
        actionStatus["leftMouseHold"] = False
    if (actionStatus["rightClickHold"]):
        mouseControl.mouseUp(button="right")
        actionStatus["rightClickHold"] = False

    # if (curGesture[4]):
    #     mouseControl.keyUp(button="ctrl")


while True:
    ret, img = cap.read()

    if (ret):
        imgHigh = img.shape[0]
        imgWidth = img.shape[1]
        imgSize = (imgHigh + imgWidth) / 2

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = handsModel.process(imgRGB)

        curFps = FPS.get(limitFps=MAXFPS)
        avgFps = FPS.avgFps()
        # print(round(avgFps))

        if (result.multi_hand_landmarks):

            mainLandmark = result.multi_hand_landmarks[0]
            gestureLandMark = numpy.zeros((21, 3))

            for i in range(21):
                gestureLandMark[i][0] = mainLandmark.landmark[i].x
                gestureLandMark[i][1] = mainLandmark.landmark[i].y
                gestureLandMark[i][2] = mainLandmark.landmark[i].z

                gestureLandMark[i][0] *= imgWidth / imgSize
                gestureLandMark[i][1] *= imgHigh / imgSize

            curGesture = gesture.analize(gestureLandMark)
            curGestureName = gesture.gesturesName(curGesture)

            # print(curGesture)
            # print(curGestureName)

            handX = mainLandmark.landmark[9].x
            handY = mainLandmark.landmark[9].y
            handX *= imgWidth / imgSize
            handY *= imgHigh / imgSize

            rawHandPos = numpy.array((1 - handX, handY))
            if (handControlActivated or curGesture[0] == 1):
                handControlActivated = True
                if (curGestureName == "fist"):
                    fistExitCount += 1
                    if (fistExitCount >= 5):
                        handControlActivated = False
                        mouseExit(actionStatus=actionStatus)
                else:
                    fistExitCount = 0

                    if (curGesture[0] == 1 or curGesture[3] == 1):
                        handSmoother.pushPos(rawHandPos)
                        smoothHandPos = handSmoother.getPos()
                        if (type(lastSmoothHandPos) != type(None)):
                            deltaHandPosition = smoothHandPos - lastSmoothHandPos
                            deltaMousePos = deltaHandPosition * mouseControlScale
                            deltaMousePos *= curFps / avgFps
                            # slow mode
                            if (curGesture[4] == 1):
                                deltaMousePos *= 0.1
                            # moving or scrolling
                            if (curGesture[3] == 1):
                                mouseControl.scroll(deltaMousePos[1])
                            else:
                                mouseControl.addDis(deltaMousePos)
                        else:
                            handSmoother.setPos(rawHandPos)
                            smoothHandPos = handSmoother.getPos()

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
                                and not actionStatus["doubleClicked"]):
                            # print("rightClick")
                            mouseControl.mouseDown(button="right")
                            actionStatus["rightClickHold"] = True
                    else:
                        if (actionStatus["rightClickHold"]):
                            mouseControl.mouseUp(button="right")
                            actionStatus["rightClickHold"] = False

            else:
                lastSmoothHandPos = None
                
            for handLms in result.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                # for i, lm in enumerate(handLms.landmark):
                #     print(i, lm.x, lm.y)

            for i in range(21):
                x = mainLandmark.landmark[i].x * imgWidth
                y = mainLandmark.landmark[i].y * imgHigh
                z = mainLandmark.landmark[i].z
                x = int(x)
                y = int(y)
                cv2.putText(img, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                            1 - z * 10, (255, 0, 0), 2)

        else:
            handControlActivated = False
            mouseExit(actionStatus=actionStatus)

        cv2.putText(img, "fps: " + str(int(curFps)), (0, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

        cv2.imshow("img", img)

    cv2KeyEvent = cv2.waitKey(1)
    if (cv2KeyEvent == ord('q')):
        break

    if (cv2KeyEvent == 27):
        break

cap.release()
