from mycroft import MycroftSkill, intent_file_handler


class FaceDetection(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('detection.face.intent')
    def handle_detection_face(self, message):
        self.speak_dialog('detection.face')


def create_skill():
    return FaceDetection()

