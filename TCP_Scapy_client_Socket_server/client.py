from scapy.layers.inet import *
from scapy.all import *

# HOST = ""
HOST = "10.100.102.16"
PORT = 65000
EXIT_KEYWORD = "exit()"
SYN_SEQ_NUMBER = 0
SYN_FLAG = 'S'
ACK_FLAG = 'A'


class Connections:
    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.seq = SYN_SEQ_NUMBER
        self.ack = 0

    def connect(self):
        syn_pkt = (IP(dst=self.host)
                   / TCP(sport=self.port
                         , dport=self.port
                         , flags=SYN_FLAG
                         , seq=SYN_SEQ_NUMBER))

        syn_ack_pkt = sr1(syn_pkt)

        ack_pkt = (IP(dst=self.host)
               / TCP(sport=self.port
                     , dport=self.port
                     , flags=ACK_FLAG
                     , seq=syn_ack_pkt[TCP].ack
                     , ack=syn_ack_pkt[TCP].seq + 1))

        response = sr1(ack_pkt)
        print(response[Raw].load)
        self.ack = ack_pkt[TCP].ack
        self.seq = ack_pkt[TCP].seq

    def inc_seq(self, payload_size):
        self.seq += payload_size

    def inc_ack(self):
        self.ack += 1

    def send_pkt(self, load):
        data_pkt = (IP(dst=self.host)
                    / TCP(sport=self.port, dport=self.port
                          , flags='PA'
                          , seq=self.seq
                          , ack=self.ack)
                    / Raw(load=load))

        send(data_pkt)
        print("seq: ", self.seq)
        print("ack: ", self.ack)
        payload_size = len(data_pkt[Raw].load)
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
            self.connections.send_pkt(self.load)
            self.set_load()

        self.connections.close()


def run_client():
    scapy_tcp_client = Client()
    scapy_tcp_client.client_loop()


if __name__ == "__main__":
    run_client()
