from scapy.layers.inet import *
from scapy.all import *

LOOP_BACK_IFACE = ""
L4_PROTOCOL = UDP
DPORT = 50000
FILTER = f"udp and dst port 50000"


def get_iface():
    interfaces = get_if_list()
    loopback_iface = ""
    for iface in interfaces:
        if "loopback" in iface.lower():
            loopback_iface = iface
    
    return loopback_iface


loopback_iface = get_iface()


class Scapy_Server:
    def __init__(self):
        self.l4_protocol = L4_PROTOCOL
        self.dport = DPORT
        self.sniff_filter = FILTER
        self.interface_name = LOOP_BACK_IFACE

    def handle_received_msg(self, pkt):
        if (self.l4_protocol in pkt and
                pkt[UDP].dport == self.dport):

            print("A message from port: {0} has been received..".format(self.dport))
            print(str(pkt.load))

    def start_server(self):
        print("server is listening...")
        sniff(iface=self.interface_name, filter=self.sniff_filter, prn=self.handle_received_msg)


def run_server():
    server = Scapy_Server()
    server.start_server()


if __name__ == "__main__":
    run_server()
