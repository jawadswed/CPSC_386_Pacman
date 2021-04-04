import pygame
import time
import random
import math
from animation import Anim


class Timer:
    def __init__(self, level_nb):
        self.reset(level_nb)

    def reset(self, level_nb):
        if level_nb == 1:
            self.phases = [("Scatter", 7), ("Chase", 20),
                           ("Scatter", 7), ("Chase", 20),
                           ("Scatter", 5), ("Chase", 20),
                           ("Scatter", 5), ("Chase", float("inf"))]

        elif 5 > level_nb >= 2:
            self.phases = [("Scatter", 5), ("Chase", 20),
                           ("Scatter", 5), ("Chase", 20),
                           ("Scatter", 5), ("Chase", 1037),
                           ("Scatter", 1), ("Chase", float("inf"))]

        elif level_nb >= 5:
            self.phases = [("Scatter", 7), ("Chase", 20),
                           ("Scatter", 7), ("Chase", 20),
                           ("Scatter", 5), ("Chase", 1033),
                           ("Scatter", 1), ("Chase", float("inf"))]

        self.current_phase_index = 0
        self.current_mode = "Scatter"
        self.start_time = time.time()
        self.timer = 0
        self.paused = False

    def update(self):
        if not self.paused:
            self.timer = time.time() - self.start_time


