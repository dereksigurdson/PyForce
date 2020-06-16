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

import network
from team import Team, Ship, hit, Deets
from network import Network
from config import size, border, gridleft, gridtop
from pygame.locals import *

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

screensize = screenwidth, screenheight = 950, 560  # 490, 1000
screen = pygame.display.set_mode(screensize)
pygame.display.set_caption("PyForce")
pygame.display.set_icon(pygame.image.load("images/ship003.gif"))
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
s_tada = pygame.mixer.Sound("sounds/tada.wav")

grid = pygame.image.load("images/grid.gif")
gridc = pygame.image.load("images/gridc.gif")
chess = False
info_1p = pygame.image.load("images/info_1p.gif")
gridrect = grid.get_rect()
booms = []
boomimg = pygame.image.load("images/boom.gif")
shield = pygame.image.load("images/shield.gif")
shieldc = pygame.image.load("images/shieldc.gif")

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
        self.selected = False

    def draw(self):
        pygame.draw.rect(screen, (0, 128, 0), (info.left + self.x, info.top + self.y, self.width, self.height))
        if self.selected:
            pygame.draw.rect(screen, (180, 0, 0), (info.left + self.x, info.top + self.y, 3, self.height))
            pygame.draw.rect(screen, (180, 0, 0), (info.left + self.x, info.top + self.y, self.width, 3))
            pygame.draw.rect(screen, (180, 0, 0),
                             (info.left + self.x + self.width - 3, info.top + self.y, 3, self.height))
            pygame.draw.rect(screen, (180, 0, 0),
                             (info.left + self.x, info.top + self.y + self.height - 3, self.width, 3))

        if self.teamID < 0:
            text = font20.render(self.text, 1,  (0, 0, 0))
            screen.blit(text, (info.left + self.x + self.width//2 - text.get_width()//2,
                               info.top + self.y + self.height//2 - text.get_height()//2))
        else:
            pygame.draw.rect(screen, (0, 0, 0), (info.left + self.x + 5, info.top + self.y + 5, self.width - 10, size + 5))
            screen.blit(pygame.image.load("images/ship" + self.text[0] + "00.gif"),
                        (info.left + self.x + 25, info.top + self.y + 10, size, size))
            text = font20.render(self.text, 1,  (0, 0, 0))
            screen.blit(text, (info.left + self.x + (size + 50)//2 - text.get_width()//2,
                               info.top + self.y + self.height - text.get_height() - 3))

    def click(self, pos):
        x1 = pos[0] - info.left
        y1 = pos[1] - info.top
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            self.selected = True
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
    text = font40.render("Ready", True, (180, 0, 0))
    screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 190))
    pygame.display.update((info.left + 30, info.top + 140, 400, 150))

    now = time.time()
    while time.time() - now < 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    screen.blit(pygame.Surface((300, 100)), (info.left + 80, info.top + 190))
    text = font40.render("Set", True, (180, 0, 0))
    screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 190))
    pygame.display.update((info.left + 80, info.top + 160, 300, 150))

    now = time.time()
    while time.time() - now < 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    screen.blit(pygame.Surface((300, 100)), (info.left + 80, info.top + 190))
    text = font40.render("Go!", True, (180, 0, 0))
    screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 190))
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
                if chess:
                    spd_images.append(pygame.image.load("images/shipc" + str(imageMap[team]) + str(lvl) + "0.gif"))
                else:
                    spd_images.append(pygame.image.load("images/ship" + str(imageMap[team]) + str(lvl) + str(spd) + ".gif"))
            lvl_images.append(spd_images)
        shipImages.append(lvl_images)
        shotImages.append(pygame.image.load("images/shot" + str(team) + ".gif"))
    if imageMap[-1] != -1:
        # simple swap : todo allow for all team selections
        myID = teams[0].teamID
        if chess:
            shipImages[myID][0][0] = pygame.image.load("images/shipc" + str(imageMap[imageMap[-1]]) + "00.gif")
            shipImages[myID][0][3] = pygame.image.load("images/shipc" + str(imageMap[imageMap[-1]]) + "00.gif")
            shipImages[imageMap[imageMap[-1]]][0][0] = pygame.image.load("images/shipc" + str(myID) + "00.gif")
            shipImages[imageMap[imageMap[-1]]][0][3] = pygame.image.load("images/shipc" + str(myID) + "00.gif")
        else:
            shipImages[myID][0][0] = pygame.image.load("images/ship" + str(imageMap[imageMap[-1]]) + "00.gif")
            shipImages[myID][0][3] = pygame.image.load("images/ship" + str(imageMap[imageMap[-1]]) + "03.gif")
            shipImages[imageMap[imageMap[-1]]][0][0] = pygame.image.load("images/ship" + str(myID) + "00.gif")
            shipImages[imageMap[imageMap[-1]]][0][3] = pygame.image.load("images/ship" + str(myID) + "03.gif")
        shotImages[myID] = pygame.image.load("images/shot" + str(imageMap[imageMap[-1]]) + ".gif")
        shotImages[imageMap[imageMap[-1]]] = pygame.image.load("images/shot" + str(myID) + ".gif")


