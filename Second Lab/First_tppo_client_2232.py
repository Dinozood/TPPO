import json
import socket
import warnings
from threading import Thread, Lock
import argparse


class ArgumentException(Exception):
    pass


class CreationSocketException(Exception):
    pass


class Client():
    def __init__(self, _server_addr, _server_port):
        self.receiver_thread = None
        self.sock_fd = 0
        self.server_addr = _server_addr
        self.server_port = _server_port
        self.server_addr_port = (self.server_addr, int(self.server_port))
        self.IO_mutex = Lock()
        self.BUFFERSIZE = 4096

    def __del__(self):
        cmd = {
            "command": "CLOSE"
        }
        js_cmd = json.loads(cmd)
        self.sock_fd.sendto(js_cmd.encode(), self.server_addr_port)
        js_data = self.sock_fd.recv(self.BUFFERSIZE)
        js_data = js_data.decode()
        js_data = json.loads(js_data)
        if js_data["status"] != "OK":
            print("Error, server didn't close the connection")
        else:
            print("Connection with server closed")
            self.sock_fd.close()

    def run(self):
        self.create_socket()
        self.print_usage()
        self.receiver_thread = Thread(target=self.reciever)
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        self.sending()

    def sending(self):
        while True:
            try:
                cmd = input()
                cmd_split = cmd.split()
                if len(cmd_split) == 0:
                    continue
                if len(cmd_split) > 3:
                    raise ArgumentException("Wrong usage, too many arguments")
                if cmd_split[0] == "CHECK":
                    self.check_server()
                if cmd_split[0] == "GET":
                    self.get_device_params()
                if cmd_split[0] == "SET":
                    if len(cmd_split) == 3:
                        try:
                            self.set_device_params(int(cmd_split[1]), int(cmd_split[2]))
                        except ValueError as ve:
                            print("wrong parameters for set")
                            print(ve)

                    else:
                        raise ArgumentException("Wrong Usage, with SET u should to provide 2 parameters\n"
                                                "exmpl: SET [regime_arg] [target_temp]")
                if cmd_split[0] == "TIP":
                    self.print_usage()
                if cmd_split[0] == "CLOSE":
                    self.close_connection()
            except ArgumentException as e:
                print("ERRORROROROROR")
                print(e)

    def reciever(self):
        while True:
            data = self.sock_fd.recv(self.BUFFERSIZE)
            data = data.decode()
            js_data = json.loads(data)
            print(js_data['comment'])

    def check_server(self):
        cmd = {
            "command": "CHECK"
        }
        js_cmd = json.dumps(cmd)
        self.sock_fd.sendto(js_cmd.encode(), self.server_addr_port)

    def get_device_params(self):
        cmd = {
            "command": "GET"
        }
        js_cmd = json.dumps(cmd)
        self.sock_fd.sendto(js_cmd.encode(), self.server_addr_port)

    def set_device_params(self, regime, target_temp):
        cmd = {
            "command": "SET",
            "parameters": {
                "regime": regime,
                "target_temp": target_temp
            }
        }
        js_cmd = json.dumps(cmd)
        self.sock_fd.sendto(js_cmd.encode(), self.server_addr_port)

    def create_socket(self):
        self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.sock_fd == -1:
            raise CreationSocketException("Failed to create UDP socket")
        cmd = {
            "command": "CONNECT"
        }
        js_cmd = json.dumps(cmd)
        self.sock_fd.sendto(js_cmd.encode("utf-8"), self.server_addr_port)

    @staticmethod  # Единый метод для всех экземпляров класса
    def print_usage():
        print("--------------------------------------------------------")
        print("Use CHECK - to check server")
        print("Use GET - to get device parameters")
        print("USE SET [regime_arg] [target_temp] - to set device parameters (exmpl:\"SET 5 20\")")
        print("USE TIP - to show this  message")
        print("--------------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Service client",
                                     description="That program is a client for communication with service"
                                                 "which using for setting and getting information about device in"
                                                 "service",
                                     epilog="For more information contact with multiplydino@gmail.com"
                                     )

    parser.add_argument("-A", "--address", default="127.0.0.1", help="Server ip address param")
    parser.add_argument("-P", "--port", default="1337", help="Server port param")
    args = parser.parse_args()
    server_addr = args.address
    server_port = args.port

    client = Client(server_addr, server_port)
    client.run()
