from scapy.layers.inet import *
from scapy.all import *
import argparse
import random


EXIT_KEYWORD = "exit()"
SYN_SEQ = random.randint(0, 4294967296)
SYN_FLAG = 'S'
ACK_FLAG = 'A'
FIN_FLAG = 'F'
INTERFACE = "\\Device\\NPF_{C357C829-E948-47FF-B0D2-608BDF16AFDC}"  # The Ethernet Interface
CLIENT_PACKETS_FILTER = "tcp and src host %s and src port %s"


def parameters_from_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('host', type=str, help='set a host')
    parser.add_argument('port', type=int, choices=range(49152, 65536), help='set a port')

    args = parser.parse_args()
    return args


class Connections:
    def __init__(self):
        self.host = args.host
        self.port = args.port
        self.seq = SYN_SEQ
        self.ack = 0
        self.iface = INTERFACE
        self.filter = CLIENT_PACKETS_FILTER % (self.host, self.port)

    def connect(self):
        syn_packet = (IP(dst=self.host)
                      / TCP(dport=self.port
                            , flags=SYN_FLAG
                            , seq=self.seq))

        print("syn_packet: (syn/ack)", syn_packet[TCP].seq, syn_packet[TCP].ack)

        syn_ack_packet = sr1(syn_packet, iface=self.iface)

        print("syn_ack_packet: (syn/ack)", syn_ack_packet[TCP].seq, syn_ack_packet[TCP].ack)

        ack_packet = (IP(dst=self.host)
                      / TCP(dport=self.port
                            , flags=ACK_FLAG
                            , seq=syn_ack_packet[TCP].ack
                            , ack=syn_ack_packet[TCP].seq + 1))

        print("ack_packet: (syn/ack)", ack_packet[TCP].seq, ack_packet[TCP].ack)

        response = sr1(ack_packet, iface=self.iface)

        print(response[Raw].load.decode('utf-8'))

        self.ack = response[TCP].seq
        self.seq = response[TCP].ack

        print("response seq: ", response[TCP].seq)
        print("response ack: ", response[TCP].ack)

    def inc_seq(self, payload_size):
        self.seq += payload_size

    def inc_ack(self):
        self.ack += 1

    def send_packet(self, payload):
        data_packet = (IP(dst=self.host)
                       / TCP(dport=self.port
                             , seq=self.seq
                             , ack=self.ack
                             , flags='')
                       / Raw(load=payload.encode('utf-8')))

        send(data_packet, iface=self.iface)

        print("seq: ", self.seq)
        print("ack: ", self.ack)

        payload_size = len(data_packet[Raw].load)
        print("load: ", payload_size)

        self.inc_seq(payload_size)
        self.inc_ack()

    def close(self):
        print("\nSending a Fin Request To End The Connection...\n")
        fin_request = (IP(dst=self.host)
                       / TCP(dport=self.port
                             , flags=FIN_FLAG+ACK_FLAG
                             , seq=self.seq
                             , ack=self.ack))

        send(fin_request, iface=self.iface)


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
