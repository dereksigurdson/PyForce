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
import copy

from pygame.locals import *

#import os
#os.chdir("c:\\2020\\Python\\Projects\\PyForce27")

size = 30
border = 5
score = [0, 0]
level = 0
lives = [3,3]
screensize = screenwidth, screenheight = 460, 1000
screen = pygame.display.set_mode(screensize)
gridpos = gridleft, gridtop = 5, 91
pygame.display.set_caption("PyForce")
play = False  # Game play on / off
key = 0

pygame.init()
pygame.font.init()
font20 = pygame.font.Font("consolas.ttf", 20)
font40 = pygame.font.Font("consolas.ttf", 40)

grid = pygame.image.load("grid.gif")
gridrect = grid.get_rect()
sploady1 = pygame.image.load("sploady1.gif")
life = pygame.image.load("ship1100.gif")
liferect = life.get_rect()
lifeleft = 136
liferect.left = lifeleft


ships = []
drones = []

def show_lives(count):
    liferect.top = 710 if count < 4 else 745 if count < 6 else 780
    if count != 0: screen.blit(life, liferect)
    liferect.left = liferect.left + size * 1.2 if count not in (4,6) else lifeleft
    if count > 1:
        show_lives(count - 1)
    else:
        liferect.left = lifeleft


def draw_fuel_bar(f, x=47, y=709):
    if f < 0:
        f = 0
    bar_length = 23
    bar_height = 158
    fill = bar_height * f // 10000
    fill_rect = pygame.Rect(x, y + bar_height - fill,  bar_length, fill)
    colour = [0, 204, 0] if f >= 5000 else [255, 128, 0] if f >= 2500 else [255, 0, 0]
    pygame.draw.rect(screen, colour, fill_rect)


class Ship:
    # Player ship
    def __init__(self, left, top, direction, speed, team=1):
        self.direction = direction
        self.speed = speed
        self.team = team
        self.shot = False
        self.shotSpeed = 5
        self.hit = False
        self.inert = False  # so bullet persists
        self.images = []
        lvl=1
        self.images = []
        self.shots = []
        for dir in range(4):
            speedImages=[]
            for spd in range(4):
                speedImages.append(pygame.image.load("ship" + str(team) +  str(lvl) +  str(dir) +  str(spd) + ".gif"))
            self.images.append(speedImages)
            self.shots.append(pygame.image.load("shot" + str(team) +  str(dir) + ".gif"))
        self.image = self.images[0][0]
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left

    def move(self, key=0):
        self.image = self.images[self.direction][self.speed]
        screen.blit(self.image, self.rect)
        if ((self.rect.top - gridtop) / 2) % size == 0:  # allow east-west
            if key in [K_LEFT, K_4, K_a]:
                # self.speed = 3 #min(self.speed+1, 3)
                self.direction = 3
            elif key in [K_RIGHT, K_6, K_d]:
                # self.speed = 3 #min(self.speed+1, 3)
                self.direction = 1
        if ((self.rect.left - gridleft) / 2) % size == 0:  # allow north-south
            if key in [K_UP, K_8, K_w]:
                # self.speed = 3 #min(self.speed+1, 3)
                self.direction = 0
            elif key in [K_DOWN, K_2, K_s]:
                # self.speed = 3 #min(self.speed+1, 3)
                self.direction = 2
        if key in [K_RCTRL, K_5]:
            self.speed = 0
        if key in [K_LEFT, K_4, K_a, K_RIGHT, K_6, K_d, K_UP, K_8, K_w, K_DOWN, K_2, K_s]: self.speed = 3

        if key in [K_SPACE] or self.shot:
            self.shoot()

        # Move as far as border
        if self.direction == 0:
            self.rect.top = max(self.rect.top - self.speed, gridtop)
        elif self.direction == 1:
            self.rect.left = min(self.rect.left + self.speed, gridleft + 14 * size)
        elif self.direction == 2:
            self.rect.top = min(self.rect.top + self.speed, gridtop + 14 * size)
        else: # self.direction == 3
            self.rect.left = max(self.rect.left - self.speed, gridleft)

    def shoot(self):
        if not self.shot:  # bullet's not already out there
            self.shot = self.shots[self.direction]
            self.shotRect = self.shot.get_rect()
            self.shotDirection = self.direction
            if self.direction == 3:
                self.shotRect.top = self.rect.top
                self.shotRect.left = self.rect.left - size // 2
            elif self.direction == 1:
                self.shotRect.top = self.rect.top
                self.shotRect.left = self.rect.left + size // 2
            elif self.direction == 0:
                self.shotRect.top = self.rect.top - size // 2
                self.shotRect.left = self.rect.left
            elif self.direction == 2:
                self.shotRect.top = self.rect.top + size // 2
                self.shotRect.left = self.rect.left
            screen.blit(self.shot, self.shotRect)
        else:  # shot already fired, so move it
            if self.shotDirection == 0:
                self.shotRect.top = self.shotRect.top - self.shotSpeed
            elif self.shotDirection == 1:
                self.shotRect.left = self.shotRect.left + self.shotSpeed
            elif self.shotDirection == 2:
                self.shotRect.top = self.shotRect.top + self.shotSpeed
            else:  # self.shotDirection == 3
                self.shotRect.left = self.shotRect.left - self.shotSpeed
            screen.blit(self.shot, self.shotRect)
            if self.shotRect.top + size // 2 < gridtop or self.shotRect.top + size // 2 > gridtop + 15 * size  or \
                    self.shotRect.left + size // 2 < gridleft or self.shotRect.left + size // 2 > gridleft + size * 15:
                # hit a wall
                self.shot = False

