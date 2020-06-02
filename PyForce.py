# PyForce
#
# PyRat drones have infiltrated the trade route and must be cleared.
# Drone AI gets more advanced as each level is cleared.
#
# Derek Sigurdson
# April 2020

import pickle
import pygame
import random
import sys
import time

from team import Team, Ship, hit, Deets
from network import Network
from config import size, border, gridleft, gridtop
from pygame.locals import *

# import os
# os.chdir("c:\\2020\\Python\\Projects\\PyForceWeb")

screensize = screenwidth, screenheight = 950, 560  # 490, 1000
screen = pygame.display.set_mode(screensize)
pygame.display.set_caption("PyForce")
info = pygame.Rect(500, 90, 450, 450)  # (20, 560, 450, 430)

pygame.init()
pygame.font.init()
font20 = pygame.font.Font("consolas.ttf", 20)
font40 = pygame.font.Font("consolas.ttf", 40)
pygame.mixer.init()
s_bzzt = pygame.mixer.Sound("sounds/bzzt.wav")
s_side = pygame.mixer.Sound("sounds/side.wav")
s_boom = [pygame.mixer.Sound("sounds/boom0.wav"),
          pygame.mixer.Sound("sounds/boom1.wav"),
          pygame.mixer.Sound("sounds/boom2.wav"),
          pygame.mixer.Sound("sounds/boom3.wav"),
          pygame.mixer.Sound("sounds/boom4.wav"),
          pygame.mixer.Sound("sounds/boom5.wav"),
          pygame.mixer.Sound("sounds/boom6.wav"),
          pygame.mixer.Sound("sounds/boom7.wav")]
s_shot = [pygame.mixer.Sound("sounds/laser_x.wav"),
          pygame.mixer.Sound("sounds/laser_y.wav"),
          pygame.mixer.Sound("sounds/laser_z.wav")]

grid = pygame.image.load("images/grid.gif")
info_1p = pygame.image.load("images/info_1p.gif")
gridrect = grid.get_rect()
booms = []
boomimg = pygame.image.load("images/boom.gif")
shield = pygame.image.load("images/shield.gif")

players = 0
teams = []

imageMap = {-1: -1, 0: 0, 1: 1, 2: 2, 3: 3, "D": 0, "K": 1, "B": 3, "A": 2}
shipImages = []
shotImages = []
delay = 10

