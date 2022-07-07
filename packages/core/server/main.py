from threading import Thread
import eventlet
import socketio
from packages.core.utils import Logger

sio = socketio.Server(cors_allowed_origins=["http://localhost:3000"])
app = socketio.WSGIApp(sio)
logger = Logger(origin="server")


@sio.event
def register_as_pyra_ui(sid):
    logger.info("pyra-ui client connected")
    sio.enter_room(sid, "pyra-ui")
    # TODO: Emit initial config
    # TODO: Emit initial logs
    # TODO: Emit initial state


# When the server receives a "new_log_line"/"new_core_state" event, it broadcasts
# the event back to all connected clients that registered as pyra-ui clients.


@sio.event
def new_log_lines(sid, data):
    sio.emit("new_log_lines", data, room="pyra-ui")


@sio.event
def new_core_state(sid, data):
    sio.emit("new_core_state", data, room="pyra-ui")


@sio.event
def disconnect(sid):
    logger.info(f"pyra-ui client disconnected, rooms = {sio.rooms(sid)}")
    sio.leave_room(sid, "pyra-ui")


class Server_Thread:
    @staticmethod
    def start():
        logger.info("Starting thread")
        thread = Thread(target=Server_Thread.main)
        thread.start()

    @staticmethod
    def main():
        eventlet.wsgi.server(eventlet.listen(("", 5001)), app)