class Drone:
    global play
    global ships

    # Drone ship
    def __init__(self, left, top, direction, speed, team=0):
        self.direction = direction
        self.speed = speed
        self.team = team
        # (X * rnd) < level - Y : at level Y+i, there's an i/X chance of canDo
        self.canSee = (5 * random.random()) < level - 1  # ship02
        self.canShoot = (5 * random.random()) < level - 2
        self.canFollow = (5 * random.random()) < level - 3  # ship03
        self.canSense = (7 * random.random()) < level - 3
        self.isFast = (7 * random.random()) < level - 7
        self.canTakeAHit = pygame.image.load("shield.gif") if (5 * random.random()) < level - 4  else False
        self.shot = False
        self.shotSpeed = 4
        self.hit = False
        self.inert = False  # so bullet persists

        self.images = []
        self.shots = []
        lvl = 3 if self.canFollow else 2
        self.images = []
        for dir in range(4):
            speedImages = []
            for spd in range(4):
                speedImages.append(pygame.image.load("ship" + str(team) + str(lvl) + str(dir) + str(spd) + ".gif"))
            self.images.append(speedImages)
            self.shots.append(pygame.image.load("shot" + str(team) + str(dir) + ".gif"))
        self.image = self.images[2][0]
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left

    def move(self):

        # draw drone w/features
        if play:
            self.speed = 3 if self.isFast else 2
        else:
            self.speed = 0
        self.image = self.images[self.direction][self.speed]
        if not self.inert:
            screen.blit(self.image, self.rect)
            if self.canShoot and not self.shot: screen.blit(self.shots[self.direction], self.rect)
            if self.canTakeAHit: screen.blit(self.canTakeAHit, self.rect)

        # make turn decision
        self.turn()
        if self.canShoot:
            self.shoot()

        # Move as far as border
        if clear(self):
            if self.direction == 0:
                self.rect.top = max(self.rect.top - self.speed, gridtop)
            elif self.direction == 1:
                self.rect.left = min(self.rect.left + self.speed, gridleft + 14 * size)
            elif self.direction == 2:
                self.rect.top = min(self.rect.top + self.speed, gridtop + 14 * size)
            else:  # self.direction == 3
                self.rect.left = max(self.rect.left - self.speed, gridleft)
        else:  # turn around
            self.direction = (self.direction + 2) % 4

    def turn(self):

        r = random.random()
        # firt check @corner overrides
        if ((self.rect.top - gridtop) / 2) % size == 0 and ((self.rect.left - gridleft) / 2) % size == 0:
            if self.canSense and not ships[1-self.team].hit and r < .1:  # track north-south
                if self.rect.top < ships[1-self.team].rect.top:
                    self.direction = 2
                if self.rect.top > ships[1-self.team].rect.top:
                    self.direction = 0
            elif self.canSense and not ships[1-self.team].hit and r < .2:  # track east-west
                if self.rect.left < ships[1-self.team].rect.left:
                    self.direction = 1
                if self.rect.top > ships[1-self.team].rect.top:
                    self.direction = 3
            if self.canFollow and not ships[1-self.team].hit:  # one row/col over
                if self.rect.top == ships[1-self.team].rect.top + 2 * size:
                    self.direction = 0
                elif self.rect.top == ships[1-self.team].rect.top - 2 * size:
                    self.direction = 2
                elif self.rect.left == ships[1-self.team].rect.left + 2 * size:
                    self.direction = 3
                elif self.rect.left == ships[1-self.team].rect.left - 2 * size:
                    self.direction = 1
            if self.canSee and not ships[1-self.team].hit:  # in the same aisle
                if self.rect.top == ships[1-self.team].rect.top and self.rect.left > ships[1-self.team].rect.left:
                    self.direction = 3
                elif self.rect.top == ships[1-self.team].rect.top and self.rect.left < ships[1-self.team].rect.left:
                    self.direction = 1
                elif self.rect.top > ships[1-self.team].rect.top and self.rect.left == ships[1-self.team].rect.left:
                    self.direction = 0
                elif self.rect.top < ships[1-self.team].rect.top and self.rect.left == ships[1-self.team].rect.left:
                    self.direction = 2
            if r < .15:  # random left
                self.direction = (self.direction - 1) % 4
            elif r < .3:  # random right
                self.direction = (self.direction + 1) % 4
        if self.direction == 0 and self.rect.top - gridtop == 0 or \
                self.direction == 1 and self.rect.left == gridleft + 14 * size or \
                self.direction == 2 and self.rect.top == gridtop + 14 * size or \
                self.direction == 3 and self.rect.left == gridleft:  # Don't go off grid (start over)
            self.direction = (self.direction + 2) % 4

    def shoot(self):
        if not self.shot:  # bullet's not already out there
           if not ships[1-self.team].hit:  # shoot 'em if you got 'em in your sights
                if self.rect.top == ships[1-self.team].rect.top and self.rect.left > ships[1-self.team].rect.left and self.direction == 3:
                    self.shot = self.shots[3]
                    self.shotRect = self.shot.get_rect()
                    self.shotRect.top = self.rect.top
                    self.shotRect.left = self.rect.left - size // 2
                    self.shotDirection = self.direction
                    screen.blit(self.shot, self.shotRect)
                elif self.rect.top == ships[1-self.team].rect.top and self.rect.left < ships[1-self.team].rect.left and self.direction == 1:
                    self.shot = self.shots[1]
                    self.shotRect = self.shot.get_rect()
                    self.shotRect.top = self.rect.top
                    self.shotRect.left = self.rect.left + size // 2
                    self.shotDirection = self.direction
                    screen.blit(self.shot, self.shotRect)
                elif self.rect.top > ships[1-self.team].rect.top and self.rect.left == ships[1-self.team].rect.left and self.direction == 0:
                    self.shot = self.shots[0]
                    self.shotRect = self.shot.get_rect()
                    self.shotRect.top = self.rect.top - size // 2
                    self.shotRect.left = self.rect.left
                    self.shotDirection = self.direction
                    screen.blit(self.shot, self.shotRect)
                elif self.rect.top < ships[1-self.team].rect.top and self.rect.left == ships[1-self.team].rect.left and self.direction == 2:
                    self.shot = self.shots[2]
                    self.shotRect = self.shot.get_rect()
                    self.shotRect.top = self.rect.top + size // 2
                    self.shotRect.left = self.rect.left
                    self.shotDirection = self.direction
                    screen.blit(self.shot, self.shotRect)
        else:  # shot already fired, so move it
            if self.shotDirection == 0:
                self.shotRect.top = self.shotRect.top - self.shotSpeed
            elif self.shotDirection == 1:
                self.shotRect.left = self.shotRect.left + self.shotSpeed
            elif self.shotDirection == 2:
                self.shotRect.top = self.shotRect.top + self.shotSpeed
            else:  # self.shotDirection == 3
                self.shotRect.left = self.shotRect.left - self.shotSpeed
            if self.shotRect.top - gridtop < -size // 2 or gridtop + 15 * size - self.shotRect.top < size // 2 or \
                    self.shotRect.left - gridleft < -size // 2 or gridleft + 15 * size - self.shotRect.left < size // 2 :
                # hit a wall
                self.shot = False
            else:
                screen.blit(self.shot, self.shotRect)


