import pygame 
import math

from pygame.math import Vector2 as vec2
import pygame.gfxdraw

import copy
from enum import Enum
import random
  
pygame.init() 

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Shape(Enum):
    CIRCLE = 1
    SQUARE = 2
    TRIANGLE = 3

MAXV = 4.55
ACC = 0.2

SIZE=20

CAR_CAP = 6
STATION_CAP = 6
CROWD_TIME = 300
  
surface = pygame.display.set_mode((1000, 600)) 
pygame.display.set_caption("Mini Metro") 
clock = pygame.time.Clock()

grid = 50
c = 10

def get_angle(v1: vec2, v2: vec2):
    d = v2-v1
    angle = math.atan(d.y/d.x) if d.x != 0 else 0
    if d.x < 0: angle += math.pi
    return angle

def draw_passenger(screen, pos: vec2, shape: Shape, color=BLACK):
    x, y = pos
    match shape:
        case Shape.CIRCLE:
            pygame.draw.circle(screen, color, (x, y), 3)
        case Shape.SQUARE:
            pygame.draw.rect(screen, color, pygame.Rect(x-3, y-3, 6, 6))
        case Shape.TRIANGLE:
            pygame.draw.polygon(screen, color, [(x, y-2.5), (x-3, y+3), (x+3, y+3)])
        case _:
            raise ValueError(f"{shape} is not a valid shape")