def show_lives():
    if players == 1:
        lives = teams[0].lives
        lifeleft = info.left + 116
        lifetop = info.top + 150
        for life in range(lives):
            screen.blit(shipImages[int(0 if imageMap[-1] == -1 else imageMap[teams[0].teamID])][0][0], (lifeleft, lifetop, size, size))
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
                             info.top + (110 if teams[team].teamID > 1 else 50)))
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
    screen.blit(pygame.Surface((info.width, info.height)), (info.left, info.top))

    if team == "Server not available":
        text = font40.render("Cannot", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 90))
        text = font40.render("Locate", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 130))
        text = font40.render("Server", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 170))
        text = font20.render("Update IP address in config.py", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 280))
        text = font20.render("Click mouse or press any key", True, (0, 128, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 370))
        text = font20.render("to return to the main menu", True, (0, 128, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 400))
        pygame.display.flip()
        return

    if team == "Esc":
        text = font40.render("Until", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 90))
        text = font40.render("Next", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 130))
        text = font40.render("Time", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 170))
        text = font20.render("Click mouse or press any key", True, (0, 128, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 370))
        text = font20.render("to return to the main menu", True, (0, 128, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 400))
        pygame.display.flip()
        return

    if players == 1:
        text = font40.render("Game Over", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 20))
        pygame.display.flip()

        try:
            with open("singles.dat", "rb") as file:
                scores = pickle.load(file)
                file.close()
        except FileNotFoundError:
            scores = [["Derek", 10000, 5], ["Pete", 8000, 4], ["Mark", 6000, 3], ["Mike", 4000, 2], ["Jack", 2000, 1]]
            # scores = [["Derek", 10000, 5], ["Pete", 8000, 4], ["Mark", 6000, 3], ["Mike", 4000, 2], ["Jack", 2000, 1]]

        player_name = ""
        for i in range(5):
            if team.score > scores[i][1]:
                text = font20.render("You got a High Score!", True, (180, 0, 0))
                screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 190))
                text = font20.render("Please enter your name:", True, (180, 0, 0))
                screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 240))
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
        text = font40.render("High Scores", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 70))
        text = font20.render("Player     Level    Score", True, (0, 128, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 130))

        for i in range(5):  # display high scores
            colour = (0, 128, 0) if scores[i][1] == team.score and scores[i][0] == player_name else (180, 0, 0)
            text = font20.render('{:<15}'.format(scores[i][0]), True, colour)
            screen.blit(text, (info.left + 82, info.top + 160 + i * 25))
            text = font20.render('{:>7}'.format(str(scores[i][2])), True, colour)
            screen.blit(text, (info.left + 165, info.top + 160 + i * 25))
            text = font20.render('{:>14}'.format(str(scores[i][1])), True, colour)
            screen.blit(text, (info.left + 208, info.top + 160 + i * 25))
        if team.score < scores[4][1]:  # display player score
            text = font20.render('{:<15}'.format("You"), True, (0, 128, 0))
            screen.blit(text, (info.left + 80, info.top + 165 + 5 * 25))
            text = font20.render('{:>7}'.format(str(team.level)), True, (0, 128, 0))
            screen.blit(text, (info.left + 165, info.top + 165 + 5 * 25))
            text = font20.render('{:>14}'.format(str(team.score)), True, (0, 128, 0))
            screen.blit(text, (info.left + 210, info.top + 165 + 5 * 25))

        with open("singles.dat", "wb") as file:
            pickle.dump(scores, file)
            file.close()
    elif team is None:
        text = font20.render("Tie game!", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 190))
    else:
        text = font40.render("Game Over", True, (180, 0, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 100))
        text = font20.render("The winner is ", True, (180, 0, 0))
        screen.blit(text, (info.left + 115, info.top + 190))
        screen.blit(shipImages[team.teamID][0][0], (info.left + 280, info.top + 185, size, size))
        if teams[0].teamID == team.teamID:
            text = font20.render("Congratulations!", True, (180, 0, 0))
            screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 240))
            s_tada.play()
        else:
            text = font20.render("Better luck next time", True, (180, 0, 0))
            screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 240))
            s_boom[0].play()
        with open("multi" + str(players) + ".dat", "wb") as file:
            pickle.dump([time.time(), players, team], file)
            file.close()

    text = font20.render("Click mouse or press any key", True, (0, 128, 0))
    screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 350))
    text = font20.render("to return to the main menu", True, (0, 128, 0))
    screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 380))
    pygame.display.flip()
    time.sleep(1)


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
            time.sleep(.03)
            hitter = target.team.teamID

        # did ship's shot hit enemy ship?
        if ship.shot:
            shipShotRect = ship.orient(teams[0].orientation, True)
            if hit(targetRect, shipShotRect, .7) and not target.inert:
                target.hit = True
                booms.append(targetRect.copy())
                if players > 1:
                    booms.append(show_life(target.team, target.team.lives - 1))
                #else:  # False negatives error
                ship.shot = False
                time.sleep(.03)
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
                booms.append(shipRect.copy())
                if players > 1:
                    booms.append(show_life(ship.team, ship.team.lives - 1))
                #else:  # False negatives error
                target.shot = False
                time.sleep(.03)
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
    screen.blit(gridc if chess else grid, gridrect)
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
            rotation = 0 if chess else (ship.direction + team.orientation + teams[0].orientation) * -90
            if not ship.inert:
                image = shipImages[imageMap[team.teamID]][ship.rank][min(ship.speed, 3)]
                screen.blit(pygame.transform.rotate(image, rotation), ship.orient(teams[0].orientation))
                if ship.canTakeAHit:
                    screen.blit(shieldc if chess else shield, ship.orient(teams[0].orientation))
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


