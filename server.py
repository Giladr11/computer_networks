from scapy.layers.inet import *
from scapy.all import *

interfaces = get_if_list()
LOOP_BACK_IFACE = ""

for iface in interfaces:
    if "loopback" in iface.lower():
        LOOP_BACK_IFACE = iface


L4_PROTOCOL = UDP
DPORT = 50000
FILTER = f"udp and dst port {DPORT}"


class SCAPY_SERVER:
    def __init__(self):
        self.l4_protocol = L4_PROTOCOL
        self.dport = DPORT
        self.sniff_filter = FILTER
        self.interface_name = LOOP_BACK_IFACE

    def handle_received_msg(self, packet):
        if (self.l4_protocol in packet and
                packet[UDP].dport == self.dport):

            print("A message from port: {0} has been received..".format(self.dport))
            print(packet.load)

    def start_server(self):
        print("server is listening...")
        sniff(iface=self.interface_name, filter=self.sniff_filter, prn=self.handle_received_msg)


def run_server():
    server = SCAPY_SERVER()
    server.start_server()


if __name__ == "__main__":
    run_server()
