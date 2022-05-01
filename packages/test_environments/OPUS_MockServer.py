import win32ui
from pywin.mfc import object
import dde


class MyRequestTopic(object.Object):
    def __init__(self, topicName):
        topic = dde.CreateTopic(topicName)
        topic.AddItem(dde.CreateStringItem(""))
        object.Object.__init__(self, topic)

    def Request(self, aString):
        print("Received request:", aString)
        return "OK" + " " + aString

server = dde.CreateServer()
server.AddTopic(MyRequestTopic("OPUS/System"))
server.Create("OPUS")

while 1:
    win32ui.PumpWaitingMessages(0, -1)