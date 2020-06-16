import socket
import pickle

from config import server, port

class Network:
    def __init__(self, mode):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
        self.address = (self.server, self.port)
        self.teamID = self.connect(mode)

    def get_teamID(self):
        return self.teamID

    def connect(self, mode):
        try:
            self.client.connect(self.address)
            self.client.send(str.encode(str(mode)))
            self.client.settimeout(.04)
            return self.client.recv(1024).decode()
        except socket.error as e:
            print(e)
            return "Server not available"

    def send(self, data, force=False):
        if force:
            self.client.settimeout(2)
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(1024))
        except socket.error as e:
            print(e)
        self.client.settimeout(.04)
