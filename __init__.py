from mycroft import MycroftSkill, intent_file_handler
import cv2
import numpy as np

class FaceDetection(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('detection.face.intent')
    def handle_detection_face(self, message):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('/home/craghack/Documents/camera/trainer.yml')
        faceCascade = cv2.CascadeClassifier("/home/craghack/Documents/camera/haarcascade_frontalface_default.xml")
        font = cv2.FONT_HERSHEY_SIMPLEX

        names = ['unknown']
        ids =  open("/home/craghack/Documents/camera/ids.txt", "r")
        for line in ids:
            names.append(line.split(' ')[2].rstrip())
        ids.close()

        # Initialize and start realtime video capture
        cam = cv2.VideoCapture(0)
        cam.set(3, 640) # set video widht
        cam.set(4, 480) # set video height

        minW = 0.1*cam.get(3)
        minH = 0.1*cam.get(4)
        self.speak_dialog('detection.face')

        confident = False
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
                    confident = True
                    self.speak_dialog('seen.face')
                    confidence = "  {0}%".format(round(confidence))
                elif (confidence > 35):
                    confident = True
                    self.speak_dialog('identified.face')
                    confidence = "  {0}%".format(round(confidence))

#                if (confidence > 50):
#                    confident = True
#                    id = names[id-1]
#                    if id == "unknown":
#                        self.speak_dialog('seen.face')
#                    else:
#                        self.speak_dialog('identified.face')
#                    confidence = "  {0}%".format(round(confidence))

                # If confidence is less then 50 ==> "0" : perfect match
#                if (confidence > 50):
#                    self.speak_dialog('identified.face')
#                    id = names[id]
#                    confidence = "  {0}%".format(round(confidence))
#                else:
#                    self.speak_dialog('seen.face')
#                    id = names[0]
#                    confidence = "  {0}%".format(round(confidence))
                
                    break
            if(len(faces)):
                cv2.putText(frame, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
                cv2.putText(frame, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)
                cv2.imwrite("capture.jpg", frame)
        cam.release()


def create_skill():
    return FaceDetection()