def clear(ship):
    rect = copy.copy(ship.rect)
    if ship.direction == 0: rect.top -= ship.speed
    if ship.direction == 1: rect.left += ship.speed
    if ship.direction == 2: rect.top += ship.speed
    if ship.direction == 3: rect.left -= ship.speed
    for drone in drones[ship.team]:
        if hit(drone.rect, rect, 2) and ship is not drone:
            return False
    return True


def hit(rectA, rectB, factor):
    # True if two objects are close enough
    return pow(pow(rectA.top - rectB.top, 2) + pow(rectA.left - rectB.left, 2), .5) < size // factor


def boom(ship):
    # check for collision
    for drone in drones[ship.team-1]:
        if ship.shot: # did ship shot hit drone?
            if not drone.inert and hit(drone.rect, ship.shotRect, 1.5):
                drone.hit = True
                ship.shot = False
                screen.blit(sploady1, drone.rect)
        if drone.shot: # did drone shot hit ship?
            if not ship.inert and hit(drone.shotRect, ship.rect, 1.5):
                ship.hit = True
                drone.shot = False
                screen.blit(sploady1, ship.rect)
        if not drone.inert and not ship.inert and hit(drone.rect, ship.rect, 1.5):
            screen.blit(sploady1, ship.rect)
            screen.blit(sploady1, drone.rect)
            ship.hit = True
            drone.hit = True


