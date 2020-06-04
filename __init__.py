from mycroft import MycroftSkill, intent_file_handler
import cv2

class FaceDetection(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('detection.face.intent')
    def handle_detection_face(self, message):
        # Load the cascade
        face_cascade = cv2.CascadeClassifier('/home/gillion/Documents/camera/haarcascade_frontalface_default.xml')
        # Read the input
        cam = cv2.VideoCapture(0)
        self.speak_dialog('detection.face')
        while True:
            # Capture frame-by-frame
            ret, frame = cam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.2, 4)
#            for (x, y, w, h) in faces:
#                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            if len(faces):
                self.speak_dialog('seen.face')
#                cv2.imwrite("seen.png", frame)
                break
        cam.release()

def create_skill():
    return FaceDetection()

