import pygame
import math
import random
from scipy.interpolate import interp1d
from win32gui import SetWindowPos

# UNITS: meter, kilogram

GRAVITY = 9.806
BODIES = []
PATHS = []
path_creation_interval = 10  # 5 frames represents 0.1 seconds passed @60FPS.
path_max_lifetime = 180  # 120 frames represents 2 seconds passed @60FPS.

XMAX = 800
YMAX = 700
SCALE = XMAX / 100
BORDER_ELASTICITY = 0.9

pygame.init()
screen = pygame.display.set_mode((XMAX, YMAX))
SetWindowPos(pygame.display.get_wm_info()['window'], -1, 0, 0, 0, 0, 1)

clock = pygame.time.Clock()
running = True
dt = 0


class Body:
    def __init__(self, xpos, ypos, radius, color, mass, xvelo, yvelo):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = radius * SCALE
        self.color = color

        self.mass = mass
        self.xvelo = xvelo
        self.yvelo = yvelo

        self.path_frame_count = 0

    def collision_check(self):
        for other in BODIES:
            if other != self:
                xdist = abs(other.xpos - self.xpos)
                ydist = abs(other.ypos - self.ypos)
                distance = math.sqrt(pow(xdist, 2) + pow(ydist, 2))

                if (other.radius + self.radius) >= distance:
                    self.collision_handle()

    def collision_handle(self):
        print("Collision detected!")

    def update_values(self):
        self.path_frame_count += 1

        self.yvelo += GRAVITY * SCALE * dt

        self.xpos += self.xvelo * SCALE * dt
        self.ypos += self.yvelo * SCALE * dt

        if self.ypos <= 0:
            self.ypos = 0
            self.yvelo = -self.yvelo * BORDER_ELASTICITY
        elif self.ypos >= YMAX:
            self.ypos = YMAX
            self.yvelo = -self.yvelo * BORDER_ELASTICITY

        if self.xpos <= 0:
            self.xpos = 0
            self.xvelo = -self.xvelo * BORDER_ELASTICITY
        elif self.xpos >= XMAX:
            self.xpos = XMAX
            self.xvelo = -self.xvelo * BORDER_ELASTICITY

        self.collision_check()

    def reset_path_count(self):
        self.path_frame_count = 0


class Path:
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = 2
        self.lifetime = path_max_lifetime

    def determine_color(self):
        default = 255
        adjusted = interp1d([0, path_max_lifetime], [0, default])
        new_val = adjusted(self.lifetime)
        new_color = (new_val, new_val, new_val)
        return new_color


Test1 = Body(XMAX / 2, YMAX / 2, 1, "aliceblue", 5, 50, 0)
Test2 = Body(100, 100, 1, "aliceblue", 5, 50, 0)
BODIES.append(Test1)
BODIES.append(Test2)

while running:
    # -- user events --
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")  # wipe away last frame

    # -- update frame --
    for path in PATHS:
        path.lifetime -= 1
        if path.lifetime <= 0:
            PATHS.remove(path)

        # draw paths
        pygame.draw.circle(screen, path.determine_color(), (path.xpos, path.ypos), path.radius)

    for body in BODIES:
        # update bodies
        body.update_values()

        # create new paths, if applicable
        if body.path_frame_count >= path_creation_interval:
            newPath = Path(body.xpos, body.ypos)
            PATHS.append(newPath)
            body.reset_path_count()

        # draw bodies
        pygame.draw.circle(screen, body.color, (body.xpos, body.ypos), body.radius)

    pygame.display.flip()  # display updates
    dt = clock.tick(60) / 1000  # lock to 60 fps

pygame.quit()