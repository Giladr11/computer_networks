from scapy.layers.inet import *
from scapy.all import *


def parameters_from_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('host', type=str, help='set a host')
    parser.add_argument('port', type=int, choices=range(49152, 65536), help='set a port')

    args = parser.parse_args()
    return args


# HOST = ""
HOST = "10.100.102.16"
PORT = 65000
EXIT_KEYWORD = "exit()"
SYN_SEQ_NUMBER = 0
SYN_FLAG = 'S'
ACK_FLAG = 'A'
PUSH_ACK_FLAG = 'PA'

class Connections:
    def __init__(self):
        self.host = args.host
        self.port = args.port
        self.seq = SYN_SEQ_NUMBER
        self.ack = 0

    def connect(self):
        syn_pkt = (IP(dst=self.host)
                   / TCP(sport=self.port
                         , dport=self.port
                         , flags=SYN_FLAG
                         , seq=SYN_SEQ_NUMBER))

        syn_ack_packet = sr1(syn_packet)

        ack_packet = (IP(dst=self.host)
               / TCP(sport=self.port
                     , dport=self.port
                     , flags=ACK_FLAG
                     , seq=syn_ack_packet[TCP].ack
                     , ack=syn_ack_packet[TCP].seq + 1))

        response = sr1(ack_packet)
        print(response[Raw].load)
        self.ack = ack_packet[TCP].ack
        self.seq = ack_packet[TCP].seq

    def inc_seq(self, payload_size):
        self.seq += payload_size

    def inc_ack(self):
        self.ack += 1

    def send_packet(self, load):
        data_packet = (IP(dst=self.host)
                    / TCP(sport=self.port, dport=self.port
                          , flags=PUSH_ACK_FLAG
                          , seq=self.seq
                          , ack=self.ack)
                    / Raw(load=load))

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
                     , flags='FA'
                     , seq=self.seq
                     , ack=self.ack))

        send(fin_request)


class Client:
    def __init__(self):
        self.load = ""
        self.connections = Connections()
        self.connections.connect()

    def set_load(self):
        self.load = input("Type a message: ")

    def client_loop(self):
        self.set_load()
        while self.load != EXIT_KEYWORD:
            self.connections.send_packet(self.load)
            self.set_load()

        self.connections.close()


def run_client():
    scapy_tcp_client = Client()
    scapy_tcp_client.client_loop()


if __name__ == "__main__":
    args = parameters_from_command_line()
    run_client()
