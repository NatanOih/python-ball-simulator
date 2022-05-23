import pygame
import math
import random
from random import randint

pygame.init()

#Global Variables

WIDTH, HEIGHT = 1000, 1000
screen_size = WIDTH, HEIGHT
BOX_LEFT, BOX_RIGHT, BOX_UP, BOX_DOWN = WIDTH/2 - 250, WIDTH/2 + 250, HEIGHT/2 - 250, HEIGHT/2 + 250
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("particles Simulation")
FPS = 60
RADIUS = 7
MASS = 5
N = 5
GRAVITY = + 0.3

#colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)

FONT = pygame.font.SysFont("comicsans", 16)

class Planet(object):
    G = 5  # bigger G equals more attraction force
    TIMESTEP = 1 

    def __init__(self, x, y, radius, color, mass, vel_x, vel_y):
        self.x = x + WIDTH / 2
        self.y = y + HEIGHT / 2
        self.radius = radius
        self.color = color
        self.mass = mass
        self.orbit = []
        self.x_vel = vel_x
        self.y_vel = vel_y

    @staticmethod
    def get_distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        distance_x = x2 - x1
        distance_y = y2 - y1
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
        return distance

    @staticmethod
    def get_angle(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        distance_x = x2 - x1
        distance_y = y2 - y1
        theta = math.atan2(distance_y, distance_x)
        return theta

    @staticmethod
    def elastic_collision(self_mass, other_mass, self_vel, other_vel):
        new_self_vel = (abs(self_mass) - abs(other_mass)) * self_vel/(abs(self_mass) + abs(other_mass)) + (2 * abs(other_mass)) * other_vel / (abs(self_mass) + abs(other_mass))
        new_other_vel = (abs(other_mass) - abs(self_mass)) * other_vel/(abs(self_mass) + abs(other_mass)) + 2 * abs(self_mass) * self_vel / (abs(self_mass) + abs(other_mass))
        return new_self_vel, new_other_vel

    def circle_collision(self, other):
        point1 = self.x, self.y
        point2 = other.x, other.y

        #detect collisions
        if Planet.get_distance(point1, point2) < self.radius + other.radius:
            self.x_vel, other.x_vel = Planet.elastic_collision(self.mass, other.mass, self.x_vel, other.x_vel)
            self.y_vel, other.y_vel = Planet.elastic_collision(self.mass, other.mass, self.y_vel, other.y_vel)

        #planets collide inside each over
        if Planet.get_distance(point1, point2) < self.radius//4:
            return True

    def borders_collision(self):
        out_of_bound = False
        if self.x + self.radius + self.x_vel > BOX_RIGHT:
            self.x_vel *= -1
        if self.x > BOX_RIGHT + 5:
            out_of_bound = True

        if self.x - self.radius + self.x_vel < BOX_LEFT:
            self.x_vel *= -1
        if self.x < BOX_LEFT - 5:
            out_of_bound = True

        if self.y + self.radius + self.y_vel > BOX_DOWN:
            self.y_vel *= -1
            self.y = BOX_DOWN - self.radius
        if self.y > BOX_DOWN + 5:
            out_of_bound = True

        if self.y - self.radius + self.y_vel < BOX_UP:
            self.y_vel *= -1
            self.y = BOX_UP + self.radius
        if self.y < BOX_UP - 5:
            out_of_bound = True
        return out_of_bound

    def attraction(self, other, attraction_off):
        if not attraction_off:
            point1 = self.x, self.y
            point2 = other.x, other.y
            force = self.G * self.mass * other.mass / (Planet.get_distance(point1, point2) ** 2)
            theta = Planet.get_angle(point1, point2)
            force_x = math.cos(theta) * force
            force_y = math.sin(theta) * force
            return force_x, force_y
        return 0, 0

    def draw(self, win, draw_orbit):
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                updated_points.append(point)

            if draw_orbit:
                pygame.draw.lines(win, self.color, False, updated_points, 2)

        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def update_position(self, balls, attraction_off, gravity_off):
        out_bound = False
        collapse = False
        total_fx = total_fy = 0
        if not gravity_off:
            total_fy = self.mass * GRAVITY

        if self.borders_collision():
            out_bound = True

        for planet in balls:
            if self == planet:
                continue
            if self.circle_collision(planet):
                collapse = True

            fx, fy = self.attraction(planet, attraction_off)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP

        self.orbit.append((self.x, self.y))

        #path length
        if len(self.orbit) > 20:
            self.orbit.pop(0)

        return collapse, out_bound


def mobius_transform(value):
    '''
    function to scale down the incomming values into something managble
    '''
    transform = 1/20 * value
    return transform
    
def lunch(distance, theta):
    transformed_distance = mobius_transform(distance)
    factor = 1
    vel_x = factor * abs(transformed_distance) * - math.cos(theta)
    vel_y = factor * abs(transformed_distance) * - math.sin(theta)
    return vel_x, vel_y

def throw_ball(release, press):
    mouse_traveled = Planet.get_distance(release, press)
    mouse_angle = Planet.get_angle(release, press)
    lunch_vel_x, lunch_vel_y = lunch ( mouse_traveled, mouse_angle)
    mouse_line = [press, release]
    pygame.draw.lines(WIN, WHITE, False, mouse_line, 2)
    return Planet(release[0] - WIDTH / 2, release[1] - HEIGHT / 2, RADIUS, (random.randint(0, 255), random.randint(0, 255) , random.randint(0, 255)), MASS, lunch_vel_x, lunch_vel_y)


def main():
    run = True
    clock = pygame.time.Clock()
    attraction_off = False
    gravity_off = False
    draw_orbit = True

    balls = []

    #initiate few random objects at the beggining
    for i in range(1, N + 1):
        planet_i = Planet(randint(-200, 200), randint(-200, 200), RADIUS, (random.randint(0, 255), random.randint(0, 255) , random.randint(0, 255)), MASS, random.uniform(-0.5, 0.5), random.uniform(-1, 1))
        balls.append(planet_i)

    while run:
        clock.tick(60)
        WIN.fill((0, 0, 0))
        pygame.draw.rect(WIN, WHITE, pygame.Rect(WIDTH/2 - 250, HEIGHT/2 - 250, abs(BOX_LEFT - BOX_RIGHT), abs(BOX_UP - BOX_DOWN)),  1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            #throw new ball with mouse click    
            if event.type == pygame.MOUSEBUTTONDOWN:
                press = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                release = pygame.mouse.get_pos()
                if BOX_LEFT < release[0] < BOX_RIGHT and BOX_UP < release[1] < BOX_DOWN:
                    balls.append(throw_ball(release, press))

            #handle keys

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    balls.clear()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    attraction_off = not attraction_off

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    draw_orbit = not draw_orbit
    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gravity_off = not gravity_off
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
            
        #main Ball loop
        for i, planet in enumerate(balls):
            collapse, out_of_bounds = planet.update_position(balls, attraction_off, gravity_off)
            if collapse or out_of_bounds:
                balls.pop(i)
                continue
            planet.draw(WIN, draw_orbit)

        #UI
        balls_number = FONT.render(f"number of objects: {len(balls)}", True, WHITE)
        WIN.blit(balls_number, (WIDTH / 2 - balls_number.get_width() /
                             2, HEIGHT / 2 - balls_number.get_height() / 2))

        gravity_text = FONT.render(f"press z - Gravity :{not gravity_off}", True, WHITE)
        WIN.blit(gravity_text, (100, 100))

        attraction_text = FONT.render(f"press q - attraction :{not attraction_off}", True, WHITE)
        WIN.blit(attraction_text, (100, 200))

        path_text = FONT.render(f"press e to toggle path :{draw_orbit}", True, WHITE)
        WIN.blit(path_text, (400, 100))

        clear_screen = FONT.render(f"press r to clear screen", True, WHITE)
        WIN.blit(clear_screen, (100, 150))

        clear_screen = FONT.render(f"left mouse click and drag to throw ball", True, WHITE)
        WIN.blit(clear_screen, (400, 150))

        pygame.display.update()
    pygame.quit()

main()