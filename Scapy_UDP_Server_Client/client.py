from scapy.layers.inet import *
from scapy.all import *
import argparse

TTL = 64
EXIT_KEYWORD = "exit()"


def parameters_from_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('src_ip', type=str, help='set a src_ip')
    parser.add_argument('dst_ip', type=str, help='set a dst_ip')
    parser.add_argument('sport', type=int, choices=range(49152, 65536), help='set a sport')
    parser.add_argument('dport', type=int, choices=range(49152, 65536), help='set a dport')

    args = parser.parse_args()
    return args


class Packet:
    def __init__(self):
        self.ttl = TTL
        self.src_ip = args.src_ip
        self.dst_ip = args.dst_ip
        self.sport = args.sport
        self.dport = args.dport
        self.load = ""

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
    args = parameters_from_command_line()
    run_client()

