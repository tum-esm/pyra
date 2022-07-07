import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio)


@sio.event
def register_as_pyra_ui(sid):
    sio.enter_room(sid, "pyra-ui")
    # TODO: Emit initial config
    # TODO: Emit initial logs
    # TODO: Emit initial state


# When the server receives a "new_log_line"/"new_core_state" event, it broadcasts
# the event back to all connected clients that registered as pyra-ui clients.


@sio.event
def new_log_line(sid, data):
    sio.emit("new_log_line", data, room="pyra-ui")


@sio.event
def new_core_state(sid, data):
    sio.emit("new_core_state", data, room="pyra-ui")


@sio.event
def disconnect(sid):
    sio.leave_room(sid, "pyra-ui")


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("", 5000)), app)
