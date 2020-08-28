from mycroft import MycroftSkill, intent_file_handler
import cv2
import numpy as np

from pymouse import PyMouse
from pynput.keyboard import Key, Controller
import os
import subprocess
from time import sleep

class FaceDetection(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('detection.face.intent')
    def handle_detection_face(self, message):
        keyboard = Controller()
        m = PyMouse()
        right = Key.right
        left = Key.left

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('/home/craghack/Documents/camera/trainer.yml')
        faceCascade = cv2.CascadeClassifier("/home/craghack/Documents/camera/haarcascade_frontalface_default.xml")
        #font = cv2.FONT_HERSHEY_SIMPLEX

        names = ['unknown']
        ids =  open("/home/craghack/Documents/camera/ids.txt", "r")
        for line in ids:
            names.append(line.split(' ')[2].rstrip())
        ids.close()

        # Initialize and start realtime video capture
        cam = cv2.VideoCapture(0)
        #cam.set(3, 640) # set video widht
        #cam.set(4, 480) # set video height

        minW = 0.1*cam.get(3)
        minH = 0.1*cam.get(4)

        emoji = None
        cmd = subprocess.check_output("wmctrl -l | grep \".png\" | cut -b 23-", shell=True).decode("utf-8").rstrip()
        if not cmd == "":
            emoji = cmd.split('.')[0]
            os.system("wmctrl -a \"" + cmd + "\"")
        else:
            emoji = "suspicious"
            os.system("xdg-open /home/craghack/Downloads/emojis/suspicious.png && sleep 1")
        sleep(.25)
        m.click(350, 460)
        sleep(.25)
        m.move(799,479)
        if emoji == "happy":
            keyboard.press(left)
            keyboard.release(left)
            emoji = "suspicious"
        elif emoji == "suprised":
            keyboard.press(right)
            keyboard.release(right)
            emoji = "suspicious"

        self.speak_dialog('detection.face')

        confident = False
        count = 0
        recognized = []
        while not confident:
            rval, frame = cam.read()
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.2, 
                minNeighbors = 5, minSize = (int(minW), int(minH)))

            for(x,y,w,h) in faces:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                confidence = 100 - confidence # Confidence starts backwards for some reason

                id = names[id-1]
                if (id == "unknown") and (confidence > 50):
#                    confident = True
                    if emoji == "suspicious":
                        keyboard.press(left)
                        keyboard.release(left)
                        sleep(.75)
                        keyboard.press(right)
                        keyboard.release(right)
                    elif emoji == "happy":
                        keyboard.press(right)
                        keyboard.release(right)
                        sleep(.75)
                        keyboard.press(right)
                        keyboard.release(right)
                    recognized.append("unknown")
                    self.speak_dialog('seen.face')
                elif (confidence > 35):
#                    confident = True
                    if id not in recognized:
                        if emoji == "suspicious":
                            keyboard.press(right)
                            keyboard.release(right)
                            emoji = "happy"
                        elif emoji == "happy":
                            keyboard.press(right)
                            keyboard.release(right)
                            sleep(.75)
                            keyboard.press(left)
                            keyboard.release(left)
                        recognized.append(id)
                        dialog = id + '.face'
                        self.speak_dialog(dialog)

            if len(recognized) != 0 and len(recognized) >= len(faces):
                count += 1
                if (count >= 50):
                    confident = True
            else:
                count = 0

        cam.release()
#        keyboard.press(Key.esc)
#        keyboard.release(Key.esc)
#        os.system("wmctrl -a start-mycroft.sh debug")


def create_skill():
    return FaceDetection()

