import socket
import threading
import colorama  # For setting colorama's initiating mode to True
from cmd_function import Commands
import argparse
import logging


HEADER_SIZE = 10
DISCONNECTED_MESSAGE = "One client has Disconnected!"
CONNECTED_MESSAGE = "One client has connected to the server!"
CONNECTED_MESSAGE_TO_CLIENT = "You are connected to the server!"
SERVER_RUNNING_MESSAGE = "server is listening..."
LOG_DISCONNECTED_MESSAGE = "The Client has Disconnected the server"
SEND_FILE_KEYWORD = '/send_file'


def params_from_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('host', type=str, help="Set Host IP")
    parser.add_argument('port', type=int, choices=range(49152, 65536), help="Set Port")

    args = parser.parse_args()
    return args


class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((args.host, args.port))
        self.server.listen()
        print(SERVER_RUNNING_MESSAGE)

    @staticmethod
    def log_message(message):
        logging.info(f'Server Received: {message}')

    def receive_messages(self, client):
        while True:
            colorama.init(autoreset=True)

            try:
                message_size = client.recv(HEADER_SIZE).decode('utf-8')
                message = client.recv(int(message_size)).decode('utf-8')
                self.log_message(message)

                if not message:
                    print(DISCONNECTED_MESSAGE)
                    self.log_message(LOG_DISCONNECTED_MESSAGE)
                    break

                print(message)

                for command in Commands().commands_dict.keys():
                    if message.startswith(command):
                        match Commands().commands_dict[command][1]:
                            case 1:
                                if command == SEND_FILE_KEYWORD:
                                    function = Commands().commands_dict[command][0]
                                    param = message[len(command)+1:]
                                    function(param, client)

                                else:
                                    function = Commands().commands_dict[command][0]
                                    param = message[len(command) + 1:]
                                    result = function(param)
                                    print(result)
                                    client.send(str(len(result)).encode('utf-8'))
                                    client.send(result.encode('utf-8'))

                            case 2:
                                function = Commands().commands_dict[command][0]
                                first_param, second_param = message[len(command) + 1:].split(' ')
                                result = function(first_param, second_param)
                                print(result)
                                client.send(str(len(result)).encode('utf-8'))
                                client.send(result.encode('utf-8'))

            except Exception:
                print(DISCONNECTED_MESSAGE)
                self.log_message(LOG_DISCONNECTED_MESSAGE)
                client.close()
                break

    def accept_connections(self):
        while True:
            client, address = self.server.accept()

            print(CONNECTED_MESSAGE)
            client.send(CONNECTED_MESSAGE_TO_CLIENT.encode('utf-8'))

            main_thread = threading.Thread(target=self.receive_messages, args=(client,))
            main_thread.start()


def run_server():
    server = Server()
    server.accept_connections()


if __name__ == "__main__":
    args = params_from_command_line()
    logging.basicConfig(filename='server.log',
                        level=logging.INFO
                        , format='[%(asctime)s] %(message)s'
                        , datefmt='%Y-%m-%d %H:%M:%S')

    run_server()
