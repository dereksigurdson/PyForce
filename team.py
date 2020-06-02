import pygame
from pygame.locals import *
import random

from config import size, gridleft, gridtop


class Deets:
    def __init__(self, teamID: int, lives: int, left: int, top: int, direction: int, speed: int, shot: bool,
                 shotLeft: int, shotTop: int, shotDirection: int, orientation: int, hit: bool, current: bool):
        self.teamID: int = teamID
        self.lives = lives
        self.left = left
        self.top = top
        self.direction = direction
        self.speed = speed
        self.shot = shot
        self.shotLeft = shotLeft
        self.shotTop = shotTop
        self.shotDirection = shotDirection
        self.orientation = orientation
        self.hit = hit
        self.current = current


class Team:

    def __init__(self, teamID, orientation=0, x=0, y=0, direction=0, rank=0):
        self.teamID: int = teamID
        self.score: int = 0
        self.ships = [Ship(self, rank=rank)] if x == 0 else [Ship(self, x, y, direction, rank)]
        self.enemy = []
        self.target = None
        self.orientation = orientation
        self.deets = Deets(teamID, 3, self.ships[0].rect.left, self.ships[0].rect.top,
                           self.ships[0].direction, self.ships[0].speed,
                           self.ships[0].shot, self.ships[0].shotRect.left, self.ships[0].shotRect.top,
                           self.ships[0].shotDirection, self.orientation, self.ships[0].hit, True)
        self.lives: int = 3
        self.level = 0
        self.current = True

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        self.deets.current = value
        self._current = value

    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, value):
        self.deets.lives = value
        self._lives = value

    def update(self, deets: Deets):  # for remote player
        self.deets = deets
        self.lives = self.deets.lives
        self.ships[0].rect.left = deets.left
        self.ships[0].rect.top = deets.top
        self.ships[0].direction = deets.direction
        self.ships[0].speed = deets.speed
        self.ships[0].shot = deets.shot
        self.ships[0].shotRect.left = deets.shotLeft
        self.ships[0].shotRect.top = deets.shotTop
        self.ships[0].shotDirection = deets.shotDirection
        self.ships[0].hit = deets.hit
        self.current = deets.current
        return deets


