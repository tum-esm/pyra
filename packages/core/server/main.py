from threading import Thread
import eventlet
from numpy import broadcast
import socketio
from packages.core.utils import Logger

sio = socketio.Server(cors_allowed_origins=["http://localhost:3000"])
app = socketio.WSGIApp(sio)
logger = Logger(origin="server")


# When the server receives a "new_log_line"/"new_core_state" event, it broadcasts
# the event back to all connected clients that registered as pyra-ui clients.


@sio.event
def new_log_lines(sid, data):
    sio.emit("new_log_lines", data, broadcast=True)


@sio.event
def new_core_state(sid, data):
    sio.emit("new_core_state", data, broadcast=True)


class Server_Thread:
    @staticmethod
    def start():
        logger.info("Starting thread")
        thread = Thread(target=Server_Thread.main)
        thread.start()

    @staticmethod
    def main():
        eventlet.wsgi.server(eventlet.listen(("", 5001)), app)
