from scapy.layers.inet import *
from scapy.all import *
import argparse

TTL = 64
EXIT_KEYWORD = "exit()"


def parameters_from_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('src_ip', type=str, help='set a src_ip')
    parser.add_argument('dst_ip', type=str, help='set a dst_ip')
    parser.add_argument('sport', type=int, help='set a sport')
    parser.add_argument('dport', type=int, help='set a dport')

    args = parser.parse_args()
    return args


class Packet:
    def __init__(self):
        self.ttl = TTL
        self.src_ip = str(parameters_from_command_line().src_ip)
        self.dst_ip = str(parameters_from_command_line().dst_ip)
        self.sport = int(parameters_from_command_line().sport)
        self.dport = int(parameters_from_command_line().dport)
        self.load = ""
        print(self.src_ip, self.dst_ip, self.sport, self.dport)

    def set_load(self):
        self.load = input("type a message: ")

    def craft_packet(self):
        pkt = (IP(ttl=self.ttl, src=self.src_ip, dst=self.dst_ip) /
               UDP(sport=self.sport, dport=self.dport)/str(self.load))

        return pkt

    def send_packet(self):
        send(self.craft_packet())


class Client(Packet):
    def client_loop(self):
        self.set_load()
        while self.load != EXIT_KEYWORD:
            self.craft_packet()
            self.send_packet()
            self.set_load()


def run_client():
    client = Client()
    client.client_loop()


if __name__ == "__main__":
    run_client()

