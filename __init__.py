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

    @intent_file_handler('watch.intent')
    def handle_watch(self, message, r_name='i', remind=False):
        self.speak_dialog('starting')
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
            names.append(line.lower().split(' ')[2].rstrip())
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
            os.system("xdg-open /home/craghack/Downloads/emojis/suspicious.png")
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

        self.speak_dialog('watching')

        confident = False
        try:
            count = 0
            recognized = []
            while not confident:
                rval, frame = cam.read()
                gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

                faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.2, 
                    minNeighbors = 5, minSize = (int(minW), int(minH)))

                for(x,y,w,h) in faces:
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                    ID, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                    confidence = 100 - confidence # Confidence starts backwards for some reason

                    name = names[ID-1]
                    if (name == "unknown") and (confidence > 50):
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
                            emoji = "suspicious"
                        recognized.append("unknown")
                        self.speak_dialog('unknown')
                    elif (confidence > 15):
    #                    confident = True
                        if name not in recognized:
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
                            recognized.append(name)
                            #dialog = id + '.face'
                            response = {'name': name}
                            self.speak_dialog('recognized', data=response)

                if not r_name == 'i':
                    if r_name in recognized:
                        confident = True
                    else:
                        if emoji == "happy":
                            sleep(.5)
                            keyboard.press(left)
                            keyboard.release(left)
                            emoji = "suspicious"
                elif len(recognized) != 0 and len(recognized) >= len(faces):
                    count += 1
                    if (count >= 50):
                        confident = True
                else:
                    count = 0

            cam.release()
        except Exception as e:
            print(e)
            keyboard.press(Key.esc)
            keyboard.release(Key.esc)
            os.system("wmctrl -a \"start-mycroft.sh debug\"")
            os.system("wmctrl -a \"craghack@Cyclops: ~/mycroft-core\"")
        if not remind:
            sleep(1)
            keyboard.press(Key.esc)
            keyboard.release(Key.esc)
            os.system("wmctrl -a \"start-mycroft.sh debug\"")
            os.system("wmctrl -a \"craghack@Cyclops: ~/mycroft-core\"")
        return confident

    @intent_file_handler('wigh.intent')
    def handle_wigh(self, message):
        keyboard = Controller()
        name = message.data['name']
        reminder = message.data['reminder']
        reminder = (' ' + reminder).replace(' my ', ' your ').strip()
        reminder = (' ' + reminder).replace(' our ', ' your ').strip()
        if not name.lower() == 'i':
            reminder = (' ' + reminder).replace(' her ', ' your ').strip()
            reminder = (' ' + reminder).replace(' his ', ' your ').strip()
#        self.settings['wigh_reminders'] = []
#        return
        if 'wigh_reminders' in self.settings and not self.settings['wigh_reminders'] == []:
            self.settings['wigh_reminders'].append(reminder)
            if len(self.settings['wigh_reminders']) > 1:
                self.speak_dialog('watching')
                return
        else:
            self.settings['wigh_reminders'] = [reminder]
        try:
            if self.handle_watch(message, name, True):
                reminders = ""
                for reminder in self.settings['wigh_reminders']:
                    reminders += reminder + ", and "
                self.settings['wigh_reminders'] = []
                response = {'reminder': reminders[:-6]}
                self.speak_dialog('remind', data=response)
                sleep(4)
                keyboard.press(Key.esc)
                keyboard.release(Key.esc)
                os.system("wmctrl -a \"start-mycroft.sh debug\"")
                os.system("wmctrl -a \"craghack@Cyclops: ~/mycroft-core\"")
        except Exception as e:
            self.settings['wigh_reminders'] = []
            print(e)
            keyboard.press(Key.esc)
            keyboard.release(Key.esc)
            os.system("wmctrl -a \"start-mycroft.sh debug\"")
            os.system("wmctrl -a \"craghack@Cyclops: ~/mycroft-core\"")

def create_skill():
    return FaceDetection()

