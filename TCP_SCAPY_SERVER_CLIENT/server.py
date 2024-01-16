from scapy.layers.inet import *
from scapy.all import *


# HOST = ""
HOST = "10.100.102.16"
PORT = 65000
FILTER = f"tcp and dst port 65000 and host {HOST}"
PUSH_ACK_FLAG = 'PA'
SYN_ACK_FLAG = 'SA'
SYN_FLAG = 'S'
FIN_ACK_FLAG = 'FA'


def get_iface():
    interfaces = get_if_list()
    loopback_iface = ""
    for iface in interfaces:
        if "loopback" in iface.lower():
            loopback_iface = iface

    return loopback_iface


class Server:
    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.filter = FILTER
        self.interface_name = get_iface()
        print("Server is listening...")

    def syn_ack_replay(self, syn_packet):
        syn_ack_packet = (IP(src=self.host, dst=syn_packet[IP].src)
                          / TCP(sport=syn_packet[TCP].dport
                                , dport=syn_packet[TCP].sport
                                , flags=SYN_ACK_FLAG
                                , seq=syn_packet[TCP].ack
                                , ack=syn_packet[TCP].seq + 1))
        print("syn_ack: ",syn_ack_packet[TCP].seq, syn_ack_packet[TCP].ack)
        ack_packet = sr1(syn_ack_packet)
        return ack_packet

    def send_connection_msg(self, ack_packet):
        print("ack: ",ack_packet[TCP].seq, ack_packet[TCP].ack)
        connected_packet = (IP(src=self.host, dst=ack_packet[IP].src)
                            / TCP(sport=ack_packet[TCP].dport
                                  , dport=ack_packet[TCP].sport
                                  , flags=PUSH_ACK_FLAG
                                  , seq=ack_packet[TCP].ack
                                  , ack=ack_packet[TCP].seq + 1)
                            / Raw(load="You are connected to the server..".encode('utf-8')))
        print("connection msg: ", connected_packet[TCP].seq, connected_packet[TCP].ack)
        send(connected_packet)

    def handle_messages(self, packet):
        if packet[TCP].flags == SYN_FLAG:
            ack_packet = self.syn_ack_replay(packet)
            print("One client has Connected..")
            self.send_connection_msg(ack_packet)

        elif (packet[TCP].flags == PUSH_ACK_FLAG
              and packet[TCP].seq != 1
              and packet[TCP].ack != 1):

            data = packet[Raw].load.decode('utf-8')
            print(data)

        elif packet[TCP].flags == FIN_ACK_FLAG:
            print("One client has Disconnected..")

    def start_server(self):
        sniff(iface=self.interface_name, filter=self.filter, prn=self.handle_messages)


def activate_server():
    server = Server()
    server.start_server()


if __name__ == "__main__":
    activate_server()