class Ghost:
    def __init__(self, sprites, start_tile, exit_spawn_path, square_size, map, player_rect,
                 move_time, move_speed, choose_target_tile, start_at_power_points):
        self.sprites = sprites
        self.start_tile = start_tile
        self.exit_spawn_path = exit_spawn_path
        self.square_size = square_size
        self.map = map
        self.move_time = move_time
        self.reset_move_speed = self.move_speed = move_speed

        self.state = "normal"  # the other state is "chased"
        self.chassed_sprite_kind = "chased"

        self.move_anim = Anim(self.sprites["right"], speed=0.12)

        self.start_at_power_points = start_at_power_points  # will start if less than X power points are eaten

        self.move_timer = 0

        self.chased_change_color_timer = 0

        self.pos = [self.start_tile[0] * self.square_size, self.start_tile[1] * self.square_size]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.square_size, self.square_size)
        level_nb = 1
        self.timer = Timer(level_nb)

        # "Scatter" # Scatter -> fixed tile to reach (outside screen) | Chase -> attack pac man | Frightened -> random
        self.mode = self.timer.phases[self.timer.current_phase_index][
            0]

        self.move_direction = "left"

        self.moving_to = (8, 7)  # the first move after the ghost left the spawn (going to the left tile)

        self.choose_target_tile = choose_target_tile

        self.direction_conversion = {"right": (1, 0), "left": (-1, 0),
                                     "down": (0, 1), "up": (0, -1)}

    # def shortest_path_to(self, target_tile):
    #     return target_tile

    def move(self, player_current_tile, surface, power_points_infos):
        if self.start_at_power_points <= power_points_infos["total"] - len(
                power_points_infos["current"]) and time.time() > self.move_timer:

            self.player_current_tile = player_current_tile

            self.move_timer = time.time() + self.move_time

            if len(self.exit_spawn_path) != 0:
                move_direction = self.exit_spawn_path[0][0]
                moving_to = self.exit_spawn_path[0][1]

            else:  # if the ghost is outside the spawn cage
                move_direction = self.move_direction
                moving_to = self.moving_to

            if move_direction == "left":
                self.pos[0] -= self.move_speed
                self.rect.x = self.pos[0]
                if self.pos[0] / self.square_size < moving_to[0]:  # if exceed the target tile
                    self.pos[0] = moving_to[0] * self.square_size
                    self.rect.x = self.pos[0]

                    if self.rect.right <= 0:  # if outside the screen
                        self.rect.x = surface.get_width()
                        self.pos[0] = self.rect.x
                        self.moving_to = (surface.get_width() // self.square_size - 1, moving_to[1])
                    else:
                        if len(self.exit_spawn_path) != 0:
                            self.exit_spawn_path.pop(0)
                        else:
                            self.moving_to = self.choose_next_tile()

            elif move_direction == "right":
                self.pos[0] += self.move_speed
                self.rect.x = self.pos[0]

                if self.pos[0] / self.square_size > moving_to[0]:  # if exceed the target tile
                    self.pos[0] = moving_to[0] * self.square_size
                    self.rect.x = self.pos[0]

                    if self.rect.left >= surface.get_width():
                        self.rect.right = 0
                        self.pos[0] = self.rect.x
                        self.moving_to = (0, moving_to[1])

                    else:
                        if len(self.exit_spawn_path) != 0:
                            self.exit_spawn_path.pop(0)
                        else:
                            self.moving_to = self.choose_next_tile()

            elif move_direction == "up":
                self.pos[1] -= self.move_speed
                self.rect.y = self.pos[1]

                if self.pos[1] / self.square_size < moving_to[1]:  # if exceed the target tile
                    self.pos[1] = moving_to[1] * self.square_size
                    self.rect.y = self.pos[1]
                    if len(self.exit_spawn_path) != 0:
                        self.exit_spawn_path.pop(0)
                    else:
                        self.moving_to = self.choose_next_tile()

            elif move_direction == "down":
                self.pos[1] += self.move_speed
                self.rect.y = self.pos[1]

                if self.pos[1] / self.square_size > moving_to[1]:  # if exceed the target tile
                    self.pos[1] = moving_to[1] * self.square_size
                    self.rect.y = self.pos[1]
                    if len(self.exit_spawn_path) != 0:
                        self.exit_spawn_path.pop(0)
                    else:
                        self.moving_to = self.choose_next_tile()

    def possible_next_tile_algo(self):
        adjacency_tiles = {}
        if self.move_direction != "up":
            adjacency_tiles["down"] = self.map[self.moving_to[1] + 1][self.moving_to[0]]
        if self.move_direction != "down":
            adjacency_tiles["up"] = self.map[self.moving_to[1] - 1][self.moving_to[0]]
        if self.move_direction != "left":
            adjacency_tiles["right"] = self.map[self.moving_to[1]][self.moving_to[0] + 1]
        if self.move_direction != "right":
            adjacency_tiles["left"] = self.map[self.moving_to[1]][self.moving_to[0] - 1]

        while True:
            for direction, tile in adjacency_tiles.items():

                if tile == "#" or tile == "b":
                    del adjacency_tiles[direction]
                    break
            else:
                break

        return list(adjacency_tiles.keys())

    def choose_next_tile(self):
        # update the timer
        self.timer.update()
        if self.timer.timer > self.timer.phases[self.timer.current_phase_index][1]:
            self.timer.start_time = time.time()
            self.timer.current_phase_index += 1
            self.mode = self.timer.phases[self.timer.current_phase_index][0]

        target_tile, possibles_next_direction = self.choose_target_tile()

        if len(possibles_next_direction) == 1:
            next_direction = possibles_next_direction[0]
        # shortest path (in a straight line) to the target tile
        else:
            shortest_line = float("+inf")
            current_chosen_direction = None
            for direction in possibles_next_direction:
                conv = self.direction_conversion[direction]
                tile = (self.moving_to[0] + conv[0],
                        self.moving_to[1] + conv[1])
                # lenght from this tile to the target tile
                line_lenght = math.sqrt(abs(tile[0] - target_tile[0]) ** 2 +
                                        abs(tile[1] - target_tile[1]) ** 2)
                if line_lenght < shortest_line:
                    shortest_line = line_lenght
                    current_chosen_direction = direction

            next_direction = current_chosen_direction

        if next_direction == "right":
            next_tile = [self.moving_to[0] + 1, self.moving_to[1]]
        elif next_direction == "left":
            next_tile = [self.moving_to[0] - 1, self.moving_to[1]]
        elif next_direction == "down":
            next_tile = [self.moving_to[0], self.moving_to[1] + 1]
        elif next_direction == "up":
            next_tile = [self.moving_to[0], self.moving_to[1] - 1]

        self.move_direction = next_direction

        return next_tile

    def draw(self, surface):
        # if self.state == "chased":

        self.move_anim.do()
        if self.state == "chased":
            if self.chased_start_time + 10 > time.time():
                if self.chased_start_time + 7 < time.time() and self.chased_change_color_timer < time.time():
                    self.chased_change_color_timer = time.time() + 0.3
                    if self.chassed_sprite_kind == "chased":
                        self.chassed_sprite_kind = "chased_white"
                    else:
                        self.chassed_sprite_kind = "chased"
            else:
                self.chassed_sprite_kind = "chased"
                self.state = "normal"

            sprite = self.sprites[self.chassed_sprite_kind][self.move_anim.s_index]
        else:  # draw the normal sprite
            self.move_speed = self.reset_move_speed
            sprite = self.sprites[self.move_direction][self.move_anim.s_index]
        # pygame.draw.rect(surface, sprite, self.rect)
        surface.blit(sprite, (self.rect.x + (self.square_size - sprite.get_width()) / 2,
                              self.rect.y + (self.square_size - sprite.get_height()) / 2 + 1.5))

    def collide(self, surface, player):

        if self.rect.colliderect(player.rect):
            if self.state == "chased":
                # self.pos = [self.start_tile[0] * self.square_size, self.start_tile[1] * self.square_size]

                self.pos[0] = 9 * self.square_size
                self.pos[1] = 9 * self.square_size
                self.rect = pygame.Rect(self.pos[0], self.pos[1], self.square_size, self.square_size)
                self.exit_spawn_path = [("up", (9, 8)), ("up", (9, 7))]
                player.score += 200
                self.moving_to = (8, 7)
                self.move_direction = "left"
                self.state = "normal"
                print("pac man eat ghost")
            else:
                player.killed = True
                print("ghost eat pac man")


class Blinky(Ghost):  # red ghost
    def __init__(self, sprites, square_size, map, player_rect, current_level):
        levels_settings = {1: {"move_time": 0.017, "move_speed": 3, "start_at_power_points": 0},
                           2: {"move_time": 0.016, "move_speed": 3, "start_at_power_points": 0},
                           3: {"move_time": 0.015, "move_speed": 3, "start_at_power_points": 0},
                           "more": {"move_time": 0.014, "move_speed": 2, "start_at_power_points": 0}}
        if current_level not in list(levels_settings.keys()):
            current_level = "more"

        move_time = levels_settings[current_level]["move_time"]
        move_speed = levels_settings[current_level]["move_speed"]
        start_at_power_points = levels_settings[current_level]["start_at_power_points"]

        start_tile = (9, 7)
        exit_spawn_path = []  # already out of the spawn
        super().__init__(sprites, start_tile, exit_spawn_path, square_size, map, player_rect,
                         move_time, move_speed, self.choose_target_tile, start_at_power_points)

    def choose_target_tile(self):
        possibles_next_direction = self.possible_next_tile_algo()
        if self.state == "chased":  # if the ghost in bkue version:
            random_direction = random.choice(possibles_next_direction)
            target_tile = (self.moving_to[0] + self.direction_conversion[random_direction][0],
                           self.moving_to[0] + self.direction_conversion[random_direction][0])

        elif len(possibles_next_direction) == 1:  # if only one possible direction
            target_tile = "_"

        else:  # if multiples possible directions
            if self.mode == "Chase":
                # next_direction = random.choice(possibles_next_direction)
                target_tile = self.player_current_tile
                pass

            if self.mode == "Scatter":
                target_tile = (17, 0)

        return target_tile, possibles_next_direction


class Clyde(Ghost):  # yellow ghost
    def __init__(self, sprites, square_size, map, player_rect, current_level):
        levels_settings = {1: {"move_time": 0.024, "move_speed": 2, "start_at_power_points": 60},
                           2: {"move_time": 0.02, "move_speed": 2, "start_at_power_points": 40},
                           3: {"move_time": 0.018, "move_speed": 2, "start_at_power_points": 30},
                           "more": {"move_time": 0.016, "move_speed": 2, "start_at_power_points": 15}}
        if current_level not in list(levels_settings.keys()):
            current_level = "more"

        move_time = levels_settings[current_level]["move_time"]
        move_speed = levels_settings[current_level]["move_speed"]
        start_at_power_points = levels_settings[current_level]["start_at_power_points"]

        start_tile = (10, 9)
        exit_spawn_path = [("left", (9, 9)), ("up", (9, 8)), ("up", (9, 7))]
        super().__init__(sprites, start_tile, exit_spawn_path, square_size, map, player_rect,
                         move_time, move_speed, self.choose_target_tile, start_at_power_points)

    def choose_target_tile(self):
        possibles_next_direction = self.possible_next_tile_algo()

        if self.state == "chased":  # if the ghost in bkue version:
            random_direction = random.choice(possibles_next_direction)
            target_tile = (self.moving_to[0] + self.direction_conversion[random_direction][0],
                           self.moving_to[0] + self.direction_conversion[random_direction][0])

        elif len(possibles_next_direction) == 1:  # if only one possible direction
            target_tile = "_"

        else:  # if multiples possible directions
            if self.mode == "Chase":
                # if  the distance to pac man is less  than 8 tiles, he will go to the bottom left tile
                # otherwise his target tile is the pac man tile
                distance_to_player = math.sqrt(
                    abs(self.player_current_tile[0] - (self.pos[0] + self.square_size / 2) // self.square_size) ** 2 +
                    abs(self.player_current_tile[1] - (self.pos[1] + self.square_size / 2) // self.square_size) ** 2)
                if distance_to_player <= 8:
                    target_tile = (0, 20)
                else:
                    target_tile = self.player_current_tile
            if self.mode == "Scatter":
                target_tile = (0, 20)

        return target_tile, possibles_next_direction


class Pinky(Ghost):  # pink ghost
    def __init__(self, sprites, square_size, map, player_rect, player_direction, current_level):
        self.player_direction = player_direction

        levels_settings = {1: {"move_time": 0.024, "move_speed": 2, "start_at_power_points": 5},
                           2: {"move_time": 0.02, "move_speed": 2, "start_at_power_points": 0},
                           3: {"move_time": 0.018, "move_speed": 2, "start_at_power_points": 0},
                           "more": {"move_time": 0.016, "move_speed": 2, "start_at_power_points": 0}}
        if current_level not in list(levels_settings.keys()):
            current_level = "more"

        move_time = levels_settings[current_level]["move_time"]
        move_speed = levels_settings[current_level]["move_speed"]
        start_at_power_points = levels_settings[current_level]["start_at_power_points"]
        start_tile = (9, 9)
        exit_spawn_path = [("up", (9, 8)), ("up", (9, 7))]
        super().__init__(sprites, start_tile, exit_spawn_path, square_size, map, player_rect,
                         move_time, move_speed, self.choose_target_tile, start_at_power_points)

    def choose_target_tile(self):
        possibles_next_direction = self.possible_next_tile_algo()

        if self.state == "chased":  # if the ghost in bkue version:
            random_direction = random.choice(possibles_next_direction)
            target_tile = (self.moving_to[0] + self.direction_conversion[random_direction][0],
                           self.moving_to[0] + self.direction_conversion[random_direction][0])

        elif len(possibles_next_direction) == 1:  # if only one possible direction
            target_tile = "_"

        else:  # if multiples possible directions
            if self.mode == "Chase":

                if self.player_direction["current"] is None:
                    player_dir = self.player_direction["previous"]
                else:
                    player_dir = self.player_direction["current"]

                target_tile_x = self.player_current_tile[0] + self.direction_conversion[player_dir][
                    0] * 4  # take the tile 4 in front of the pac man direction
                target_tile_y = self.player_current_tile[1] + self.direction_conversion[player_dir][1] * 4
                target_tile = (target_tile_x, target_tile_y)

            elif self.mode == "Scatter":
                target_tile = (1, 0)

        return target_tile, possibles_next_direction


class Inky(Ghost):
    def __init__(self, sprites, square_size, map, player_rect, player_direction, blinky_position, current_level):
        self.player_direction = player_direction
        self.blinky_position = blinky_position

        levels_settings = {1: {"move_time": 0.024, "move_speed": 2, "start_at_power_points": 24},
                           2: {"move_time": 0.02, "move_speed": 2, "start_at_power_points": 18},
                           3: {"move_time": 0.018, "move_speed": 2, "start_at_power_points": 14},
                           "more": {"move_time": 0.016, "move_speed": 2, "start_at_power_points": 9}}
        if current_level not in list(levels_settings.keys()):
            current_level = "more"

        move_time = levels_settings[current_level]["move_time"]
        move_speed = levels_settings[current_level]["move_speed"]
        start_at_power_points = levels_settings[current_level]["start_at_power_points"]

        start_tile = (8, 9)
        exit_spawn_path = [("right", (9, 9)), ("up", (9, 8)), ("up", (9, 7))]
        super().__init__(sprites, start_tile, exit_spawn_path, square_size, map, player_rect,
                         move_time, move_speed, self.choose_target_tile, start_at_power_points)

    def choose_target_tile(self):
        possibles_next_direction = self.possible_next_tile_algo()

        if self.state == "chased":  # if the ghost in bkue version:
            random_direction = random.choice(possibles_next_direction)
            target_tile = (self.moving_to[0] + self.direction_conversion[random_direction][0],
                           self.moving_to[0] + self.direction_conversion[random_direction][0])

        elif len(possibles_next_direction) == 1:  # if only one possible direction
            target_tile = "_"

        else:  # if multiples possible directions
            if self.mode == "Chase":
                if self.player_direction["current"] is None:
                    player_dir = self.player_direction["previous"]
                else:
                    player_dir = self.player_direction["current"]

                # Inky take the 2 tile in front of pac man direction.
                # Then he double the vector going from blinky to thies tile
                target_tile_x = self.player_current_tile[0] + self.direction_conversion[player_dir][
                    0] * 2  # take the tile 2 in front of the pac man direction

                # add the x vector going from blinky to this tile
                target_tile_x += abs(target_tile_x - (self.blinky_position[
                                                          0] + self.square_size / 2) // self.square_size)
                target_tile_x = min(target_tile_x, len(self.map[0]))
                target_tile_x = max(0, target_tile_x)
                # same for y
                target_tile_y = self.player_current_tile[1] + self.direction_conversion[player_dir][1] * 2
                target_tile_y += abs(
                    target_tile_y - (self.blinky_position[1] + self.square_size / 2) // self.square_size)
                target_tile_y = min(target_tile_y, len(self.map))
                target_tile_y = max(0, target_tile_y)

                target_tile = (target_tile_x, target_tile_y)

            if self.mode == "Scatter":
                target_tile = (19, 20)

        return target_tile, possibles_next_direction
