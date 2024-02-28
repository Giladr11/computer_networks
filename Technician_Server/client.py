import socket
import colorama  # Set colorama's initiating mode to True
from colorama import Fore  # Set colors to the help info and success/failed messages
import argparse  # Set HOST & PORT when running the script
import logging


EXIT_KEYWORD = "exit()"
ERROR_MESSAGE = "An error occurred!"
LOG_DISCONNECTED_MESSAGE = "The Client has Disconnected from the server"
COMMAND_KEYCHAR = "/"
COMMANDS_LIST = ['/dir', '/delete', '/copy', '/execute', '/take_screenshot', '/send_file']
BUFFER_SIZE = 1024
COMMANDS_HELP_INFO = (f"{Fore.LIGHTYELLOW_EX}The Commands you can use are:\n"
                      f"1. {COMMANDS_LIST[0]}  __full_directory_url__\n"
                      f"2. {COMMANDS_LIST[1]}  __full_file_url_\n"
                      f"3. {COMMANDS_LIST[2]}  __full_file_url___full_file_url__\n"
                      f"4. {COMMANDS_LIST[3]}  __app_url__\n"
                      f"5. {COMMANDS_LIST[4]}  __full_file_url_to_save_at__\n"
                      f"6. {COMMANDS_LIST[5]}  __full_file_url__to_save_at_{Fore.RESET}")


def params_from_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('host', type=str, help="Set Host IP")
    parser.add_argument('port', type=int, choices=range(49152, 65536), help="Set Port")

    args = parser.parse_args()
    return args


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((args.host, args.port))
        print(self.client.recv(BUFFER_SIZE).decode('utf-8'))
        self.message = ""

    def set_message(self):
        self.message = input("Type a message: ")

    def send_message(self):
        self.client.send(self.message.encode('utf-8'))

    @staticmethod
    def log_message(message):
        logging.info(f'Client Received: {message}')

    def save_received_file(self, message):
        file_type, file_size = message.split('/')

        print("file's type: ", file_type)
        print("file's size: ", file_size)

        data = self.client.recv(int(file_size))

        file_name = input("Type a name for the new file: ")

        try:
            with open(file_name + file_type, 'wb') as f:
                f.write(data)

            print(f"{Fore.LIGHTGREEN_EX}{file_name+file_type} is Saved!{Fore.RESET}")

        except Exception:
            print(f"{Fore.LIGHTRED_EX}Couldn't save File..{Fore.RESET}")

    def send_messages(self):
        self.set_message()
        while self.message != EXIT_KEYWORD:
            colorama.init(autoreset=True)

            if self.message.startswith(COMMAND_KEYCHAR):
                command_status = False

                for command in COMMANDS_LIST:
                    if self.message.startswith(command):
                        command_status = True

                if command_status is False:
                    print(COMMANDS_HELP_INFO)

                else:
                    self.send_message()
                    self.receive_messages()

            else:
                self.send_message()

            self.set_message()

        self.log_message(LOG_DISCONNECTED_MESSAGE)
        self.client.close()

    def receive_messages(self):
        colorama.init(autoreset=True)

        try:
            message_size = self.client.recv(BUFFER_SIZE).decode('utf-8')
            message = self.client.recv(int(message_size)).decode('utf-8')

            if message.startswith('.'):
                self.save_received_file(message)

            else:
                print("\n" + message + "\n")
                self.log_message(message)

        except Exception:
            print(ERROR_MESSAGE)
            self.log_message(LOG_DISCONNECTED_MESSAGE)
            self.client.close()


def run_client():
    client = Client()
    client.send_messages()


if __name__ == "__main__":
    args = params_from_command_line()
    logging.basicConfig(filename='client.log',
                        level=logging.INFO
                        , format='[%(asctime)s] %(message)s'
                        , datefmt='%Y-%m-%d %H:%M:%S')
    run_client()
