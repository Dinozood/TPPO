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
        self.sock_fd = 0
        self.server_addr = _server_addr
        self.server_port = _server_port
        self.server_addr_port = (self.server_addr, int(self.server_port))
        self.server_addr_port = ("127.0.0.1", 1337)
        self.IO_mutex = Lock()
        self.BUFFERSIZE = 4096

    def sending(self):
        while True:
            try:
                cmd = input()
                cmd_split = cmd.split()
                if len(cmd_split) > 3:
                    raise ArgumentException("Wrong usage, too many arguments")
                if cmd_split[0] == "CHECK":
                    self.check_server()
                if cmd_split[0] == "GET":
                    self.get_device_params()
                if cmd_split[0] == "SET":
                    if len(cmd_split) == 3:
                        self.set_device_params(cmd_split[1], cmd_split[2])
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

    def run(self):
        self.create_socket()
        sending_thread = Thread(target=self.sending)
        sending_thread.daemon = True  # Чтобы не плодить сирот и зомбей
        sending_thread.start()
        self.print_usage()
        while True:
            pass
            # data = self.sock_fd.recv(self.BUFFERSIZE)
            # if not data:
            #     break
            # print(data.decode())

    def create_socket(self):
        self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.sock_fd == -1:
            raise CreationSocketException("Failed to create UDP socket")
        cmd = {
            "command": "CONNECT"
        }
        js_cmd = json.dumps(cmd)
        self.sock_fd.sendto(js_cmd.encode("utf-8"), self.server_addr_port)
        js_data = self.sock_fd.recv(self.BUFFERSIZE)
        js_data = js_data.decode()
        js_data = json.loads(js_data)
        if js_data["status"] == "OK":
            print(f"Connected to server at {self.server_addr}:{self.server_port}")

    @staticmethod  # Единый метод для всех экземпляров класса
    def print_usage():
        print("--------------------------------------------------------")
        print("Use CHECK - to check server")
        print("Use GET - to get device parameters")
        print("USE SET [regime_arg] [target_temp] - to set device parameters (exmpl:\"SET 5 20\")")
        print("USE TIP - to show this  message")
        print("--------------------------------------------------------")

    def check_server(self):
        cmd = {
            "command": "CHECK"
        }
        js_cmd = json.dumps(cmd)
        self.sock_fd.sendto(js_cmd.encode(), self.server_addr_port)
        data = self.sock_fd.recv(self.BUFFERSIZE)
        data = data.decode()
        js_data = json.loads(data)
        if js_data["status"] == "OK":
            print("Server is alive")
        else:
            print("Unknown error, server sent something strange")

    def get_device_params(self):
        cmd = {
            "command": "GET"
        }
        js_cmd = json.dumps(cmd)
        self.sock_fd.sendto(js_cmd.encode(), self.server_addr_port)
        data = self.sock_fd.recv(self.BUFFERSIZE)
        data = data.decode()
        js_data = json.loads(data)
        print(f"Device parameters are\n"
              f"REGIME - {js_data['regime']}\n"
              f"TARGET TEMPERATURE - {js_data['target_temp']}\n"
              f"CURRENT TEMPERATURE - {js_data['current_temp']}\n")

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
        js_data = self.sock_fd.recv(self.BUFFERSIZE)
        js_data = js_data.decode()
        js_data = json.loads(js_data)
        if js_data["status"] != "OK":
            print("Error, please use right parameters, 0 => REGIME => 10 and 15 => TARGET_TEMP => 35")
        else:
            print("Device parameters are setted")

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
