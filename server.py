import socket
from _thread import *
from team import Team, Deets
import pickle
import time
from game import Game

from config import server, port

game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    game_socket.bind((server, port))
except socket.error as e:
    str(e)

game_socket.listen(2)
print("Waiting for a connection, Server Started")

games = {}
idCount = {2: 0, 3: 0, 4: 0}
nextGame = {2: 0, 3: 0, 4: 0}


def threaded_client(conn, teamID, gameID):
    global idCount

    # 1st response to network class is teamID
    conn.send(str.encode(str(teamID)))

    while True:
        try:
            data = pickle.loads(conn.recv(1024))

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
        except:
            break

    print("Lost connection")
    try:
        # if nextGame[games[gameID].mode] == gameID:
        #     idCount[games[gameID].mode] -= 1
        if teamID == 0:
            del games[gameID]
            print("Closing Game", gameID)
    except:
        pass
    return
    conn.close()


gameID = 0
while True:
    # Listen for connection
    conn, address = game_socket.accept()
    print("Connected to:", address)

    teamID = 0
    mode = int(conn.recv(1024).decode())
    idCount[mode] += 1
    requiredPlayers = {2: 2, 3: 2, 4: 4}

    if idCount[mode] % requiredPlayers[mode] == 1:
        gameID += 1
        nextGame[mode] = gameID
        games[gameID] = Game(gameID, mode)
        print("Creating a new mode", mode, "game, ID = ", gameID)
    else:
        teamID = len(games[nextGame[mode]].get_deets())

    if idCount[mode] % requiredPlayers[mode] == 0:
        games[nextGame[mode]].ready = True
        idCount[mode] = 0

    # log connection
    with open("games.dat", "a") as file:
        file.write(str(time.time()) + ", " + str(address) + ", " + str(mode) + ", " + str(gameID))
        file.close()

    print(idCount, address, nextGame[mode], teamID)
    start_new_thread(threaded_client, (conn, teamID, nextGame[mode]))

