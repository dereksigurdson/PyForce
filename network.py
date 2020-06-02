import socket
import pickle


class Network:
    def __init__(self, mode):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "xxx.xx.xx.xxx"
        self.port = 5555
        self.address = (self.server, self.port)
        self.teamID = self.connect(mode)

    def get_teamID(self):
        return self.teamID

    def connect(self, mode):
        try:
            self.client.connect(self.address)
            self.client.send(str.encode(str(mode)))
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)
