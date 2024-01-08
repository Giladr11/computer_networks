import socket
import threading

# HOST = ""
HOST = "10.100.102.16"
PORT = 65000


class TCP_SERVER:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(1)
        print("server is listening...")

    @staticmethod
    def receive_messages(client):
        while True:
            msg = client.recv(1024)
            if not msg:
                print("1 client has disconnected")
                break
            print(msg.decode('utf-8'))
        client.close()

    def accept_connections(self):
        while True:
            client, address = self.server.accept()
            print("one client has connected!")
            client.send("You are connected to the server..".encode('utf-8'))
            main_thread = threading.Thread(target=self.receive_messages, args=(client,))
            main_thread.start()


def main():
    tcp_server = TCP_SERVER()
    tcp_server.accept_connections()


if __name__ == "__main__":
    main()
