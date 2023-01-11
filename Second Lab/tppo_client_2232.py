import requests
import socketio
import argparse

from First_tppo_client_2232 import ArgumentException, Client

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
    url = f"http://{server_addr}:{server_port}/device"
    sio = socketio.Client()
    my = False


    def get_device_params():
        return requests.get(url + "/whole_info")


    def check_server():
        return requests.get(url + "/check")


    def set_device_params(regime, target_temp):
        return requests.get(url + f"?regime={regime}&target_temp={target_temp}")


    @sio.event
    def connect():
        print("CONNECTED")
        while True:
            print("ENTER CMD")
            try:
                cmd = input()
                cmd_split = cmd.split()
                if len(cmd_split) == 0:
                    continue
                if len(cmd_split) > 3:
                    raise ArgumentException("Wrong usage, too many arguments")
                if cmd_split[0] == "GET":
                    repl = get_device_params()
                    print(f"RESPONSE[{repl.status_code}]: {repl.content.decode()}")
                if cmd_split[0] == "CHECK":
                    repl = check_server()
                    print(f"RESPONSE[{repl.status_code}]: {repl.content.decode()}")
                if cmd_split[0] == "SET":
                    if len(cmd_split) == 3:
                        repl = set_device_params(int(cmd_split[1]), int(cmd_split[2]))
                        print(f"RESPONSE[{repl.status_code}]: {repl.content.decode()}")
                    else:
                        raise ArgumentException("Wrong Usage, with SET u should to provide 2 parameters\n"
                                                "exmpl: SET [regime_arg] [target_temp]")
                if cmd_split[0] == "TIP":
                    Client.print_usage()
                if cmd_split[0] == "CLOSE":
                    sio.disconnect()
            except ArgumentException as e:
                print(e)


    @sio.event
    def disconnect():
        print("I'm disconnected")


    @sio.on("Alarm")
    def notify(msg):
        print(f"SERVER MESSAGE: {msg['comment']}")


    Client.print_usage()
    sio.connect(f"http://{server_addr}:{server_port}")
