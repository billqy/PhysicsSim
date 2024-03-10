import pygame
import math
import numpy as np
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
                    self.collision_handle(other, distance)

    def collision_handle(self, other, d):
        # u1 = v1 - 2 * m2 / M * np.dot(v1 - v2, r1 - r2) / d * (r1 - r2)
        # u2 = v2 - 2 * m1 / M * np.dot(v2 - v1, r2 - r1) / d * (r2 - r1)

        vx1, vx2 = self.xvelo, other.xvelo
        vy1, vy2 = self.yvelo, other.yvelo
        px1, px2 = self.xpos, other.xpos
        py1, py2 = self.ypos, other.ypos
        M = self.mass + other.mass
        dx = np.linalg.norm(px1 - px2)**2
        dy = np.linalg.norm(py1 - py2)**2

        if dx == 0:
            dx += 0.00000001
        if dy == 0:
            dy += 0.00000001

        self.xvelo = vx1 - 2 * other.mass / M * np.dot(vx1 - vx2, px1 - px2) / dx * (px1 - px2)
        other.xvelo = vx2 - 2 * self.mass / M * np.dot(vx2 - vx1, px2 - px1) / dx * (px2 - px1)

        self.yvelo = vy1 - 2 * other.mass / M * np.dot(vy1 - vy2, py1 - py2) / dy * (py1 - py2)
        other.yvelo = vy2 - 2 * self.mass / M * np.dot(vy2 - vy1, py2 - py1) / dy * (py2 - py1)

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


Test1 = Body(100, 300, 1, "aliceblue", 5, 10, 5)
Test2 = Body(400, 400, 1.5, "aliceblue", 50, 50, 0)
Test3 = Body(XMAX/2, YMAX/2, 1.25, "aliceblue", 25, -10, 50)
Test4 = Body(600, 750, 1.1, "aliceblue", 10, -30, -10)
Test5 = Body(300, 600, 1, "aliceblue", 5, 100, -30)
BODIES.append(Test1)
BODIES.append(Test2)
BODIES.append(Test3)
BODIES.append(Test4)
BODIES.append(Test5)

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