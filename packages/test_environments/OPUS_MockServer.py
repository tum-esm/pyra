import win32ui
import pywin
import dde


class MyRequestTopic(pywin.mfc.object.Object):
    def __init__(self, topicName):
        topic = dde.CreateTopic(topicName)
        topic.AddItem(dde.CreateStringItem(""))
        pywin.mfc.object.Object.__init__(self, topic)

    def Request(self, aString):
        print("Received request:", aString)
        return "OK" + " " + aString


server = dde.CreateServer()
server.AddTopic(MyRequestTopic("OPUS/System"))
server.Create("OPUS")

while 1:
    win32ui.PumpWaitingMessages(0, -1)
