from scapy.layers.inet import *
from scapy.all import *
import argparse
import random


EXIT_KEYWORD = "exit()"
SYN_SEQ_NUMBER = random.randint(0, 4294967296)
CLIENT_PACKETS_FILTER = "tcp and dst host {0} and dst port {1}"
SYN_FLAG = 'S'
ACK_FLAG = 'A'
PUSH_FLAG = 'P'
FIN_FLAG = 'F'


def parameters_from_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('host', type=str, help='set a host')
    parser.add_argument('port', type=int, choices=range(49152, 65536), help='set a port')

    args = parser.parse_args()
    return args


# A function that returns the "loopback" interface from the scapy iface list
# The loopback iface is not connected to any device and used for testing purposes
def get_iface():
    interfaces = get_if_list()
    loopback_iface = ""
    for iface in interfaces:
        if "loopback" in iface.lower():
            loopback_iface = iface

    return loopback_iface


class Connections:
    def __init__(self):
        self.host = args.host
        self.port = args.port
        self.packets_filter = CLIENT_PACKETS_FILTER.format(self.host, self.port)
        self.interface_name = get_iface()
        self.seq = SYN_SEQ_NUMBER
        self.ack = 0

    def connect(self):
        syn_packet = (IP(dst=self.host)
                      / TCP(sport=self.port
                            , dport=self.port
                            , flags=SYN_FLAG
                            , seq=self.seq))

        send(syn_packet)

        print("syn_packet (seq,ack) ", syn_packet.seq, syn_packet.ack)

        syn_ack_packet = sniff(iface=self.interface_name, filter=self.packets_filter, count=1)[0]

        print("syn_ack_packet (seq,ack) ", syn_ack_packet.seq, syn_ack_packet.ack)
        print("syn_ack flag: ", syn_ack_packet[TCP].flags)

        ack_packet = (IP(dst=syn_ack_packet[IP].src)
                      / TCP(sport=syn_ack_packet[TCP].dport
                            , dport=syn_ack_packet[TCP].sport
                            , flags=ACK_FLAG
                            , seq=syn_ack_packet[TCP].ack
                            , ack=syn_ack_packet[TCP].seq + 1))

        print("ack_packet (seq,ack) ", ack_packet.seq, ack_packet.ack)

        send(ack_packet)
        response = sniff(iface=self.interface_name, filter=self.packets_filter, count=1)[0]

        print("connection_msg_packet (seq,ack) ", response.seq, response.ack)
        print("response flag: ", response[TCP].flags)

        print(response[Raw].load.decode('utf-8'))
        self.ack = response[TCP].seq + len(response[Raw].load)
        self.seq = response[TCP].ack + 1

    def inc_seq(self, payload_size):
        self.seq += payload_size

    def inc_ack(self):
        self.ack += 1

    def send_packet(self, load):
        data_packet = (IP(dst=self.host)
                       / TCP(sport=self.port, dport=self.port
                             , flags=(PUSH_FLAG+ACK_FLAG)
                             , seq=self.seq
                             , ack=self.ack)
                       / Raw(load=load.encode('utf-8')))

        send(data_packet)

        print("seq: ", self.seq)
        print("ack: ", self.ack)

        payload_size = len(data_packet[Raw].load)

        print("load: ", payload_size)

        self.inc_seq(payload_size)
        self.inc_ack()

    def close(self):
        print("\nSending a Fin Request To End The Connection...\n")
        fin_request = (IP(dst=self.host)
                       / TCP(sport=self.port
                             , dport=self.port
                             , flags=(FIN_FLAG+ACK_FLAG)
                             , seq=self.seq
                             , ack=self.ack))

        send(fin_request)


class Client:
    def __init__(self):
        self.payload = ""
        self.connections = Connections()
        self.connections.connect()

    def set_payload(self):
        self.payload = input("Type a message: ")

    def client_loop(self):
        self.set_payload()
        while self.payload != EXIT_KEYWORD:
            self.connections.send_packet(self.payload)
            self.set_payload()

        self.connections.close()


def run_client():
    scapy_tcp_client = Client()
    scapy_tcp_client.client_loop()


if __name__ == "__main__":
    args = parameters_from_command_line()
    run_client()