class Ship:

    # Player ship
    def __init__(self, team, x=gridleft + 10 * size, y=gridtop + 14 * size, direction=0, rank=0, target=None):
        self.direction = direction
        self.speed = 0
        self.team = team
        self.shot = False
        self.shotSpeed = 5
        self.hit = False
        self.inert = False  # so bullet persists
        self.rect = pygame.Rect(x, y, size, size)
        self.shotRect = pygame.Rect(x, y, size, size)
        self.shotDirection = 0
        self.autopilot = rank != 0

        self.canShoot = False
        self.canTakeAHit = False

        self.fuel = 10000
        self.lives = 3
        self.delay = 0

        # drone stuff
        self.target = target
        # (X * rnd) < rank - Y : at rank/level Y+i, there's an i/X chance of canDo
        self.canSee = (5 * random.random()) < rank - 1  # ship02
        self.canShoot = True if self.team.teamID > 1 else (5 * random.random()) < rank - 2
        self.canFollow = (5 * random.random()) < rank - 3  # ship03
        self.canSense = (7 * random.random()) < rank - 3
        self.isFast = (7 * random.random()) < rank - 7
        self.canTakeAHit = (5 * random.random()) < rank - 4

        # reassign rank for image
        if self.autopilot:
            self.rank = 3 if self.canFollow else 2 if self.canSee else 1
            self.speed = 3 if self.isFast else 2
        else:
            self.rank = 0

    def update(self):
        self.team.deets.left = self.rect.left
        self.team.deets.top = self.rect.top
        self.team.deets.direction = self.direction
        self.team.deets.speed = self.speed
        self.team.deets.shot = self.shot
        self.team.deets.shotLeft = self.shotRect.left
        self.team.deets.shotTop = self.shotRect.top
        self.team.deets.shotDirection = self.shotDirection
        self.team.deets.hit = self.hit

    def reset(self, x, y, direction=-1):
        if direction != -1:
            self.direction = direction
        self.speed = 0
        self.shot = False
        self.hit = False
        self.inert = False
        self.rect.left = x
        self.rect.top = y

    # return a Rect consistent with parameter's orientation
    def orient(self, orientation, shot=False):
        if orientation == self.team.orientation:
            return self.shotRect if shot else self.rect
        else:
            cw90x = (self.team.orientation - orientation) % 4
            return self.rotate(cw90x, shot)

    # return a Rect rotated clockwise 90' cw90x times
    def rotate(self, cw90x, shot=False):
        # cartesian coords
        x = (self.shotRect.left if shot else self.rect.left) - gridleft - 15 * size // 2
        y = -((self.shotRect.top if shot else self.rect.top) - gridtop - 15 * size // 2)

        # rotate clockwise around 0,0
        for i in range(cw90x):
            x, y = y, -x

        # return grid coords
        left = x + gridleft + 15 * size // 2 - (size if (cw90x % 4) in (1, 2) else 0)
        top = -y + gridtop + 15 * size // 2 - (size if (cw90x % 4) in (2, 3) else 0)
        return pygame.Rect(left, top, size, size)

    def revive(self, factor=3):  # find an empty row & col for revived ship
        while True:
            # set some candidate coordinates
            left = int((8 * random.random()) // 1 * size * 2 + gridleft)
            top = int((8 * random.random()) // 1 * size * 2 + gridtop)
            rect = pygame.Rect(left, top, size, size)

            for ship in self.team.enemy:
                shipRect = ship.orient(self.team.orientation)
                if shipRect.left == left or shipRect.top == top or hit(shipRect, rect, factor):
                    break
            else:
                self.rect.left = left
                self.rect.top = top
                self.inert = False
                break

    def retarget(self):
        rect1 = self.target.orient(self.team.orientation)
        rect2 = self.rect
        dist2 = pow(rect1.top - rect2.top, 2) + pow(rect1.left - rect2.left, 2)
        for ship in self.team.enemy:
            rect1 = ship.orient(self.team.orientation)
            # print(self.team.teamID, rect2, self.target.team.teamID, rect1)
            if pow(rect1.top - rect2.top, 2) + pow(rect1.left - rect2.left, 2) < dist2 and not ship.inert:
                self.target = ship
                dist2 = pow(rect1.top - rect2.top, 2) + pow(rect1.left - rect2.left, 2)

    def move(self, key=0):

        if key < 0:
            # make turn decision
            self.retarget()
            self.speed = key * -1
            self.turn()
            if not clear(self, self.team.ships):
                self.direction = (self.direction + 2) % 4
            if self.canShoot:
                self.autoshoot()

        else:
            # player piloted ship
            if ((self.rect.top - gridtop) / 2) % size == 0:  # allow east-west
                if key in [K_LEFT, K_4, K_a]:
                    self.direction = 3
                elif key in [K_RIGHT, K_6, K_d]:
                    self.direction = 1
            if ((self.rect.left - gridleft) / 2) % size == 0:  # allow north-south
                if key in [K_UP, K_8, K_w]:
                    self.direction = 0
                elif key in [K_DOWN, K_2, K_s]:
                    self.direction = 2
            if key in [K_RCTRL, K_LCTRL, K_5]:
                self.speed = 0
            if key in [K_LEFT, K_4, K_a, K_RIGHT, K_6, K_d, K_UP, K_8, K_w, K_DOWN, K_2, K_s]:
                self.speed = 3

            if key in [K_SPACE] or self.shot:
                self.shoot()

        # Move as far as border
        if self.direction == 0:
            self.rect.top = max(self.rect.top - self.speed, gridtop)
        elif self.direction == 1:
            self.rect.left = min(self.rect.left + self.speed, gridleft + 14 * size)
        elif self.direction == 2:
            self.rect.top = min(self.rect.top + self.speed, gridtop + 14 * size)
        else:  # self.direction == 3
            self.rect.left = max(self.rect.left - self.speed, gridleft)

        self.fuel -= max(self.speed, 1)
        self.update()  # keep current

    def shoot(self):
        if not self.shot:  # bullet's not already out there
            self.shot = True
            self.shotRect = self.rect.copy()
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

        else:  # shot already fired, so move it
            if self.shotDirection == 0:
                self.shotRect.top = self.shotRect.top - self.shotSpeed
            elif self.shotDirection == 1:
                self.shotRect.left = self.shotRect.left + self.shotSpeed
            elif self.shotDirection == 2:
                self.shotRect.top = self.shotRect.top + self.shotSpeed
            else:  # self.shotDirection == 3
                self.shotRect.left = self.shotRect.left - self.shotSpeed

    def turn(self):
        r = random.random()
        targetRect = self.target.orient(self.team.orientation)
        # first check @corner overrides
        if ((self.rect.top - gridtop) / 2) % size == 0 and ((self.rect.left - gridleft) / 2) % size == 0:
            if self.canSense and not self.target.inert and r < .1:  # track north-south
                if self.rect.top < targetRect.top:
                    self.direction = 2
                if self.rect.top > targetRect.top:
                    self.direction = 0
            elif self.canSense and not self.target.inert and r < .2:  # track east-west
                if self.rect.left < targetRect.left:
                    self.direction = 1
                if self.rect.top > targetRect.top:
                    self.direction = 3
            if self.canFollow and not self.target.inert:  # one row/col over
                if self.rect.top == targetRect.top + 2 * size:
                    self.direction = 0
                elif self.rect.top == targetRect.top - 2 * size:
                    self.direction = 2
                elif self.rect.left == targetRect.left + 2 * size:
                    self.direction = 3
                elif self.rect.left == targetRect.left - 2 * size:
                    self.direction = 1
            if self.canSee and not self.target.inert:  # in the same aisle
                if self.rect.top == targetRect.top and self.rect.left > targetRect.left:
                    self.direction = 3
                elif self.rect.top == targetRect.top and self.rect.left < targetRect.left:
                    self.direction = 1
                elif self.rect.top > targetRect.top and self.rect.left == targetRect.left:
                    self.direction = 0
                elif self.rect.top < targetRect.top and self.rect.left == targetRect.left:
                    self.direction = 2
            if r < .15:  # random left
                self.direction = (self.direction - 1) % 4
            elif r < .3:  # random right
                self.direction = (self.direction + 1) % 4
            if self.direction == 0 and self.rect.top == gridtop or \
                    self.direction == 1 and self.rect.left == gridleft + 14 * size or \
                    self.direction == 2 and self.rect.top == gridtop + 14 * size or \
                    self.direction == 3 and self.rect.left == gridleft:  # Don't go off grid
                self.direction = (self.direction + 1 if r < .5 else 3) % 4
            if not clear(self, self.team.ships):
                self.direction = (self.direction + 2) % 4

    def autoshoot(self):
        if not self.shot and not self.inert:  # bullet's not already out there
            targetRect = self.target.orient(self.team.orientation)

            if not self.target.hit:  # shoot 'em if you got 'em in your sights
                if self.rect.top == targetRect.top and self.rect.left > targetRect.left\
                        and self.direction == 3 and not self.target.inert:
                    self.shotRect = self.rect.copy()
                    self.shotRect.left = self.rect.left - size // 2
                    self.shotDirection = self.direction
                    self.shot = True
                elif self.rect.top == targetRect.top and self.rect.left < targetRect.left\
                        and self.direction == 1 and not self.target.inert:
                    self.shotRect = self.rect.copy()
                    self.shotRect.left = self.rect.left + size // 2
                    self.shotDirection = self.direction
                    self.shot = True
                elif self.rect.top > targetRect.top and self.rect.left == targetRect.left\
                        and self.direction == 0 and not self.target.inert:
                    self.shotRect = self.rect.copy()
                    self.shotRect.top = self.rect.top - size // 2
                    self.shotDirection = self.direction
                    self.shot = True
                elif self.rect.top < targetRect.top and self.rect.left == targetRect.left\
                        and self.direction == 2 and not self.target.inert:
                    self.shotRect = self.rect.copy()
                    self.shotRect.top = self.rect.top + size // 2
                    self.shotDirection = self.direction
                    self.shot = True
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
                    self.shotRect.left - gridleft < -size // 2 or gridleft + 15 * size - self.shotRect.left < size // 2:
                # hit a wall
                self.shot = False


def hit(rect1, rect2, factor):
    # True if two objects are close enough
    return pow(pow(rect1.top - rect2.top, 2) + pow(rect1.left - rect2.left, 2), .5) < size * factor


def clear(ship, ships):
    # check to see if the space in front is clear of teammates
    rect = ship.rect.copy()
    if ship.direction == 0:
        rect.top -= ship.speed
    if ship.direction == 1:
        rect.left += ship.speed
    if ship.direction == 2:
        rect.top += ship.speed
    if ship.direction == 3:
        rect.left -= ship.speed
    for other in ships:
        if hit(other.rect, rect, .5) and ship is not other:
            return False
    return True
