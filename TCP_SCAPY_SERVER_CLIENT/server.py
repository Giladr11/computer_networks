from scapy.layers.inet import *
from scapy.all import *
import argparse


SERVER_PACKETS_FILTER = "tcp and dst host {0} and dst port {1}"
PUSH_FLAG = 'P'
SYN_FLAG = 'S'
ACK_FLAG = 'A'
FIN_FLAG = 'F'
URG_FLAG = 'U'


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


class Server:
    def __init__(self):
        self.host = args.host
        self.port = args.port
        self.packets_filter = SERVER_PACKETS_FILTER.format(self.host, self.port)
        self.interface_name = get_iface()
        print("Server is listening...")

    def syn_ack_replay(self, syn_packet):
        syn_ack_packet = (IP(src=self.host, dst=syn_packet[IP].src)
                          / TCP(sport=syn_packet[TCP].dport
                                , dport=syn_packet[TCP].sport
                                , flags=SYN_FLAG+ACK_FLAG
                                , seq=syn_packet[TCP].ack
                                , ack=syn_packet[TCP].seq + 1))

        send(syn_ack_packet)

        print("syn_packet (seq,ack) ", syn_packet.seq, syn_packet.ack)
        print("syn_ack_packet (seq,ack) ", syn_ack_packet.seq, syn_ack_packet.ack)

        ack_packet = sniff(iface=self.interface_name, filter=self.packets_filter, count=1)[0]

        print("ack flag: ", ack_packet[TCP].flags)

        return ack_packet

    def send_connection_msg(self, ack_packet):
        connection_msg_packet = (IP(src=self.host, dst=ack_packet[IP].src)
                                 / TCP(sport=ack_packet[TCP].dport
                                       , dport=ack_packet[TCP].sport
                                       , flags=URG_FLAG+ACK_FLAG
                                       , seq=ack_packet[TCP].ack
                                       , ack=ack_packet[TCP].seq + 1)
                                 / Raw(load="You are connected to the server..".encode('utf-8')))

        print("ack_packet (seq,ack) ", ack_packet.seq, ack_packet.ack)
        print("connection_msg_packet (seq,ack) ", connection_msg_packet.seq, connection_msg_packet.ack)

        send(connection_msg_packet)

    def handle_messages(self, packet):
        if packet[TCP].flags == SYN_FLAG:
            ack_packet = self.syn_ack_replay(packet)
            print("One client has Connected..")
            self.send_connection_msg(ack_packet)

        elif packet[TCP].flags == (PUSH_FLAG+ACK_FLAG):
            data = packet[Raw].load.decode('utf-8')
            print(data)

        elif packet[TCP].flags == (FIN_FLAG+ACK_FLAG):
            print("One client has Disconnected..")

    def start_server(self):
        print(self.packets_filter)
        sniff(iface=self.interface_name, filter=self.packets_filter, prn=self.handle_messages)


def activate_server():
    server = Server()
    server.start_server()


if __name__ == "__main__":
    args = parameters_from_command_line()
    activate_server()