def place_ship(team=1):  # find an empty row & col for our revived hero
    while True:
        left =int((8 * random.random()) // 1 * size * 2 + gridleft)
        top = int((8 * random.random()) // 1 * size * 2 + gridtop)
        for drone in drones[team-1]:
            if drone.rect.left == left or drone.rect.top == top:
                break
        else: #######todo: check for ship-ship conflict
            ships[team].rect.left = left
            ships[team].rect.top = top
            break

def game_over(score):

    #screen.blit(pygame.Surface((100, 150)), (5, 550))
    screen.blit(pygame.Surface((150, 100)), (300, 550))
    screen.blit(pygame.Surface((450, 445)), (5, 600))
    screen.blit(font40.render("Game Over", True, (180, 0, 0)), (100, 650))

    try:
        with open("scores.dat", "rb") as file:
            scores = pickle.load(file)
    except:
        scores = [["Derek", 10000, 5], ["Pete", 8000, 4], ["Mark", 6000, 3], ["Mike", 4000, 2], ["Jack", 2000, 1]]
    for i in range(5):
        if score > scores[i][1]:
            screen.blit(font20.render("You got a High Score!", True, (180, 0, 0)), (80, 750))
            screen.blit(font20.render("Please enter your name:", True, (180, 0, 0)), (80, 800))
            player_name = ""
            while True:
                pygame.display.flip()
                while True:
                    event = pygame.event.poll()
                    if event.type == KEYDOWN:
                        inkey = event.key
                        break
                if inkey == K_BACKSPACE:
                    player_name = player_name[:len(player_name) - 1]
                elif inkey == K_RETURN:
                    break
                elif inkey <= 127:
                    player_name = player_name + chr(inkey - (32 if len(player_name) == 0 else 0))

                screen.blit(font20.render(player_name, True, (180, 0, 0)), (100, 880))

            scores.insert(i, [str(player_name), score, level])
            scores.pop()
            break

    screen.blit(pygame.Surface((150, 100)), (300, 550))
    screen.blit(pygame.Surface((450, 445)), (5, 600))
    screen.blit(font40.render("High Scores", True, (180, 0, 0)), (100, 630))
    screen.blit(font20.render("Player     Level       Score", True, (180, 0, 0)), (80, 690))
    screen.blit(font20.render("Press heRe to restart", True, (180, 0, 0)), (100, 900))

    for i in range(5):
        screen.blit(font20.render('{:<15}'.format(scores[i][0]), True, (180, 0, 0)), (80, 720 + i * 25))
        screen.blit(font20.render('{:>7}'.format(str(scores[i][2])), True, (180, 0, 0)), (165, 720 + i * 25))
        screen.blit(font20.render('{:>14}'.format(str(scores[i][1])), True, (180, 0, 0)), (235, 720 + i * 25))
    with open("scores.dat", "wb") as file:
        pickle.dump(scores, file)

def main():

    global score
    global level
    global drones
    global lives
    global key
    global play
    global ships

    random.seed()

    players = 1
    if players == 1:
        drones=[[], None]

    canLevel = True
    fuel = 10000

    while True:

        screen.blit(grid, gridrect)
        if not canLevel: screen.blit(pygame.Surface((60, 60)), (150, 600))

        if players == 1:
            if len(drones[0]) == 0:  # Instantiate drone fleet for the new level
                for i in range(7):
                    drone = Drone(border + i * 2 * size, gridtop, 2, 0, 0)
                    drones[0].append(drone)
                ships = [None, Ship(gridleft + 14 * size, gridtop + 14 * size, 0, 0, 1)]

                score[1] = score[1] + 100 * level + fuel // 10 * level  # bonus
                ships[1].shot = False
                #need this? ships[1].direction = 1
                key = 0
                level = level + 1
                fuel = 10000
                play = False

        screen.blit(font40.render('{:<10}'.format("Score"), True, (0, 150, 0)), (20, 565))
        screen.blit(font40.render('{:>10}'.format(str(score[1])), True, (0, 150, 0)), (80, 565))
        screen.blit(font40.render('{:<10}'.format("Level"), True, (0, 150, 0)), (20, 605))
        screen.blit(font40.render('{:>10}'.format(str(level)), True, (0, 150, 0)), (80, 605))

        screen.blit(font40.render('{:<10}'.format("Fuel"), True, (0, 150, 0)), (20, 660))
        draw_fuel_bar(fuel)
        screen.blit(font40.render('{:<10}'.format("Ships"), True, (0, 150, 0)), (136, 660))
        show_lives(lives[1])

        if ships[1].hit:  # lose a life
            ships[1].rect.top = -10000
            ships[1].rect.left = -10000
            ships[1].speed = 0
            ships[1].move(0)
            for drone in drones[0]:
                if drone.shot or ships[1].shot:
                    break
            else: # no live shots
                play = False
                if lives[1] >= 1:
                    lives[1] = lives[1] - 1
                    ships[1].hit = False
                    fuel = (fuel + 10000) // 2
                    draw_fuel_bar(fuel)
                    place_ship(1)
                    ships[1].image = ships[1].images[ships[1].direction][0]
                    screen.blit(ships[1].image, ships[1].rect)
                    pygame.draw.polygon(screen, (0,0,0), ((130, 840), (130, 700), (270, 700)))
                    show_lives(lives[1])
                else:
                    game_over(score[1])

        else:
            ships[1].move(key)

        fuel = fuel - ships[1].speed
        if key in {K_SPACE}: key = 0  # don't keep shooting

        boom(ships[1])

        for drone in drones[0]:
            drone.move()
            if drone.hit:
                drone.hit = False
                if drone.canTakeAHit:
                    drone.canTakeAHit = False
                else:
                    drone.inert = True
                    score[1] = score[1] + 100  # score!
            if drone.inert and not drone.shot:
                drones[0].remove(drone)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()  # time.sleep(10) #
            if event.type == pygame.KEYDOWN: key = event.key

        while not play:  # wait for keypress to start game
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.KEYDOWN:
                    play = True
                    key = event.key

        if key == K_l and lives > 0:  # change level
            level = 10
            canLevel = False
            drones[0] = []
            for i in range(7):
                drone = Drone(gridleft + i * 2 * size, gridtop, 2, 0, 0)
                drones[0].append(drone)
            ships =[None, Ship(gridleft + 14 * size, gridtop + 14 * size, 0, 0, 1)]
            ships[1].shot = False
            fuel = 10000
            play = False

        if key == K_r:  # reset game
            level = 0
            drones[0] = []
            score = [0,0]
            canLevel = True
            lives = [3,6]

        time.sleep(1.0 / 50)

if __name__ == "__main__":
        main().run()