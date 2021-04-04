import pygame
import time
from animation import Anim


class Player:
    def __init__(self, square_size, obstacles, sprites):
        self.square_size = square_size
        self.obstacles = obstacles
        self.sprites = sprites
        self.move_anim = Anim(sprites["moving"]["right"], speed=0.12)
        self.death_anim = Anim(sprites["death"], speed=0.1)
        self.font = pygame.font.SysFont("coopbl", 55)

        self.timer = {"move": 0}

        self.move_time = 0.02

        self.portals = {1: None, 2: None, "space_pressed": False}

        # initial amount of lives
        self.lives = 3

        # the player will move 2 pixel every move_time sec
        self.reset_move_speed = self.move_speed = 3

        self.color = (211, 144, 11)

        self.direction = {"current": "left",
                          "next": None,
                          "previous": None,
                          "right": (1, 0),
                          "left": (-1, 0),
                          "down": (0, 1),
                          "up": (0, -1)}

        self.killed = False
        self.make_death_anim = False
        self.make_ghost_respawn = False
        self.start_pos = [self.square_size * 9, self.square_size * 11]
        self.rect = pygame.Rect(self.start_pos[0],
                                self.start_pos[1],
                                self.square_size,
                                self.square_size)

        self.define_current_tile()

        self.score = 0

    def define_current_tile(self):
        current_tile_x = int(self.rect.centerx / self.square_size)
        current_tile_y = int(self.rect.centery / self.square_size)
        self.current_tile = [current_tile_x, current_tile_y]

    def user_input(self):
        keys_pressed = pygame.key.get_pressed()
        if ((keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]) and not (
                keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d])):
            self.direction["next"] = "left"

        if ((keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]) and not (
                keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a])):
            self.direction["next"] = "right"

        if ((keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]) and not (
                keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w])):
            self.direction["next"] = "down"

        if ((keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]) and not (
                keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s])):
            self.direction["next"] = "up"

    def change_direction(self, surface):
        if self.direction["next"] is not None:
            next_rect = self.rect.copy()

            next_rect.x += self.move_speed * self.direction[self.direction["next"]][0]

            next_rect.y += self.move_speed * self.direction[self.direction["next"]][1]

            if next_rect.right > 0 and next_rect.left < surface.get_width():

                if next_rect.collidelist(self.obstacles) == -1:
                    self.direction["current"] = self.direction["next"]
                    self.direction["previous"] = self.direction["current"]
                    self.direction["next"] = None

    def move(self, surface):
        self.user_input()

        if time.time() > self.timer["move"]:
            self.timer["move"] = time.time() + self.move_time
            self.define_current_tile()

            self.change_direction(surface)

            if self.direction["current"] is not None:

                self.rect.x += self.move_speed * self.direction[self.direction["current"]][0]
                self.rect.y += self.move_speed * self.direction[self.direction["current"]][1]

                # if the player is outside the screen at the right
                if self.rect.x > surface.get_width():
                    self.rect.x = 0 - self.square_size

                # if the player is outside the screen at the left
                if self.rect.x < 0 - self.square_size:
                    self.rect.x = surface.get_width()

                if self.current_tile == self.portals[2]:
                    self.current_tile = self.portals[1]
                    self.rect.x = self.portals[1][0] * self.square_size
                    self.rect.y = self.portals[1][1] * self.square_size

                # if the player HAS collide with an obstacle
                collide_index = self.rect.collidelist(self.obstacles)
                if collide_index != -1:

                    if self.direction["current"] == "up":
                        self.rect.y = self.obstacles[collide_index].bottom

                    elif self.direction["current"] == "down":
                        self.rect.y = self.obstacles[collide_index].top - self.square_size

                    elif self.direction["current"] == "right":
                        self.rect.x = self.obstacles[collide_index].left - self.square_size

                    elif self.direction["current"] == "left":
                        self.rect.x = self.obstacles[collide_index].right

                    self.direction["previous"] = self.direction["current"]
                    self.direction["current"] = None

    def draw_score(self, surface):
        label = self.font.render(f"Score : {self.score}", 1, (222, 222, 222))
        x_pos = surface.get_width() - label.get_width() - self.square_size
        y_pos = self.square_size // 2 - label.get_height() // 2
        surface.blit(label, (x_pos, y_pos))

    def draw_lives(self, surface):
        label = self.font.render(f"Lives : {self.lives}", 1, (222, 222, 222))
        x_pos = surface.get_width() // 2 - label.get_width() // 2
        y_pos = surface.get_height() - label.get_height() - 4
        surface.blit(label, (x_pos, y_pos))

    def draw(self, surface):
        self.draw_score(surface)
        self.draw_lives(surface)
        self.draw_portals(surface)

        if not self.make_death_anim:
            self.move_anim.do()
            if self.direction["current"] is None:
                self.move_anim.s_index = 0
                direction = "right"
            else:
                direction = self.direction["current"]
            sprite = self.sprites["moving"][direction][self.move_anim.s_index]
            pos_x = self.rect.x + (self.square_size - sprite.get_width()) / 2
            pos_y = (self.rect.y +
                     (self.square_size - sprite.get_height()) / 2 + 1)
            surface.blit(sprite, (pos_x, pos_y))

        # death anim
        if self.make_death_anim:
            self.move_speed = 0
            sprite = self.death_anim.current_sprite
            pos_x = self.rect.x + (self.square_size - sprite.get_width()) / 2
            pos_y = (self.rect.y +
                     (self.square_size - sprite.get_height()) / 2 + 1)
            surface.blit(sprite, (pos_x, pos_y))

            if self.death_anim.do() == "end":
                # reset
                self.make_death_anim = False
                self.make_ghost_respawn = True
                self.reset_pos()

    def reset_pos(self):
        self.rect.x = self.start_pos[0]
        self.rect.y = self.start_pos[1]
        self.move_speed = self.reset_move_speed
        self.direction["current"] = "left"
        self.portals = {1: None, 2: None, "space_pressed": False}

    # Tests if the player is killed or not
    def test_kill(self):
        if self.killed is True:
            self.killed = False
            self.lives -= 1
            self.death_anim.s_index = 0
            self.make_death_anim = True
            self.portals = {1: None, 2: None, "space_pressed": False}
            return True

    def create_portals(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_SPACE]:
            if not self.portals["space_pressed"]:
                self.portals["space_pressed"] = True
                tile = self.current_tile.copy()
                if self.portals[1] == None:
                    self.portals[1] = tile
                elif self.portals[2] == None:
                    self.portals[2] = tile
        else:
            self.portals["space_pressed"] = False

    def draw_portals(self, surface):
        if self.portals[1] != None:
            surface.blit(self.sprites["portals"]["blue"],
                         (self.portals[1][0] * self.square_size, self.portals[1][1] * self.square_size ))
        if self.portals[2] != None:
            surface.blit(self.sprites["portals"]["orange"],
                         (self.portals[2][0] * self.square_size, self.portals[2][1] * self.square_size ))
