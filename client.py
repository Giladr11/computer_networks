from scapy.layers.inet import *
from scapy.all import *
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('src_ip', type=str, help='set a src_ip')
parser.add_argument('dst_ip', type=str, help='set a dst_ip')
parser.add_argument('sport', type=int, help='set a sport')
parser.add_argument('dport', type=int, help='set a dport')

args = parser.parse_args()


TTL = 64
SRC_IP = args.src_ip    #"10.100.102.1"
DST_IP = args.dst_ip    #"10.100.102.16"
SPORT = args.sport      #49700
DPORT = args.dport      #50000
EXIT_KEYWORD = "exit()"
print(SRC_IP, DST_IP, SPORT, DPORT)


class PACKET:
    def __init__(self):
        self.ttl = TTL
        self.src_ip = str(SRC_IP)
        self.dst_ip = str(DST_IP)
        self.sport = int(SPORT)
        self.dport = int(DPORT)
        self.load = input("type a message: ")

    def set_load(self):
        self.load = input("type a message: ")

    def craft_packet(self):
        packet = IP(ttl=self.ttl, src=self.src_ip, dst=self.dst_ip)/UDP(sport=self.sport, dport=self.dport)/self.load
        return packet

    def send_packet(self):
        send(self.craft_packet())


class Client(PACKET):
    def client_loop(self):
        while self.load != EXIT_KEYWORD:
            self.craft_packet()
            self.send_packet()
            self.set_load()


def main():
    client = Client()
    client.client_loop()


if __name__ == "__main__":
    main()

