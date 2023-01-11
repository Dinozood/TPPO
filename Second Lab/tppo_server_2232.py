import argparse
from flask import Flask, request, abort
import flask_socketio
import logging

from First_tppo_server_2232 import Server, Observer, json

app = Flask(__name__)
socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False,
                                   async_handlers=True)
logging.getLogger('werkzeug').disabled = True

server = 0


class ServerREST(Server):

    def __init__(self, _addr, _port):
        super().__init__(_addr, _port)

    def setup_socket(self):
        pass

    def run(self):
        global socketio
        socketio.run(app, host=self.addr, port=self.port, debug=False, allow_unsafe_werkzeug=True, log_output=False)

    def on_modified(self, event):
        global socketio
        if event.is_directory:
            self.mutex.acquire()
            print(f"Exec get_params from handler at {self} with {event}")
            regime, target_temp, _ = self.conditioner.get_params()
            self.mutex.release()
            msg = {
                "comment": f"Conditioner parameters has been changed\n"
                           f"Regime: {regime}, Target Temperature: {target_temp}"
            }
            socketio.emit("Alarm", msg, broadcast=True)


@socketio.on("disconnect")
def disconnect():
    global server
    print("Client disconnected")


@socketio.on('connect')
def connection(auth):
    global server
    print("A client has connected!")


@app.route("/device/whole_info")
def get_info():
    global server
    repl = {
        "regime": server.conditioner.regime,
        "target_temp": server.conditioner.target_temp,
        "real_temp": server.conditioner.real_temp
    }

    return repl


@app.route("/device/<string:type>")
def get_specific_info(type):
    if type not in ["regime", "target_temp"]:
        abort(404)
    repl = get_info()
    return {type: repl[type]}


@app.route("/device/check")
def ping_pong():
    return {"comment": "pong"}


@app.route("/device")
def set_params():
    global server
    regime = request.args.get("regime")
    target_temp = request.args.get("target_temp")
    repl = ""
    server.mutex.acquire()
    if regime and target_temp:
        if server.conditioner.set_params(_speed=int(regime), _target_temp=int(target_temp)):
            repl = {
                "comment": f"Wrong params, please use 0 => regime => 10 and 15 => target_temp => 35"
            }
        else:
            repl = {
                "regime": server.conditioner.regime,
                "target_temp": server.conditioner.target_temp
            }
    elif regime:
        if server.conditioner.set_params(_speed=int(regime)):
            repl = {
                "comment": f"Wrong params, please use 0 => regime => 10"
            }
        else:
            repl = {
                "regime": server.conditioner.regime
            }
    elif target_temp:
        if server.conditioner.set_params(_target_temp=int(target_temp)):
            repl = {
                "comment": f"Wrong params, please use 15 => target_temp => 35"
            }
        else:
            repl = {
                "target_temp": server.conditioner.target_temp
            }
    else:
        abort(404)
    server.mutex.release()
    return repl


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Service server",
                                     description="That program is a Server for service which watching device statement "
                                                 "and realising communication between device and user...",
                                     epilog="For more information contact with multiplydino@gmail.com"
                                     )

    parser.add_argument("-A", "--address", default="127.0.0.1", help="Server ip address param")
    parser.add_argument("-P", "--port", default="1337", help="Server port param")
    args = parser.parse_args()
    server_addr = args.address
    server_port = args.port

    server = ServerREST(server_addr, server_port)
    observer = Observer()
    observer.schedule(server, server.conditioner.file_path, recursive=True)
    observer.start()

    server.run()