class Station:
    def __init__(self, pos: vec2, shape: Shape):
        self.pos = pos
        self.shape = shape
        self.passengers = []
        self.countdown = random.randint(0, 10)
        self.crowd_time = 0

    def draw(self, screen):
        x, y = self.pos
        match self.shape:
            case Shape.CIRCLE:
                pygame.draw.circle(screen, BLACK, (x, y), 17)
                pygame.draw.circle(screen, WHITE, (x, y), 13)
            case Shape.SQUARE:
                pygame.draw.rect(screen, BLACK, pygame.Rect(x-17, y-17, 34, 34))
                pygame.draw.rect(screen, WHITE, pygame.Rect(x-13, y-13, 26, 26))
            case Shape.TRIANGLE:
                pygame.draw.polygon(surface, BLACK, [(x, y-SIZE*1.5), (x-SIZE*1.5-2, y+SIZE), (x+SIZE*1.5-2, y+SIZE)])
                pygame.draw.polygon(surface, WHITE, [(x, y-SIZE+3), (x-SIZE+2, y+SIZE*0.5+1), (x+SIZE+2, y+SIZE*0.5+1)])

        for idx, passenger in enumerate(self.passengers):
            draw_passenger(screen, self.pos + (SIZE + 5 + (idx % 3)*10, -15 + (idx // 3)* 10), passenger)

    def update(self):
        """Add passengers and check for overflow"""
        self.countdown -= 1

        if len(self.passengers) > STATION_CAP:
            self.crowd_time += 1

            if self.crowd_time > CROWD_TIME:
                print("You lose.")

        else:
            self.crowd_time = 0



        if self.countdown <= 0:
            self.countdown = random.randint(150, 300)

            i = random.random()
            passenger_type = Shape.CIRCLE
            if i < 0.2:
                passenger_type = Shape.SQUARE
            elif i < 0.5:
                passenger_type = Shape.TRIANGLE

            self.passengers.append(passenger_type)

class Line:
    def __init__(self, color, stations):
        self.color = color
        self.stations = stations
        self.segs = get_line_segments([station.pos for station in stations])
        self.locations = [seg[0] for seg in self.segs]
        self.locations.append(self.segs[-1][1])

    def draw(self, screen):
        w1, w2 = 8, 10

        # Draw the segments
        for seg in self.segs:
            start, end = seg

            angle = math.atan((end.y - start.y)/(end.x - start.x)) if end.x != start.x else 0

            width = w1 if start.x == end.x or start.y == end.y else w2

            pygame.draw.line(screen, self.color, (start.x + math.cos(angle), start.y + math.sin(angle)), (end.x - math.cos(angle), end.y - math.sin(angle)), width)

        # Draw the endings
        start, end = self.segs[0]
        angle = math.atan((end.y - start.y)/(end.x - start.x)) if end.x != start.x else 0
        width = w1 if start.x == end.x or start.y == end.y else w2
        pygame.draw.line(screen, self.color, (start.x, start.y), (start.x - 40*math.cos(angle), start.y - 40*math.sin(angle)), width)

        start, end = self.segs[-1]
        angle = math.atan((end.y - start.y)/(end.x - start.x)) if end.x != start.x else 0
        width = w1 if start.x == end.x or start.y == end.y else w2
        pygame.draw.line(screen, self.color, (end.x, end.y), (end.x + 40*math.cos(angle), end.y + 40*math.sin(angle)), width)

class Car:
    def __init__(self, color, pos, line: Line):
        self.color = color
        self.pos = pos
        self.v = 0
        self.target_idx = 0
        self.seg_idx = 0
        self.forward = True
        self.wait = False
        self.wait_counter = 0
        self.passengers = []
        self.line = line

        self.angle = get_angle(self.pos, self.line.locations[self.seg_idx])
        self.dir = vec2(math.cos(self.angle), math.sin(self.angle))

    def draw(self, screen):
        w, h = 40, 20
        x, y = self.pos

        # Create surface for car
        car_surface = pygame.Surface((w, h), pygame.SRCALPHA)  # Alpha for transparency
        car_surface.fill(self.color)

        # Add passengers
        for idx, passenger in enumerate(self.passengers):
            draw_passenger(car_surface, (10+10*(idx % 3), 5+10*(idx // 3)), passenger, WHITE)

        # Rotate surface
        rotated_car_surface = pygame.transform.rotate(car_surface, -self.angle*180/math.pi+self.forward*180+180)
        rotated_rect = rotated_car_surface.get_rect(center=(x, y))
        screen.blit(rotated_car_surface, rotated_rect.topleft)

        # Draw passengers
        
    def update(self):

        if self.wait:
            self.wait_counter -= 1

            if self.wait_counter <= 0:
                self.wait = False
                self.wait_counter = 5

        else:

            self.pos += self.v * self.dir

            if self.line.stations[self.target_idx].pos.distance_to(self.line.locations[self.seg_idx]) != 0:
                if self.pos.distance_to(self.line.locations[self.seg_idx]) < self.v:
                    self._stop_update()
        
            if self.pos.distance_to(self.line.stations[self.target_idx].pos) <= self.v:
                self.v = 0
                self._station_update()

            if self.pos.distance_to(self.line.stations[self.target_idx].pos) <= 50:
                self.v = max(0, self.v - ACC)

            elif self.v < MAXV:
                self.v = min(MAXV, self.v + ACC)

    def _stop_update(self):
        self.seg_idx += 1 if self.forward else -1
        self.angle = get_angle(self.pos, self.line.locations[self.seg_idx])
        self.dir = vec2(math.cos(self.angle), math.sin(self.angle))

    def _station_update(self):

        station = self.line.stations[self.target_idx]

        # Offboard any passengers
        for idx in range(len(self.passengers)-1, -1, -1):
            if self.passengers[idx] == station.shape:
                self.passengers.pop(idx) 

        # Onboard any passengers
        for idx in range(len(station.passengers) -1, -1, -1):
            if len(self.passengers) >= CAR_CAP:
                break
            self.passengers.append(station.passengers.pop(idx))

        self.pos = copy.deepcopy(station.pos)

        if self.forward:
            if self.target_idx + 1 < len(self.line.stations):
                self.target_idx += 1
            else:
                self.forward = False
                self.target_idx -= 1
        else:
            if self.target_idx - 1 >= 0:
                self.target_idx -= 1
            else:
                self.forward = True
                self.target_idx += 1
        self.wait = True

        self._stop_update()

def get_line_segments(stops):
    """Get all the line segments in a path"""

    segs = []

    for i in range(len(stops) - 1):
        start, end = stops[i], stops[i+1]

        if start.x == end.x or start.y == end.y:
            segs.append([start, end])
        elif abs(start.x - end.x) > abs(start.y - end.y):
            sign = 1 if end.x - start.x > 0 else -1
            mid = vec2(start.x + sign * abs(start.y - end.y), end.y)
            
            segs.append([start, mid])
            segs.append([mid, end])

        elif abs(start.x - end.x) < abs(start.y - end.y):
            sign = 1 if end.y - start.y > 0 else -1
            mid = (end.x, start.y + sign * abs(start.x - end.x))
            
            segs.append([start, mid])
            segs.append([mid, end])

        else:
            segs.append([start, end])

    return segs



stations = [
    Station(vec2(300, 500), Shape.CIRCLE),
    Station(vec2(600, 500), Shape.CIRCLE),
    Station(vec2(800, 400), Shape.CIRCLE),
    Station(vec2(300, 150), Shape.CIRCLE),
    Station(vec2(500, 300), Shape.SQUARE),
    Station(vec2(650, 250), Shape.TRIANGLE)
]

lines = [
    Line(BLUE, [stations[0], stations[1], stations[2]]),
    Line(RED, [stations[3], stations[4], stations[5]])
]

cars = [
    Car(BLUE, vec2(300, 500), lines[0]),
    Car(RED, vec2(300, 150), lines[1])
]

exit = False

while not exit: 

    # Draw the background
    surface.fill(WHITE)
    for x in range(1000//grid):
        pygame.draw.line(surface, GRAY, (x*grid, 0), (x*grid, 600))
    for y in range(600//grid):
        pygame.draw.line(surface, GRAY, (0, y*grid), (1000, y*grid))

    for line in lines:
        line.draw(surface)

    # Draw the vehicles
    for car in cars:
        car.update()
        car.draw(surface)

    for station in stations:
        station.update()
        station.draw(surface)

    # r = math.tan(3*math.pi/8)*c
    # x = 450
    # y = 300
    # # print(r)
    # rect = pygame.Rect(x + c - r, y-2*r, 2*r, 2*r)

    # d = 0

    # for i in range(10*6):
    #     rect = pygame.Rect(x+c-r-d+2, y-2*r-d+1, 2*r+2*d, 2*r+2*d)
    #     pygame.draw.arc(screen, RED, rect, 5*math.pi/4, 3*math.pi/2, width=1)
    #     d += 0.05


    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            exit = True

    pygame.display.update() 
    clock.tick(30)