def update(network, force=False):
    deets = None
    while True:
        # send local teams' deets
        if players == 3:
            network.send(teams[2].deets, force)
        deets = network.send(teams[0].deets, force)
        if deets is not None or not force:
            break

    # update remote teams' deets (if they were retrieved before a timeout)
    if deets is not None:
        if players == 2:
            teams[1].update(deets[1 - teams[0].teamID])
        elif players == 3:
            teams[1].update(deets[1 - teams[0].teamID])
            teams[3].update(deets[3 - teams[0].teamID])
        elif players == 4:
            for t in range(3):
                try:
                    teams[t+1].update(deets[teams[t+1].teamID])
                except:
                    pass
    else:
        if players == 2:
            teams[1].ships[0].move()
        elif players == 3:
            teams[1].ships[0].move()
            teams[3].ships[0].move()
        elif players == 4:
            for t in range(3):
                try:
                    teams[t+1].ships[0].move()
                except:
                    pass



    return deets


def pvp():
    global teams

    network = Network(players)
    if network.get_teamID() == "Server not available":
        return "Server not available"
    clock = pygame.time.Clock()
    key = 0
    myID = int(network.get_teamID())
    if myID is None:
        print("No server")
        screen.blit(pygame.Surface((info.width, info.height)), (info.left, info.top))
        screen.blit(font20.render("Server unavailable", True, (180, 0, 0)), (info.left + 110, info.top + 140))
        screen.blit(font20.render("Please select Single Player option", True, (180, 0, 0)), (info.left + 30, info.top + 190))
        screen.blit(font20.render("Click mouse or press any key", True, (180, 0, 0)), (info.left + 125, info.top + 320))
        screen.blit(font20.render("to return to the main menu", True, (180, 0, 0)), (info.left + 65, info.top + 370))
        pygame.display.update(info)
        return
    teams = [Team(myID)]  # this thread's team
    load_images()
    pygame.display.set_caption("PyForce - P" + str(myID))

    # screen.blit(grid, gridrect)
    # screen.blit(pygame.Surface((490, 450)), (info.left, info.top))
    # text = font20.render("These are your ships:", True, (0, 128, 0))
    # screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 50))
    # screen.blit(shipImages[myID][0][0], (info.left + info.width // 2 - size // 2, info.top + 100, size, size))
    # text = font20.render("Players in the game:", True, (180, 0, 0))
    # screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 190))
    # pygame.display.update(info)


    # wait for opponent(s)
    users = 2 if players == 3 else players
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return "Esc"

        data = network.send(teams[0].deets, True)
        if len(data) >= users:  # enough players have joined
            break
        else:
            screen.blit(pygame.Surface((40, 40)), (info.left + info.width - 110, info.top + 5 + 60 * players + 150))
            screen.blit(font40.render(str(len(data)), True, (180, 0, 0)),
                                      (info.left + info.width - 100, info.top + 5 + 60 * players + 150))
            # text = font40.render(str(len(data)) + " of " + str(users), True, (180, 0, 0))
            # screen.blit(pygame.Surface((info.width, 50)), (info.left, info.top + 230))
            # screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 230))
            #
            # for d in data:
            #     pygame.display.update(screen.blit(shipImages[imageMap[data[d].teamID]][0][0],
            #                                       (info.left + info.width // 2 - 3 * size + 2 * size * data[d].teamID,
            #                                        info.top + 300, size, size)))
            pygame.display.update(info)  # (info.left, info.top + 100, 500, size))
            clock.tick(10)

    screen.blit(font20.render("Setting up teams....", True, (180, 0, 0)), (info.left + 85, info.top + 290))
    pygame.display.update(info)
    #pygame.display.update((info.left + 80, info.top + 240, 400, 200))

    if players == 2:
        teams.append(Team(1 - myID, 2))
    elif players == 3:
        teams.append(Team(1 - myID, 2))  # remote player
        # bot 1 (teams[2] automated by this thread)
        teams.append(Team(myID + 2, 0, gridleft + 14 * size, gridtop + 4 * size, 3, 7))
        teams[2].ships[0].canTakeAHit = False
        teams[2].ships[0].rank = 0
        network.send(teams[2].deets)
        teams[2].ships[0].target = teams[0].ships[0]  # targeting this player
        # bot 2 (teams[3] automated by remote thread)
        teams.append(Team(3 - myID, 2, gridleft + 14 * size, gridtop + 4 * size, 3, 7))
        teams[3].ships[0].canTakeAHit = False
        teams[3].ships[0].rank = 0
    elif players == 4:
        teams.append(Team((myID + 1) % 4, 3))
        teams.append(Team((myID + 2) % 4, 2))
        teams.append(Team((myID + 3) % 4, 1))

    users = 4 if players == 3 else players
    while True:
        deets = network.send(teams[0].deets)
        if len(deets) == users:
            break
        time.sleep(.1)

    #  Assign enemy targets, get all deets
    for teamA in teams:
        teamA.deets = deets[teamA.teamID]
        for teamB in teams:
            if teamA.teamID != teamB.teamID:
                for ship in teamB.ships:
                    teamA.enemy.append(ship)

    draw_screen()
    ship_hit = False

    # and we're off
    ready_set_go()

    # game loop
    while True:

        # move & send results
        teams[0].ships[0].move(key)  # move self
        # teams[1].ships[0].move(0)  # move remote ship (momentum)
        if players == 3:
            teams[2].ships[0].move(-6)  # move assigned drone

        update(network)

        for team in teams:

            # check for collisions
            crash(team.ships[0])

            if team.ships[0].hit:
                ship_hit = True
                team.ships[0].rect.left = -10000 - 1000 * team.teamID
                team.ships[0].update()
                team.lives -= 1
                team.ships[0].inert = True
                if team.teamID == myID or (players == 3 and team.teamID == myID + 2):
                    update(network)  # send the bad news
                team.ships[0].hit = False
                team.ships[0].update()

        if ship_hit:
            # Make sure all threads are current
            t = time.time()
            while True:
                deets = update(network, True)
                for deet in deets:
                    if not deets[deet].current and deets[deet].lives > 0:
                        screen.blit(pygame.Surface((450, 200)), (info.left, info.top + 270))
                        text = font20.render("Player has been hit!", True, (180, 0, 0))
                        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 290))
                        text = font20.render("Must update before continuing...", True, (180, 0, 0))
                        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 320))
                        pygame.display.update(info)
                        if time.time() < t + 1:
                            ship_hit = False
                            break
                        else:
                            screen.blit(pygame.Surface((450, 200)), (info.left, info.top + 270))
                            text = font20.render("Player not responding", True, (180, 0, 0))
                            screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 290))
                            text = font20.render("Sacrifices must be made...", True, (180, 0, 0))
                            screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 320))
                            pygame.display.update(info)
                            time.sleep(.5)
                            ship_hit = False
                            for team in teams:
                                if team.teamID == deets[deet].teamID:
                                    deets[deet].lives -= 3
                                    if deets[deet].lives <= 0:
                                        team.ships[0].inert = True
                                        deets[deet].left = -10000 - 1000 * team.teamID
                                        deets[deet].top = -10000 - 1000 * team.teamID
                                    network.send(deets[deet])
                else:  # All live teams are current
                    break

            draw_screen()

        teams_left = 0
        winner = None

        for team in teams:

            if team.lives > 0:
                teams_left += 1
                winner = team  # potential winner, anyway

                # if team's ship is inert, does it get revived?
                if team.ships[0].inert and not team.ships[0].shot:
                    if team.teamID == myID or (players == 3 and team.teamID == myID + 2):  # this thread
                        team.ships[0].revive(5)
                    else:
                        team.ships[0].inert = False
                        # ready_set_go()

        # Game over?
        if teams_left <= 1:
            # allow for explosion to complete
            update(network)
            delay = 10  # if len(booms) > 0 else 0
            while delay:
                time.sleep(1.0 / 25)
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
        clock.tick(25)
        #  time.sleep(1.0 / 50)


