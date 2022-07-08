import os
from threading import Thread
from flask_cors import CORS
import socketio
from flask import Flask


dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(dir(os.path.abspath(__file__)))))

sio = socketio.Server(async_mode="threading", cors_allowed_origins="*")
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

CORS(app)

# When the server receives a "new_log_line"/"new_core_state" event, it broadcasts
# the event back to all connected clients that registered as pyra-ui clients.


@sio.event
def new_log_lines(sid, data):
    sio.emit("new_log_lines", data, broadcast=True)


@sio.event
def new_core_state(sid, data):
    sio.emit("new_core_state", data, broadcast=True)


if __name__ == "__main__":
    app.run()
