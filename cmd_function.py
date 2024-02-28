import glob
import os
import shutil
import subprocess
import pyscreeze
import colorama  # Set colorama's initiating mode to True
from colorama import Fore  # Set colors to function's results


class Commands:
    def __init__(self):
        colorama.init(autoreset=True)
        self.commands_dict = {'/dir': (self.dir, 1)
                              , '/delete': (self.delete, 1)
                              , '/copy': (self.copy, 2)
                              , '/execute': (self.execute, 1)
                              , '/take_screenshot': (self.take_screenshot, 1)
                              , '/send_file': (self.send_file, 1)}

    @staticmethod
    def dir(directory_url):
        dir_files = glob.glob(directory_url + "\*.*")

        if not dir_files:
            return f"{Fore.LIGHTRED_EX}'{directory_url}' wasn't Found..{Fore.RESET}"

        else:
            return f"{Fore.LIGHTGREEN_EX}The List of Files in '{directory_url}':\n\n{dir_files}{Fore.RESET}"

    @staticmethod
    def delete(file_url):
        try:
            os.remove(file_url)
            return f"{Fore.LIGHTGREEN_EX}'{file_url}' has been Deleted Successfully!{Fore.RESET}"

        except Exception:
            return f"{Fore.LIGHTRED_EX}Couldn't Delete '{file_url}'{Fore.RESET}"

    @staticmethod
    def copy(src_file, dst_file):
        try:
            if src_file != dst_file:
                shutil.copy(src_file, dst_file)
                return f"{Fore.LIGHTGREEN_EX}{src_file} has been Copied Successfully to '{dst_file}'{Fore.RESET}"

            else:
                return f"{Fore.LIGHTRED_EX}Couldn't Copy a file to its own url{Fore.RESET}"

        except Exception:
            return f"{Fore.LIGHTRED_EX}Couldn't Copy '{src_file}' to '{dst_file}'{Fore.RESET}"

    @staticmethod
    def execute(application):
        try:
            subprocess.call(application)
            split_app_link = application.split('\\')
            if '.exe' in application:
                return f"{Fore.LIGHTGREEN_EX}'{[d for d in split_app_link if '.exe' in d]}' Is Running..{Fore.LIGHTRED_EX}"

            else:
                return f"{Fore.LIGHTGREEN_EX}'{application}' Opened..{Fore.LIGHTRED_EX}"

        except Exception:
            return f"{Fore.LIGHTRED_EX}Couldn't Run '{application}'{Fore.RESET}"

    @staticmethod
    def take_screenshot(location_to_save):
        try:
            image = pyscreeze.screenshot()
            try:
                image.save(location_to_save)
                return f"{Fore.LIGHTGREEN_EX}The Screenshot is saved at '{location_to_save}'{Fore.RESET}"

            except Exception:
                return f"{Fore.LIGHTRED_EX}Couldn't save the Screenshot at '{location_to_save}'{Fore.RESET}"

        except Exception:
            return f"{Fore.LIGHTRED_EX}Couldn't take a Screenshot{Fore.RESET}"

    @staticmethod
    def send_file(file_url, client):
        try:
            if os.path.exists(file_url) is True:
                file_size = os.path.getsize(file_url)
                _, file_type = file_url.split('.')
                file_info = f'.{file_type}/{file_size}'

                client.send(str(len(file_info)).encode('utf-8'))
                client.send(file_info.encode('utf-8'))

                file = open(file_url, 'rb')
                data = file.read()
                client.sendall(data)

            else:
                client.send(f"{Fore.LIGHTRED_EX}{file_url} Doesn't exist..{Fore.RESET}".encode('utf-8'))

        except Exception:
            client.send(f"{Fore.LIGHTRED_EX}{file_url} Delivery has Failed{Fore.RESET}".encode('utf-8'))