def pve():
    random.seed()

    global teams
    teams = [Team(0), Team(1, rank=1)]  # player, drone fleet
    ship0 = teams[0].ships[0]
    teams[1].ships = []
    teams[1].target = ship0
    load_images()

    clock = pygame.time.Clock()
    levelable = True
    extras = 3
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

        # extra life?
        if teams[0].score > 1000 and extras == 3 or \
            teams[0].score > 10000 and extras == 2 or \
            teams[0].score > 100000 and extras == 1:
            teams[0].lives += 1
            extras -= 1

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

        clock.tick(25)
        #time.sleep(1.0 / 50)


def main():
    global players
    global chess
    global teams

    while True:

        buttons = [Button("Single Player", 118, 60 + 150, 200, 50, -1),
                   Button("Head to Head", 118, 120 + 150, 200, 50, -2),
                   Button("+ Head to Head +", 118, 180 + 150, 200, 50, -3),
                   Button("Free for All", 118, 240 + 150, 200, 50, -4),
                   Button("Derek", 29, 70, size + 50, size + 40, 0),
                   Button("Krista", 129, 70, size + 50, size + 40, 1),
                   Button("Avery", 329, 70, size + 50, size + 40, 2),
                   Button("Ben", 229, 70, size + 50, size + 40, 3)]

        draw_screen()

        screen.blit(pygame.Surface((info.width, info.height)), (info.left, info.top))
        text = font40.render("Select Game Mode:", True, (0, 128, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 160))
        text = font40.render("Select Team:", True, (0, 128, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 10))
        text = font20.render("(optional)", True, (0, 128, 0))
        screen.blit(text, (info.left + info.width // 2 - text.get_width() // 2, info.top + 45))

        text = font20.render("Players Required:", True, (0, 128, 0))
        screen.blit(pygame.transform.rotate(text, 90), (info.left + 20, info.top + 70 + 150))

        screen.blit(font40.render("1", True, (0, 128, 0)), (info.left + 60, info.top + 65 + 150))
        screen.blit(font40.render("2", True, (0, 128, 0)), (info.left + 60, info.top + 125 + 150))
        screen.blit(font40.render("2", True, (0, 128, 0)), (info.left + 60, info.top + 185 + 150))
        screen.blit(font40.render("4", True, (0, 128, 0)), (info.left + 60, info.top + 245 + 150))

        text = font20.render("Players Registered:", True, (0, 128, 0))
        screen.blit(pygame.transform.rotate(text, -90), (info.left + info.width - 60, info.top + 70 + 150))

        screen.blit(font40.render("0", True, (0, 128, 0)), (info.left + info.width - 100, info.top + 65 + 150))
        screen.blit(font40.render("0", True, (0, 128, 0)), (info.left + info.width - 100, info.top + 125 + 150))
        screen.blit(font40.render("0", True, (0, 128, 0)), (info.left + info.width - 100, info.top + 185 + 150))
        screen.blit(font40.render("0", True, (0, 128, 0)), (info.left + info.width - 100, info.top + 245 + 150))

        for button in buttons:
            button.draw()
        pygame.display.update(info)

        waiting_for_user = True
        while waiting_for_user:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_c:
                        chess = True
                        screen.blit(gridc, gridrect)
                    else:
                        chess = False
                        screen.blit(grid, gridrect)

                    pygame.display.update(pygame.Rect(0,0,info.left, gridrect.height))

                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = pygame.mouse.get_pos()
                    for button in buttons:
                        if button.click(click_pos):
                            for btn in buttons:
                                btn.selected = btn.teamID == button.teamID
                                btn.draw()
                            if button.teamID >= 0:
                                imageMap[-1] = imageMap[button.text[0]]
                            else:
                                waiting_for_user = False
                                break
                    pygame.display.update((info.left, info.top + 60, 500, 90))

        players = button.teamID * -1
        if button.text == "Single Player":
            game_over(pve())
        else:
            game_over(pvp())

        teams = []
        players = 0
        t = time.time()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    t -= 220
            if time.time() - t > 220:
                break


if __name__ == "__main__":
    main()
