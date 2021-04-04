import pygame
import map
import player as pl
import ghost
import time



class Maze:
    """Create a functional maze"""

    def __init__(self, map, square_size, BG_COLOR):
        self.square_size = square_size
        self.BG_COLOR = BG_COLOR
        self.make_maze_rects(map)

    def make_maze_rects(self, map):
        self.barriers_rects = []
        self.blues_rects = []
        self.black_rects = []
        for y in range(len(map)):
            for x in range(len(map[y])):
                if map[y][x] == 'b':
                    self.barriers_rects.append(pygame.Rect(x * self.square_size, y * self.square_size,
                                                           self.square_size, self.square_size))
                if map[y][x] in ('#'):
                    self.blues_rects.append(pygame.Rect(x * self.square_size, y * self.square_size,
                                                        self.square_size, self.square_size))

                    self.black_rects.append(pygame.Rect(x * self.square_size + self.square_size / 3,
                                                        y * self.square_size + self.square_size / 3,
                                                        self.square_size / 3, self.square_size / 3))

                    if y < len(map) - 1:  # check if block at the bottom
                        if map[y + 1][x] == '#':
                            self.black_rects.append(pygame.Rect(x * self.square_size + self.square_size / 3,
                                                                y * self.square_size + self.square_size / 3 * 2,
                                                                self.square_size / 3, self.square_size / 3))
                    if y > 0:  # check if block at the top
                        if map[y - 1][x] == '#':
                            self.black_rects.append(
                                pygame.Rect(x * self.square_size + self.square_size / 3, y * self.square_size,
                                            self.square_size / 3, self.square_size / 3))

                    if x < len(map[y]) - 1:  # check if block at the bottom
                        if map[y][x + 1] == '#':
                            self.black_rects.append(pygame.Rect(x * self.square_size + self.square_size / 3 * 2,
                                                                y * self.square_size + self.square_size / 3,
                                                                self.square_size / 3, self.square_size / 3))
                    if x > 0:  # check if block at the top
                        if map[y][x - 1] == '#':
                            self.black_rects.append(
                                pygame.Rect(x * self.square_size, y * self.square_size + self.square_size / 3,
                                            self.square_size / 3, self.square_size / 3))

    def draw(self, surface):
        for rect in self.blues_rects:
            pygame.draw.rect(surface, (0, 30, 242), rect)
        for rect in self.black_rects:
            pygame.draw.rect(surface, self.BG_COLOR, rect)

        for rect in self.barriers_rects:
            pygame.draw.rect(surface, self.BG_COLOR, rect)
            pygame.draw.rect(surface, (243, 179, 147), (rect.x, rect.y, self.square_size, self.square_size / 3))


class PowerPoints:
    def __init__(self, map, square_size, sound):
        self.map = map
        self.square_size = square_size
        self.sound = sound
        self.player_score_increase = 10

        self.spawn_power_points(map)

    def spawn_power_points(self, map):
        self.power_points_radius = 3
        self.power_points_rects = []
        for y in range(len(map)):
            for x in range(len(map[y])):
                if map[y][x] not in ('#', '-', 'b'):
                    self.power_points_rects.append(
                        pygame.Rect(x * self.square_size + self.square_size / 2 - self.power_points_radius,
                                    y * self.square_size + self.square_size / 2 - self.power_points_radius,
                                    self.power_points_radius * 2, self.power_points_radius * 2))
        self.total_power_points_nb = len(self.power_points_rects)

    def draw(self, surface):
        power_points_color = (222, 188, 166)
        for rect in self.power_points_rects:
            x = rect.x
            y = rect.y
            pygame.draw.circle(surface, power_points_color, (x, y), self.power_points_radius)

    def eat(self, player):
        while True:
            for rect in self.power_points_rects:
                if player.rect.colliderect(rect):
                    self.sound.play()
                    player.score += self.player_score_increase  # increase the player score
                    self.power_points_rects.remove(rect)  # remove the points
                    break
            else:
                break


# If we eat a power pill, the ghosts will turn blue and we will be able to eat them
class PowerPills:
    def __init__(self, map, square_size):
        self.map = map
        self.square_size = square_size
        self.power_pills_radius = 12
        self.spawn_power_points(map)

    def spawn_power_points(self, map):
        # locactions : (1,15),(17,15)
        self.power_pills_rects = []
        all_pos = [(1, 17), (17, 15), (1, 4), (17, 5)]

        for x, y in all_pos:
            self.power_pills_rects.append(
                pygame.Rect(x * self.square_size + self.square_size / 2 - self.power_pills_radius,
                            y * self.square_size + self.square_size / 2 - self.power_pills_radius,
                            self.power_pills_radius * 2, self.power_pills_radius * 2))

    def draw(self, surface):
        power_pills_color = (255, 87, 238)
        for rect in self.power_pills_rects:
            x = rect.x
            y = rect.y
            pygame.draw.circle(surface, power_pills_color, (x + self.power_pills_radius, y + self.power_pills_radius),
                               self.power_pills_radius)
            # pygame.draw.rect(surface, (222,22,22), (x, y, 40, 40))

    def eat(self, player, ghosts):
        while True:
            for rect in self.power_pills_rects:
                if player.rect.colliderect(rect):
                    self.power_pills_rects.remove(rect)  # remove the points

                    for ghost in ghosts:
                        ghost.state = "chased"
                        ghost.chased_start_time = time.time()
                        ghost.move_speed = ghost.move_speed / 1.5
                    break
            else:
                break