class Button:
    def __init__(self, text, x, y, width, height, teamID = -1):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.teamID = teamID

    def draw(self):
        if self.teamID < 0:
            pygame.draw.rect(screen, (0, 128, 0), (info.left + self.x, info.top + self.y, self.width, self.height))
            text = font20.render(self.text, 1,  (0, 0, 0))
            screen.blit(text, (info.left + self.x + self.width//2 - text.get_width()//2,
                               info.top + self.y + self.height//2 - text.get_height()//2))
        else:
            pygame.draw.rect(screen, (0, 128, 0), (info.left + self.x, info.top + self.y, self.width, self.height))
            pygame.draw.rect(screen, (0, 0, 0), (info.left + self.x + 5, info.top + self.y + 5, self.width - 10, size + 5))
            screen.blit(pygame.image.load("images/ship" + self.text[0] + "00.gif"),
                        (info.left + self.x + 25, info.top + self.y + 10, size, size))
            text = font20.render(self.text, 1,  (0, 0, 0))
            screen.blit(text, (info.left + self.x + (size + 50)//2 - text.get_width()//2,
                               info.top + self.y + self.height - text.get_height()))

    def click(self, pos):
        x1 = pos[0] - info.left
        y1 = pos[1] - info.top
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


def ready_set_go():

    for team in teams:
        for ship in team.ships:
            ship.speed = 0
            ship.shot = False

    draw_screen()

    screen.blit(pygame.Surface((300, 100)), (info.left + 30, info.top + 190))
    screen.blit(font40.render("Ready", True, (180, 0, 0)), (info.left + 160, info.top + 190))
    pygame.display.update((info.left + 30, info.top + 140, 400, 150))

    now = time.time()
    while time.time() - now < 1:
        pass

    screen.blit(pygame.Surface((300, 100)), (info.left + 80, info.top + 190))
    screen.blit(font40.render("Set", True, (180, 0, 0)), (info.left + 180, info.top + 190))
    pygame.display.update((info.left + 80, info.top + 160, 300, 150))

    now = time.time()
    while time.time() - now < 1:
        pass

    screen.blit(pygame.Surface((300, 100)), (info.left + 80, info.top + 190))
    screen.blit(font40.render("Go!", True, (180, 0, 0)), (info.left + 180, info.top + 190))
    pygame.display.update((info.left + 80, info.top + 160, 300, 150))


def load_images():
    # image = shipImages[team][level][speed]
    global shipImages
    global shotImages
    shipImages = []
    shotImages = []

    for team in range(4):
        lvl_images = []
        for lvl in range(4):
            spd_images = []
            for spd in range(4):
                spd_images.append(pygame.image.load("images/ship" + str(imageMap[team]) + str(lvl) + str(spd) + ".gif"))
            lvl_images.append(spd_images)
        shipImages.append(lvl_images)
        shotImages.append(pygame.image.load("images/shot" + str(team) + ".gif"))
    if imageMap[-1] == -1:
        shipImages[teams[0].teamID][0][0] = pygame.image.load("images/ship" + str(teams[0].teamID) + "00.gif")
        shipImages[teams[0].teamID][0][3] = pygame.image.load("images/ship" + str(teams[0].teamID) + "03.gif")
        shotImages[teams[0].teamID] = pygame.image.load("images/shot" + str(teams[0].teamID) + ".gif")
    else:
        # simple swap : todo allow for all team selections
        myID = teams[0].teamID
        shipImages[myID][0][0] = pygame.image.load("images/ship" + str(imageMap[imageMap[-1]]) + "00.gif")
        shipImages[myID][0][3] = pygame.image.load("images/ship" + str(imageMap[imageMap[-1]]) + "03.gif")
        shotImages[myID] = pygame.image.load("images/shot" + str(imageMap[imageMap[-1]]) + ".gif")
        shipImages[imageMap[imageMap[-1]]][0][0] = pygame.image.load("images/ship" + str(myID) + "00.gif")
        shipImages[imageMap[imageMap[-1]]][0][3] = pygame.image.load("images/ship" + str(myID) + "03.gif")
        shotImages[imageMap[imageMap[-1]]] = pygame.image.load("images/shot" + str(myID) + ".gif")


def show_lives():
    if players == 1:
        lives = teams[0].lives
        lifeleft = info.left + 116
        lifetop = info.top + 150
        for life in range(lives):
            screen.blit(shipImages[int(0 if imageMap[-1] == -1 else imageMap[-1])][0][0], (lifeleft, lifetop, size, size))
            lifeleft = lifeleft + size * 1.2
            if life in (2, 4):
                lifeleft = info.left + 116
                lifetop = lifetop + size
    else:
        # screen.blit(pygame.Surface((450, 200)), (info.left, info.top))
        for team in range(4 if players > 2 else 2):
            if teams[team].lives == 0:
                screen.blit(font20.render("Spectating", True, (180, 0, 0)),
                            (info.left + 40 + 260 * (teams[team].teamID % 2),
                             info.top + (110 if team > 1 else 50)))
            for life in range(teams[team].lives):
                show_life(teams[team], life)

def show_life(team, life):
    lifeleft = info.left + 30 + 50 * life + (info.width - 90 - 100 * life) * (team.teamID % 2)
    lifetop = info.top + (110 if team.teamID > 1 else 50)
    screen.blit(shipImages[team.teamID][0][0], (lifeleft, lifetop, size, size))
    return pygame.Rect(lifeleft, lifetop, size, size)


def draw_fuel_bar(fuel, x=info.left + 32, y=info.top + 149):
    if fuel < 0:
        fuel = 0
    bar_length = 23
    bar_height = 158
    fill = bar_height * fuel // 10000
    fill_rect = pygame.Rect(x, y + bar_height - fill,  bar_length, fill)
    colour = [0, 204, 0] if fuel >= 5000 else [255, 128, 0] if fuel >= 2500 else [255, 0, 0]
    pygame.draw.rect(screen, [0, 128, 0], pygame.Rect(x - 5, y - 5, bar_length + 10, bar_height + 10))
    pygame.draw.rect(screen, [0, 0, 0], pygame.Rect(x, y, bar_length, bar_height))
    pygame.draw.rect(screen, colour, fill_rect)


def game_over(team):

    if team is None:
        return
    screen.blit(pygame.Surface((200, 100)), (info.left + 280, info.top))
    screen.blit(pygame.Surface((500, 500)), (info.left, info.top + 40))
    screen.blit(font40.render("Game Over", True, (180, 0, 0)), (info.left + 120, info.top + 90))
    pygame.display.flip()

    if players == 1:
        try:
            with open("singles.dat", "rb") as file:
                scores = pickle.load(file)
                file.close()
        except FileNotFoundError:
            scores = [["Derek", 100, 5], ["Pete", 80, 4], ["Mark", 60, 3], ["Mike", 40, 2], ["Jack", 20, 1]]
            # scores = [["Derek", 10000, 5], ["Pete", 8000, 4], ["Mark", 6000, 3], ["Mike", 4000, 2], ["Jack", 2000, 1]]

        player_name = ""
        for i in range(5):
            if team.score > scores[i][1]:
                screen.blit(font20.render("You got a High Score!", True, (180, 0, 0)), (info.left + 100, info.top + 190))
                screen.blit(font20.render("Please enter your name:", True, (180, 0, 0)), (info.left + 100, info.top + 240))
                while True:
                    pygame.display.update((info.left, info.top, info.width, info.height))
                    while True:
                        event = pygame.event.poll()
                        if event.type == KEYDOWN:
                            inkey = event.key
                            break
                    if inkey == K_BACKSPACE:
                        player_name = player_name[:len(player_name) - 1]
                    elif inkey == K_RETURN or inkey == K_KP_ENTER:
                        break
                    elif inkey <= 127:
                        player_name = player_name + chr(inkey - (32 if len(player_name) == 0 else 0))

                    screen.blit(pygame.Surface((200, 50)), (info.left + 80, info.top + 320))
                    screen.blit(font20.render(player_name, True, (180, 0, 0)), (info.left + 80, info.top + 320))

                scores.insert(i, [str(player_name), team.score, team.level])
                scores.pop()
                break

        screen.blit(pygame.Surface((150, 100)), (info.left + 160, info.top))
        screen.blit(pygame.Surface((450, 445)), (info.left, info.top))  # top + 40
        screen.blit(font40.render("High Scores", True, (180, 0, 0)), (info.left + 100, info.top + 70))
        screen.blit(font20.render("Player      Level    Score", True, (180, 0, 0)), (info.left + 80, info.top + 130))
        screen.blit(font20.render("Press heRe to restart", True, (180, 0, 0)), (info.left + 100, info.top + 400))

        for i in range(5):
            colour = (0, 128, 0) if scores[i][1] == team.score and scores[i][0] == player_name else (180, 0, 0)
            screen.blit(font20.render('{:<15}'.format(scores[i][0]), True, colour),
                        (info.left + 80, info.top + 160 + i * 25))
            screen.blit(font20.render('{:>7}'.format(str(scores[i][2])), True, colour),
                        (info.left + 165, info.top + 160 + i * 25))
            screen.blit(font20.render('{:>14}'.format(str(scores[i][1])), True, colour),
                        (info.left + 210, info.top + 160 + i * 25))
        with open("singles.dat", "wb") as file:
            pickle.dump(scores, file)
            file.close()
    else:
        screen.blit(font20.render("The winner is ", True, (180, 0, 0)), (info.left + 115, info.top + 190))
        screen.blit(shipImages[team.teamID][0][0], (info.left + 280, info.top + 185, size, size))
        if teams[0].teamID == team.teamID:
            screen.blit(font20.render("Congratulations!", True, (180, 0, 0)), (info.left + 120, info.top + 240))
            s_boom[0].play()
        else:
            screen.blit(font20.render("Better luck next time", True, (180, 0, 0)), (info.left + 100, info.top + 240))
        with open("multi" + str(players) + ".dat", "wb") as file:
            pickle.dump([time.time(), players, team], file)
            file.close()

    screen.blit(font20.render("Press any key", True, (180, 0, 0)), (info.left + 130, info.top + 320))
    screen.blit(font20.render("to return to the main menu", True, (180, 0, 0)), (info.left + 70, info.top + 350))
    pygame.display.flip()


def round_over(victor):

    screen.blit(pygame.Surface((490, 450)), (info.left, info.top))
    result = "Victory!" if victor is teams[0] else "Defeat!"
    screen.blit(font40.render(result, True, (180, 0, 0)), (info.left + 160, info.top + 90))

    victor.score += 1
    screen.blit(font20.render("Your score", True, (180, 0, 0)), (info.left + 80, info.top + 190))
    screen.blit(font20.render("Their score", True, (180, 0, 0)), (info.left + 280, info.top + 190))
    screen.blit(font20.render('{:<15}'.format(teams[0].score), True, (180, 0, 0)), (info.left + 130, info.top + 240))
    screen.blit(font20.render('{:<15}'.format(teams[1].score), True, (180, 0, 0)), (info.left + 330, info.top + 240))

    screen.blit(font20.render("Press R to Ready-up", True, (180, 0, 0)), (info.left + 100, info.top + 340))
    pygame.display.flip()


# determines ship.hit
def crash(ship):
    hitter = -1
    shipRect = ship.orient(teams[0].orientation)

    for target in ship.team.enemy:
        # targetRect = target.orient(ship.team.orientation)
        targetRect = target.orient(teams[0].orientation)

        # did two ships collide
        if hit(targetRect, shipRect, .7) and not ship.inert and not target.inert:
            booms.append(shipRect.copy())
            booms.append(targetRect.copy())
            if players > 1:
                booms.append(show_life(ship.team, ship.team.lives - 1))
                booms.append(show_life(target.team, target.team.lives - 1))
            s_boom[0].play()
            ship.hit = True
            target.hit = True
            hitter = target.team.teamID

        # did ship's shot hit enemy ship?
        if ship.shot:
            shipShotRect = ship.orient(teams[0].orientation, True)
            if hit(targetRect, shipShotRect, .7) and not target.inert:
                target.hit = True
                ship.shot = False
                booms.append(targetRect.copy())
                if players > 1:
                    booms.append(show_life(target.team, target.team.lives - 1))
                if target.canTakeAHit:
                    s_bzzt.play()
                else:
                    s_boom[0 if players > 1 else len(ship.team.enemy)-1].play()
                hitter = ship.team.teamID
            if ship.shotRect.top + size // 2 < gridtop or ship.shotRect.top + size // 2 > gridtop + 15 * size or \
                    ship.shotRect.left + size // 2 < gridleft or ship.shotRect.left + size // 2 > gridleft + size * 15:
                # hit a wall
                ship.shot = False
                s_side.play()

        # did enemy shot hit ship?
        if target.shot:
            targetShotRect = target.orient(teams[0].orientation, True)
            if hit(targetShotRect, shipRect, .7) and not ship.inert:
                ship.hit = True
                target.shot = False
                booms.append(shipRect.copy())
                if players > 1:
                    booms.append(show_life(ship.team, ship.team.lives - 1))
                s_boom[0].play()
                hitter = target.team.teamID
            if target.shotRect.top + size // 2 < gridtop or target.shotRect.left + size // 2 < gridleft or \
                    target.shotRect.top + size // 2 > gridtop + 15 * size or \
                    target.shotRect.left + size // 2 > gridleft + size * 15:
                # hit a wall
                print("enemy shot hit a wall")
                s_side.play()
                target.shot = False

    return hitter


def show_booms():
    for boom in booms:
        screen.blit(pygame.transform.rotate(pygame.transform.scale(boomimg, (boom.width, boom.height)),
                                            boom.width * -90), boom)
        boom.height -= min(boom.height, (1 + size - boom.height))
        boom.top += (boom.width - boom.height) // 2
        boom.left += (boom.width - boom.height) // 2
        boom.width = boom.height
        if boom.width <= 0:
            booms.remove(boom)


def draw_screen():
    screen.blit(grid, gridrect)
    screen.blit(pygame.Surface((info.width, info.height)), (info.left, info.top))
    show_booms()

    if players == 1:
        screen.blit(info_1p, info)
        screen.blit(font40.render('{:<10}'.format("Score"), True, (0, 150, 0)), (info.left, info.top + 5))
        screen.blit(font40.render('{:>10}'.format(str(teams[0].score)), True, (0, 150, 0)),
                    (info.left + 60, info.top + 5))
        screen.blit(font40.render('{:<10}'.format("Level"), True, (0, 150, 0)), (info.left, info.top + 45))
        screen.blit(font40.render('{:>10}'.format(str(teams[0].level)), True, (0, 150, 0)),
                    (info.left + 60, info.top + 45))

        screen.blit(font40.render('{:<10}'.format("Fuel"), True, (0, 150, 0)), (info.left, info.top + 100))
        draw_fuel_bar(teams[0].ships[0].fuel)
        # pygame.draw.polygon(screen, (0, 0, 0), ((130, 840), (130, 700), (270, 700)))
        screen.blit(font40.render('{:<10}'.format("Ships"), True, (0, 150, 0)), (info.left + 116, info.top + 100))
    elif players > 1:
        screen.blit(font40.render("Go!", True, (180, 0, 0)), (info.left + 180, info.top + 190))

    if len(teams) > 0:
        show_lives()

    for team in teams:
        for ship in team.ships:
            rotation = (ship.direction + team.orientation + teams[0].orientation) * -90
            if not ship.inert:
                image = shipImages[imageMap[team.teamID]][ship.rank][ship.speed]
                screen.blit(pygame.transform.rotate(image, rotation), ship.orient(teams[0].orientation))
                if ship.canTakeAHit:
                    screen.blit(shield, ship.orient(teams[0].orientation))
                if ship.canShoot and not ship.shot:
                    image = shotImages[imageMap[team.teamID]]
                    screen.blit(pygame.transform.rotate(image, rotation), ship.orient(teams[0].orientation))
            if ship.shot:
                image = shotImages[imageMap[team.teamID]]
                rotation = (ship.shotDirection + team.orientation + teams[0].orientation) * -90
                screen.blit(pygame.transform.rotate(image, rotation), ship.orient(teams[0].orientation, True))

    pygame.display.flip()


def no_shots():
    for team in teams:
        if team.ships[0].shot:
            return False
    return True


def update(network):
    # send local teams' deets
    if players == 3:
        network.send(teams[2].deets)
    deets = network.send(teams[0].deets)

    # update remote teams' deets
    if players == 3:
        teams[1].update(deets[1 - teams[0].teamID])
        teams[3].update(deets[3 - teams[0].teamID])
    elif players == 4:
        for t in range(3):
            try:
                teams[t+1].update(deets[teams[t+1].teamID])
            except:
                pass


    return deets


def pvp():
    global teams

    network = Network(players)
    clock = pygame.time.Clock()
    key = 0
    myID = int(network.get_teamID())
    if myID is None:
        print("No server")
        screen.blit(pygame.Surface((info.width, info.height)), (info.left, info.top))
        screen.blit(font20.render("Server unavailable", True, (180, 0, 0)), (info.left + 110, info.top + 140))
        screen.blit(font20.render("Please select Single Player option", True, (180, 0, 0)), (info.left + 30, info.top + 190))
        screen.blit(font20.render("Press any key", True, (180, 0, 0)), (info.left + 125, info.top + 320))
        screen.blit(font20.render("to return to the main menu", True, (180, 0, 0)), (info.left + 65, info.top + 370))
        pygame.display.update(info)
        return
    teams = [Team(myID)]  # this thread's team
    pygame.display.set_caption("PyForce - P" + str(myID))

    # screen.blit(grid, gridrect)
    screen.blit(pygame.Surface((490, 450)), (info.left, info.top))
    screen.blit(font20.render("Waiting for opponent....", True, (180, 0, 0)), (info.left + 80, info.top + 190))
    pygame.display.update(info)

    # wait for opponent(s)
    while True:
        data = network.send(teams[0].deets)
        users = players if players != 3 else 2
        if len(data) == users:  # enough players have joined
            break

    if players == 3:
        teams.append(Team(1 - myID, 2))  # remote player
        # bots (teams[2&3] are automated)
        teams.append(Team(myID + 2, 0, gridleft + 14 * size, gridtop + 4 * size, 3, 7))
        network.send(teams[2].deets)  # controlled by this thread
        teams[2].ships[0].target = teams[0].ships[0]  # targeting this player
        teams.append(Team(3 - myID, 2, gridleft + 14 * size, gridtop + 4 * size, 3, 7))  # controlled by remote thread
        teams[2].ships[0].canTakeAHit = False
        teams[3].ships[0].canTakeAHit = False
    elif players == 4:
        teams.append(Team((myID + 1) % 4, 3))
        teams.append(Team((myID + 2) % 4, 2))
        teams.append(Team((myID + 3) % 4, 1))

    screen.blit(font20.render("Setting up teams....", True, (180, 0, 0)), (info.left + 85, info.top + 290))
    pygame.display.update((info.left + 80, info.top + 240, 400, 200))
    time.sleep(1)

    deets = network.send(teams[0].deets)

    #  Assign enemy targets, get all deets
    for teamA in teams:
        teamA.deets = deets[teamA.teamID]
        for teamB in teams:
            if teamA.teamID != teamB.teamID:
                for ship in teamB.ships:
                    teamA.enemy.append(ship)

    load_images()
    draw_screen()
    ship_hit = False

    # and we're off
    ready_set_go()

    # game loop
    while True:

        # move & send results
        teams[0].ships[0].move(key)  # move self
        # teams[1].ships[0].move(0)  # move remote ship (momentum)
        if players >= 3:
            teams[2].ships[0].move(-3 if players == 3 else 0) # move [assigned] drone (momentum[autopilot])
            # teams[3].ships[0].move(0)  # move remote drone (momentum)

        update(network)

        for team in teams:

            # check for collisions
            crash(team.ships[0])

            if team.ships[0].hit:
                team.ships[0].update()
                ship_hit = True
                team.lives -= 1
                team.ships[0].inert = True
                if team.teamID in {myID, myID + 2}:
                    update(network)  # send the bad news
                team.ships[0].hit = False
                team.ships[0].update()

        if ship_hit:
            # Make sure all threads are current
            while True:
                deets = update(network)
                for deet in deets:
                    if not deets[deet].current:
                        break
                else:
                    ship_hit = False
                    break

        teams_left = 0
        winner = None

        for team in teams:

            if team.lives > 0:
                teams_left += 1
                winner = team  # potential winner, anyway

                # if team's ship is inert, does it get revived?
                if team.ships[0].inert and not team.ships[0].shot:
                    if team.teamID in (myID, myID + 2):  # this thread
                        team.ships[0].revive(5)
                    else:
                        team.ships[0].inert = False

        # Game over?
        if teams_left <= 1:
            # allow for explosion to complete
            update(network)
            delay = 10  # if len(booms) > 0 else 0
            while delay:
                time.sleep(1.0 / 50)
                draw_screen()
                delay -= 1
            return winner

        update(network)
        draw_screen()

        if key == K_SPACE:
            key = 0  # don't keep shooting

        # check for quit event, log keydown
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()  # time.sleep(10)
            if event.type == pygame.KEYDOWN:
                key = event.key

        draw_screen()
        clock.tick(50)
        #  time.sleep(1.0 / 50)


def pve():
    random.seed()

    global teams
    teams = [Team(0), Team(1, rank=1)]  # player, drone fleet
    ship0 = teams[0].ships[0]
    teams[1].ships = []
    teams[1].target = ship0
    load_images()

    levelable = True
    key = 0
    play = True  # Game play on / off

    while True:

        # wait for keypress if game paused
        while not play:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    play = True
                    key = event.key

        # set up the [next] level
        if len(teams[1].ships) == 0 and len(booms) == 0:

            # player's ship
            ship0.reset(gridleft + 14 * size, gridtop + 14 * size, 0)
            teams[0].score = teams[0].score + 100 * teams[0].level + ship0.fuel // 10 * teams[0].level
            teams[0].level += 1
            ship0.fuel = 10000
            play = False
            key = 0

            # drone fleet
            for i in range(8):
                teams[1].ships.append(Ship(teams[1], gridleft + i * 2 * size, gridtop, 2, teams[0].level, teams[0].ships[0]))
            teams[0].enemy = teams[1].ships

        draw_screen()

        # player action
        if not ship0.hit:
            ship0.move(key)
            ship0.fuel -= ship0.speed
        else:
            # lose a life
            ship0.team.lives -= 0 if ship0.inert else 1
            ship0.inert = True
            ship0.move(0)  # shot must still move

            # allow shots to run course
            for drone in teams[0].enemy:
                if drone.shot or ship0.shot:
                    break
            else:  # no live shots
                if len(booms) == 0:
                    if ship0.team.lives >= 0:
                        if len(teams[1].ships) != 0:
                            ship0.hit = False
                            ship0.inert = False
                            ship0.fuel = (ship0.fuel + 10000) // 2
                            ship0.speed = 0
                            ship0.revive(3)
                            draw_screen()
                            play = False
                    else:
                        draw_screen()
                        return teams[0]
                        # ship0.hit = False

        # don't keep shooting
        if key == K_SPACE:
            key = 0

        # drone fleet action
        for drone in teams[1].ships:
            drone.move(-drone.speed)
            if drone.hit:
                drone.hit = False
                if drone.canTakeAHit:
                    drone.canTakeAHit = False
                else:
                    drone.inert = True
                    teams[0].score += 100  # score!
            if drone.inert and not drone.shot:
                teams[1].ships.remove(drone)

        # check for collisions
        crash(ship0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = event.key

        # change level
        if key == K_l and ship0.lives > 0 and levelable:
            teams[0].level += 1
            if teams[0].level == 20:
                levelable = False
            teams[1].ships = []
            for i in range(8):
                #teams[1].ships.append(Drone(teams[1], teams[0].level, gridleft + i * 2 * size, gridtop))
                teams[1].ships.append(Ship(teams[1], gridleft + i * 2 * size, gridtop, 2, teams[0].level, teams[0].ships[0]))
            teams[0].enemy = teams[1].ships
            ship0.reset(gridleft + 14 * size, gridtop + 14 * size, 0)
            ship0.fuel = 10000
            play = False
            draw_screen()

        # reset game
        if key == K_r:
            teams[0].level = 0
            teams[1].ships = []
            teams[0].score = 0
            ship0.reset(gridleft + 14 * size, gridtop + 14 * size, 0)
            ship0.team.lives = 3
            levelable = True
            # teams[1].ships[1] = ship0

        time.sleep(1.0 / 50)


def select_team(btn):
    screen.blit(pygame.Surface((500, 40)), (info.left, info.top + 430))
    text = font40.render("*", 1, (0, 128, 0))
    screen.blit(text, (info.left + btn.x + btn.width // 2 - 13, info.top + btn.y + btn.height + 10))
    pygame.display.update((info.left, info.top + 430, 500, 40))
    imageMap[-1] = btn.text[0]


def main():
    global players

    while True:

        buttons = [Button("Single Player", 125, 60, 180, 50),
                   Button("Head to Head", 125, 120, 180, 50),
                   Button("Battle Royale (fill)", 75, 180, 280, 50),
                   Button("Battle Royale (no fill)", 75, 240, 280, 50),
                   Button("Derek", 25, 350, size + 50, size + 40, 0),
                   Button("Krista", 125, 350, size + 50, size + 40, 1),
                   Button("Avery", 325, 350, size + 50, size + 40, 2),
                   Button("Ben", 225, 350, size + 50, size + 40, 3)]

        draw_screen()

        screen.blit(pygame.Surface((info.width, info.height)), (info.left, info.top))
        text = font40.render("Select Game Mode:", True, (0, 128, 0))
        screen.blit(text, (info.width / 2 - text.get_width() / 2, info.top + 10))
        text = font40.render("Select Team:", True, (0, 128, 0))
        screen.blit(text, (info.width / 2 - text.get_width() / 2, info.top + 300))
        for button in buttons:
            button.draw()
        pygame.display.update(info)

        # indicate that a team has been selected
        if imageMap[-1] != -1:
            text = font40.render("*", 1, (0, 128, 0))
            btn = buttons[int(imageMap[imageMap[-1]] + 4)]
            screen.blit(text, (info.left + btn.x + btn.width // 2 - 13, info.top + btn.y + btn.height + 10))
            pygame.display.update((info.left, info.top + 430, 500, 40))

        waiting_for_user = True
        while waiting_for_user:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = pygame.mouse.get_pos()
                    for button in buttons:
                        if button.click(click_pos):
                            if button.text == "Derek":
                                select_team(buttons[4])
                            elif button.text == "Krista":
                                select_team(buttons[5])
                            elif button.text == "Ben":
                                select_team(buttons[7])
                            elif button.text == "Avery":
                                select_team(buttons[6])
                            else:
                                waiting_for_user = False
                                user_input = button.text

        if user_input == "Single Player":
            players = 1
            game_over(pve())
        elif user_input == "Head to Head":
            players = 2
            game_over(pvp())
        elif user_input == "Battle Royale (fill)":
            players = 3
            game_over(pvp())
        elif user_input == "Battle Royale (no fill)":
            players = 4
            game_over(pvp())
        else:
            pass

        time.sleep(1)

        players = 0
        t = time.time()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    t -= 220
            if time.time() - t > 220:
                break


if __name__ == "__main__":
    main()
