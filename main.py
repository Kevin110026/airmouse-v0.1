import cv2
import mediapipe as mp
import numpy

import fps
import gesture
import mouseControl
import smoothHand

mouseControl = mouseControl.control()
handSmoother = smoothHand.smoothHand(smooth=30)
MAXFPS = 60

mouseControlScale = int(2.5 * mouseControl.screenSize.sum() / 2)

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
handsModel = mpHands.Hands(model_complexity=1,
                           max_num_hands=1,
                           min_detection_confidence=0.95,
                           min_tracking_confidence=0.01)
mpDraw = mp.solutions.drawing_utils

FPS = fps.fps()
lastGesture = numpy.zeros(5)
lastSmoothHandPos = None

fistExitCount = 0
lastMouseStatus = 0

handControlActivated = False


def mouseExit(curGesture: numpy.ndarray):
    if (curGesture[1]):
        mouseControl.mouseUp(button="left")
    if (curGesture[2]):
        mouseControl.mouseUp(button="right")
    # if (curGesture[4]):
    #     mouseControl.keyUp(button="ctrl")

    for i in range(5):
        curGesture[i] = 0

    return curGesture


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
        print(round(avgFps))

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
                        mouseExit(curGesture=lastGesture)
                        break
                else:
                    fistExitCount = 0

                    if (curGesture[0] == 1 or curGesture[3] == 1):
                        handSmoother.pushPos(rawHandPos)
                        smoothHandPos = handSmoother.getPos()
                        if (type(lastSmoothHandPos) != type(None)):
                            deltaHandPosition = smoothHandPos - lastSmoothHandPos
                            deltaMousePos = deltaHandPosition * mouseControlScale
                            deltaMousePos *= curFps / avgFps
                            if (curGesture[4] == 1):
                                deltaMousePos *= 0.1
                            if (curGesture[3] == 1):
                                mouseControl.scroll(deltaMousePos[1])
                                pass
                            else:
                                mouseControl.addDis(deltaMousePos)
                        else:
                            handSmoother.setPos(rawHandPos)

                        lastSmoothHandPos = smoothHandPos
                    else:
                        lastSmoothHandPos = None

                    if (curGesture[1] != lastGesture[1]):
                        if (curGesture[1] == 1):
                            # print("leftClick")
                            mouseControl.mouseDown(button="left")
                        else:
                            mouseControl.mouseUp(button="left")

                    if (curGesture[2] != lastGesture[2]):
                        if (curGesture[2] == 1):
                            # print("rightClick")
                            mouseControl.mouseDown(button="right")
                        else:
                            mouseControl.mouseUp(button="right")

                    lastGesture = curGesture

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
            mouseExit(curGesture=lastGesture)

        cv2.putText(img, "fps: " + str(int(curFps)), (0, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

        cv2.imshow("img", img)

    cv2KeyEvent = cv2.waitKey(1)
    if (cv2KeyEvent == ord('q')):
        break

    if (cv2KeyEvent == 27):
        break

cap.release()
