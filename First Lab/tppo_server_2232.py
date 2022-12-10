import json
import socket
import argparse
import os
import sys
import threading
import time
import signal
import fcntl
from threading import Thread, Lock

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from Device import Conditioner

flag = True


class Server(FileSystemEventHandler):
    def __init__(self, _addr, _port):
        self.addr = _addr
        self.port = int(_port)
        self.sock_fd = 0
        self.BUFFSIZE = 1024
        self.me = False
        self.subscriptions = set()
        self.conditioner = Conditioner()
        self.conditioner.start_condition()
        self.target_thread = 0
        self.setup_socket()
        self.mutex = threading.Lock()

        # signal.signal(signal.SIGIO, self.handler)
        # fd = os.open(self.conditioner.folder_path, os.O_RDONLY)
        # fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
        # fcntl.fcntl(fd, fcntl.F_NOTIFY,
        #             fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)

    def on_modified(self, event):
        if event.is_directory == True:
            self.mutex.acquire()
            print(f"Exec get_params from handler at {self} with {event}")
            regime, target_temp, _ = self.conditioner.get_params()
            self.mutex.release()
            msg = {
                "comment": f"Conditioner parameters has been changed\n"
                           f"Regime: {regime}, Target Temperature: {target_temp}"
            }
            js_msg = json.dumps(msg)
            for subscriber in self.subscriptions:
                self.sock_fd.sendto(js_msg.encode(), subscriber)

    def run(self):
        while True:
            msg, addr = self.sock_fd.recvfrom(self.BUFFSIZE)
            msg_thread = Thread(target=self.receiver, args=(msg, addr), daemon=True)
            msg_thread.start()

    def receiver(self, msg, addr):
        global flag
        self.check_addr(addr)
        msg = msg.decode("utf-8")
        js_msg = json.loads(msg)
        repl = ""
        if js_msg["command"] == "CONNECT":
            repl = {
                "comment": f"You have been connected to the server at {self.addr}:{self.port}"
            }
        if js_msg["command"] == "CHECK":
            repl = {
                "comment": "Pong!"
            }
        if js_msg["command"] == "GET":
            repl = {
                "comment": f"regime is: {self.conditioner.regime}\n"
                           f"target_temp is {self.conditioner.target_temp}\n"
                           f"current_temp is {self.conditioner.real_temp}"
            }
        if js_msg["command"] == "SET":
            regime = js_msg["parameters"]["regime"]
            target_temp = js_msg["parameters"]["target_temp"]
            self.mutex.acquire()
            self.conditioner.set_params(int(regime), int(target_temp))
            self.mutex.release()
            repl = None
        if js_msg["command"] == "CLOSE":
            self.subscriptions.remove(addr)
            repl = None
        if repl is None:
            pass
        else:
            js_repl = json.dumps(repl)
            self.sock_fd.sendto(js_repl.encode(), addr)

    def check_addr(self, addr):
        if addr in self.subscriptions:
            pass
        else:
            self.subscriptions.add(addr)

    def setup_socket(self):
        self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_fd.bind((self.addr, self.port))

    def handler(self, signum, frame):
        self.mutex.acquire()
        regime, target_temp, _ = self.conditioner.get_params()
        self.mutex.release()
        msg = {
            "comment": f"Conditioner parameters has been changed\n"
                       f"Regime: {regime}, Target Temperature: {target_temp}"
        }
        js_msg = json.dumps(msg)
        for subscriber in self.subscriptions:
            self.sock_fd.sendto(js_msg.encode(), subscriber)


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

    server = Server(server_addr, server_port)
    observer = Observer()
    observer.schedule(server, server.conditioner.file_path, recursive=True)
    observer.start()

    server.run()
