import json
import socket
import argparse
import os
import sys
import threading
import time
import signal
import fcntl
from threading import Thread

from Device import Conditioner


class Server:
    def __init__(self, _addr, _port):
        self.addr = _addr
        self.port = int(_port)
        self.sock_fd = 0
        self.BUFFSIZE = 1024
        self.subscriptions = set()
        self.conditioner = Conditioner()
        self.conditioner.start_condition()
        self.target_thread = 0
        self.me = False
        self.setup_socket()
        signal.signal(signal.SIGIO, self.handler)
        fd = os.open(self.conditioner.folder_path, os.O_RDONLY)
        fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
        fcntl.fcntl(fd, fcntl.F_NOTIFY,
                    fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)

    def run(self):
        while True:
            msg, addr = self.sock_fd.recvfrom(self.BUFFSIZE)
            msg_thread = Thread(target=self.receiver, args=(msg, addr), daemon=True)
            msg_thread.start()

    def handler(self, signum, frame):
        if not self.me:
            print(f'File {self.file_path} modified')
        self.me = False

    def receiver(self, msg, addr):
        self.check_addr(addr)
        msg = msg.decode("utf-8")
        js_msg = json.loads(msg)
        repl = ""
        if js_msg["command"] == "CONNECT":
            repl = {
                "status": "OK"
            }
        if js_msg["command"] == "CHECK":
            repl = {
                "status": "OK"
            }
        if js_msg["command"] == "GET":
            conditioner_data = self.conditioner.get_params()
            repl = {
                "regime": conditioner_data[0],
                "target_temp": conditioner_data[1],
                "current_temp": conditioner_data[2]
            }
        if js_msg["command"] == "SET":
            regime = js_msg["parameters"]["regime"]
            target_temp = js_msg["parameters"]["target_temp"]
            self.me = True
            self.conditioner.set_params(regime, target_temp)
            repl = {
                "status": "OK"
            }
        if js_msg["command"] == "CLOSE":
            self.subscriptions.remove(addr)
            repl = {
                "status": "OK"
            }
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

    server.run()
