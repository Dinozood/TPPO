import json
import socket
import argparse

from Device import Conditioner


class Server():
    def __init__(self, addr, port):
        self.sock_fd = 0
        pass

    def run(self):
        pass


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
