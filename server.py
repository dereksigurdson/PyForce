import socket
from _thread import *
from team import Team, Deets
import pickle
import time
from game import Game


server = "192.168.2.133"
port = 5555

game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    game_socket.bind((server, port))
except socket.error as e:
    str(e)

game_socket.listen(2)
print("Waiting for a connection, Server Started")

# connected = set()  # nec?
games = {}
idCount = 0


def threaded_client(conn, teamID, gameID):
    global idCount

    # 1st response to netwotrk class is teamID
    conn.send(str.encode(str(teamID)))

    while True:
        # try:
        data = pickle.loads(conn.recv(2048))

        if gameID in games:  # don't know why it wouldn't be
            game = games[gameID]

            if not data:
                print("Disconnected")
                break
            else:
                # if data != "get":
                game.put_deets(data)
                # else:
                #     print("Data = get")  # again - dunno
                conn.sendall(pickle.dumps(game.get_deets()))
        # except:
        #     break

    print("Lost connection")
    try:
        del games[gameID]
        print("Closing Game", gameID)
    except:
        pass
    idCount -= 1
    conn.close()


gameID = 0
while True:
    conn, address = game_socket.accept()
    print("Connected to:", address)

    idCount += 1
    teamID = 0
    mode = int(conn.recv(2048).decode())
    players = mode if mode != 3 else 2

    if idCount % players == 1:
        gameID += 1
        games[gameID] = Game(gameID, mode)
        print("Creating a new mode", mode, "game, ID = ", gameID)
    else:
        teamID = len(games[gameID].get_deets())

    if idCount % players == 0:
        games[gameID].ready = True

    # log connection
    with open("games.dat", "ab") as file:
        pickle.dump([time.time(), address, mode, gameID], file)
        file.close()

    start_new_thread(threaded_client, (conn, teamID, gameID))