class World:
    def __init__(self, SCREEN, sprites, sounds, start_level, BG_COLOR, user_name):
        self.SCREEN = SCREEN
        self.square_size = 42
        self.sprites = sprites
        self.sounds = sounds
        self.current_level = start_level
        self.user_name = user_name
        self.font = pygame.font.SysFont("coopbl", 55)
        self.maze = Maze(map.map_1, self.square_size, BG_COLOR)
        self.spawn_power()
        self.player = pl.Player(self.square_size, self.maze.blues_rects, sprites["pac_man"])

        self.start_screen_time = 4.3  # pac man will be able after X sec

        self.power_points_infos = {"total": self.power_points.total_power_points_nb,
                                   "current": self.power_points.power_points_rects}
        self.create_ghosts()

    def spawn_power(self):
        self.power_points = PowerPoints(map.map_1, self.square_size, self.sounds["chomp"])
        self.power_pills = PowerPills(map.map_1, self.square_size)

    def create_ghosts(self):
        self.ghost_blinky = ghost.Blinky(self.sprites["ghosts"]["blinky-red"], self.square_size, map.map_1,
                                         self.player.rect, self.current_level)
        self.ghost_clyde = ghost.Clyde(self.sprites["ghosts"]["clyde-orange"], self.square_size, map.map_1,
                                       self.player.rect, self.current_level)
        self.ghost_pinky = ghost.Pinky(self.sprites["ghosts"]["pinky-pink"], self.square_size, map.map_1,
                                       self.player.rect, self.player.direction, self.current_level)
        self.ghost_inky = ghost.Inky(self.sprites["ghosts"]["inky-turquoise"], self.square_size, map.map_1,
                                     self.player.rect, self.player.direction, self.ghost_blinky.pos, self.current_level)
        self.all_ghosts = [self.ghost_blinky, self.ghost_clyde, self.ghost_pinky, self.ghost_inky]
        self.ghost_moving_sound_time = 0.5
        self.ghost_moving_timer = 0
        self.start_screen_timer = time.time() + self.start_screen_time
        self.sounds["beginning"].play()

    def change_level(self):
        if self.player.lives > 0:
            if len(self.power_points.power_points_rects) == 0:
                print("-> next level")
                self.current_level += 1
                self.spawn_power()
                self.create_ghosts()
                self.player.reset_pos()

    def draw_current_level(self):
        text = "Level : " + str(self.current_level)
        label = self.font.render(text, 1, (222, 222, 222))
        x_pos = self.SCREEN.get_width() - label.get_width() - self.square_size * 7
        y_pos = self.square_size // 2 - label.get_height() // 2
        self.SCREEN.blit(label, (x_pos, y_pos))

    def draw(self):
        self.maze.draw(self.SCREEN)
        self.draw_current_level()
        self.power_points.draw(self.SCREEN)
        self.power_pills.draw(self.SCREEN)
        self.player.draw(self.SCREEN)
        self.ghost_blinky.draw(self.SCREEN)
        self.ghost_clyde.draw(self.SCREEN)
        self.ghost_pinky.draw(self.SCREEN)
        self.ghost_inky.draw(self.SCREEN)

    def move(self):
        self.player.move(self.SCREEN)
        for ghost in self.all_ghosts:
            ghost.move(self.player.current_tile, self.SCREEN, self.power_points_infos)

    def events(self):
        for ghost in self.all_ghosts:
            ghost.collide(self.SCREEN, self.player)
        if self.player.test_kill():
            print("recreation of the ghosts")
            if self.player.lives > 0:
                self.create_ghosts()

    def end_game_checker(self):
        if self.player.lives <= 0:
            return True

    def do(self):
        self.player.create_portals()
        self.events()
        if time.time() > self.start_screen_timer:

            if time.time() > self.ghost_moving_timer:
                self.sounds["ghost_moving"].play()
                self.ghost_moving_timer = time.time() + self.ghost_moving_sound_time

            self.move()

        self.draw()
        self.power_points.eat(self.player)
        self.power_pills.eat(self.player, self.all_ghosts)
        self.change_level()
        if self.end_game_checker():
            self.sounds["death"].play()
            return "end"
