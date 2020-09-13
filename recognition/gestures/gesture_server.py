import cv2
from src.hand_tracker import HandTracker
import math
import zoom_bridge_functions
from Globals import global_vars
import pywinauto
import time



WINDOW = "Hand Tracking"
PALM_MODEL_PATH = "../recognition/gestures/palm_detection_without_custom_op.tflite"
LANDMARK_MODEL_PATH = "../recognition/gestures/hand_landmark.tflite"
ANCHORS_PATH = "../recognition/gestures/anchors.csv"

POINT_COLOR = (0, 255, 0)
CONNECTION_COLOR = (255, 0, 0)
THICKNESS = 2


def gesture_function():
    cv2.namedWindow(WINDOW)
    capture = cv2.VideoCapture(1)

    if capture.isOpened():
        hasFrame, frame = capture.read()
    else:
        hasFrame = False

    #        8   12  16  20
    #        |   |   |   |
    #        7   11  15  19
    #    4   |   |   |   |
    #    |   6   10  14  18
    #    3   |   |   |   |
    #    |   5---9---13--17
    #    2    \         /
    #     \    \       /
    #      1    \     /
    #       \    \   /
    #        ------0-
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (5, 6), (6, 7), (7, 8),
        (9, 10), (10, 11), (11, 12),
        (13, 14), (14, 15), (15, 16),
        (17, 18), (18, 19), (19, 20),
        (0, 5), (5, 9), (9, 13), (13, 17), (0, 17)
    ]

    detector = HandTracker(
        PALM_MODEL_PATH,
        LANDMARK_MODEL_PATH,
        ANCHORS_PATH,
        box_shift=0.2,
        box_enlarge=1.3
    )

    def get_euclidean_distance(ax, ay, bx, by):
        dist = ((ax - bx) ** 2) + ((ay - by) ** 2)
        return math.sqrt(dist)

    def isThumbNearFirstFinger(p1, p2):
        distance = get_euclidean_distance(p1[0], p1[1], p2[0], p2[1])
        return distance < 0.1

    gesture = [0 for i in range(9)]
    global_vars.acquire()
    while hasFrame and global_vars.do_react:
        global_vars.release()

        thumbIsOpen = False
        firstFingerIsOpen = False
        secondFingerIsOpen = False
        thirdFingerIsOpen = False
        fourthFingerIsOpen = False

        k = 0

        landmarkList = [(0, 0)] * 21

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        points, _ = detector(image)
        if points is not None:
            for point in points:
                x, y = point
                landmarkList[k] = (x, y)
                k = k + 1
                cv2.circle(frame, (int(x), int(y)), THICKNESS * 2, POINT_COLOR, THICKNESS)
            for connection in connections:
                x0, y0 = points[connection[0]]
                x1, y1 = points[connection[1]]
                cv2.line(frame, (int(x0), int(y0)), (int(x1), int(y1)), CONNECTION_COLOR, THICKNESS)

            j = landmarkList[2][0]
            if landmarkList[3][0] < j and landmarkList[4][0] < j:
                thumbIsOpen = True

            j = landmarkList[6][1]
            if landmarkList[7][1] < j and landmarkList[8][1] < j:
                firstFingerIsOpen = True

            j = landmarkList[10][1]
            if landmarkList[11][1] < j and landmarkList[12][1] < j:
                secondFingerIsOpen = True

            j = landmarkList[14][1]
            if landmarkList[15][1] < j and landmarkList[16][1] < j:
                thirdFingerIsOpen = True

            j = landmarkList[18][1]
            if landmarkList[19][1] < j and landmarkList[20][1] < j:
                fourthFingerIsOpen = True


            if thumbIsOpen and firstFingerIsOpen and secondFingerIsOpen and thirdFingerIsOpen and fourthFingerIsOpen:
                gesture[5] += 1  # "FIVE"
            elif not thumbIsOpen and firstFingerIsOpen and secondFingerIsOpen and thirdFingerIsOpen and fourthFingerIsOpen:
                gesture[4] += 1  # "FOUR"
            elif thumbIsOpen and firstFingerIsOpen and secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
                gesture[3] += 1  # "THREE"
            elif thumbIsOpen and firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
                gesture[2] += 1  # "TWO"
            elif not thumbIsOpen and firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
                gesture[1] += 1  # "ONE"
            elif not thumbIsOpen and firstFingerIsOpen and secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
                gesture[0] += 1  # "YEAH"
            elif not thumbIsOpen and firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and fourthFingerIsOpen:
                gesture[6] += 1  # "ROCK"
            elif thumbIsOpen and firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and fourthFingerIsOpen:
                gesture[7] += 1  # "SPIDERMAN"
            elif not thumbIsOpen and not firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
                gesture[8] += 1  # "FIST"

            print(gesture)

            if any([i >= 3 for i in gesture]):
                cur_gesture = gesture.index(3)
                print("Detected gesture: ", cur_gesture)
                global_vars.acquire()
                # print("inside lock from gesture!")
                cur_action = global_vars.gesture_assignments[cur_gesture]
                if cur_action != 7:
                    try:
                        # print(global_vars.gesture_assignments)
                        zoom_bridge_functions.zoom_function_wrap(cur_action)
                    except (pywinauto.findwindows.ElementNotFoundError, pywinauto.findbestmatch.MatchError, AttributeError, RuntimeError) as e:
                        print(e.args)
                else:
                    global_vars.do_live_transcribe = not global_vars.do_live_transcribe

                global_vars.release()
                # print("outside lock from gesture!")
                gesture = [0 for i in range(9)]

        # cv2.imshow(WINDOW, frame)
        hasFrame, frame = capture.read()
        key = cv2.waitKey(1)
        if key == 27:
            break
        time.sleep(0.01)
        global_vars.acquire()

    capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    gesture_function()