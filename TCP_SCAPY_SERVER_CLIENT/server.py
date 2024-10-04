from scapy.layers.inet import *
from scapy.all import *
import random
import argparse


SYN_FLAG = 'S'
ACK_FLAG = 'A'
FIN_FLAG = 'F'
INTERFACE = "\\Device\\NPF_{C357C829-E948-47FF-B0D2-608BDF16AFDC}"  # The Ethernet Interface
SERVER_PACKETS_FILTER = "tcp and dst host %s and dst port %s"
SYN_ACK_SEQ = random.randint(0, 4294967296)


def parameters_from_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('host', type=str, help='set a host')
    parser.add_argument('port', type=int, choices=range(49152, 65536), help='set a port')

    args = parser.parse_args()
    return args


class Server:
    def __init__(self):
        self.host = args.host
        self.port = args.port
        self.iface = INTERFACE
        self.packets_filter = SERVER_PACKETS_FILTER % (self.host, self.port)
        self.syn_ack_seq = SYN_ACK_SEQ
        print("Server is listening...")

    def syn_ack_replay(self, syn_packet):
        syn_ack_packet = (IP(src=self.host, dst=syn_packet[IP].src)
                          / TCP(sport=syn_packet[TCP].dport
                                , dport=syn_packet[TCP].sport
                                , flags=SYN_FLAG+ACK_FLAG
                                , seq=self.syn_ack_seq
                                , ack=syn_packet[TCP].seq + 1))

        send(syn_ack_packet, iface=self.iface)

        print("syn_packet (seq,ack) ", syn_packet.seq, syn_packet.ack)
        print("syn_ack_packet (seq,ack) ", syn_ack_packet.seq, syn_ack_packet.ack)

        ack_packet = sniff(iface=self.iface, filter=self.packets_filter, count=1)[0]

        print("ack flag: ", ack_packet[TCP].flags)

        return ack_packet

    def send_connection_msg(self, ack_packet):
        connection_msg_packet = (IP(src=self.host, dst=ack_packet[IP].src)
                                 / TCP(sport=ack_packet[TCP].dport
                                       , dport=ack_packet[TCP].sport
                                       , seq=ack_packet[TCP].ack
                                       , ack=ack_packet[TCP].seq + 1
                                       , flags='')
                                 / Raw(load="You are connected to the server..".encode('utf-8')))

        print("ack_packet (seq,ack) ", ack_packet.seq, ack_packet.ack)
        print("connection_msg_packet (seq,ack) ", connection_msg_packet.seq, connection_msg_packet.ack)

        send(connection_msg_packet, iface=self.iface)

    def handle_messages(self, packet):
        if SYN_FLAG in packet[TCP].flags:
            ack_packet = self.syn_ack_replay(packet)
            print("One client has Connected..")
            self.send_connection_msg(ack_packet)

        elif FIN_FLAG in packet[TCP].flags:
            print("One client has Disconnected..")

        elif Raw in packet:
            print("received message: ", packet[Raw].load.decode('utf-8'))

    def start_server(self):
        print(self.packets_filter)
        sniff(iface=self.iface, filter=self.packets_filter, prn=self.handle_messages)


def activate_server():
    server = Server()
    server.start_server()


if __name__ == "__main__":
    args = parameters_from_command_line()
    activate_server()

