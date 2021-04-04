import pygame
import sys


class Menu:
    """Make a functional menu"""

    def __init__(self, SCREEN, sprites):
        self.SCREEN = SCREEN
        self.GAME_NAME = "PAC MAN"
        self.sprites = sprites

        self.small_font = pygame.font.SysFont("coopbl", 28)
        self.medium_font = pygame.font.SysFont("coopbl", 50)
        self.normal_font = pygame.font.SysFont("coopbl", 80)
        self.big_font = pygame.font.SysFont("coopbl", 160)

        self.user_name = ""
        self.menu_state = "start"
        self.reset()

    def reset(self):
        """reset the menu"""
        self.user_name = ""
        self.menu_state = "start"

    def draw_characteres(self):
        x_pos = 120
        y_pos = 260
        names = ["Blinky", "Clyde", "Pinky", "Inky", "Pac-Man"]
        index = 0
        colors = [(230, 0, 18), (240, 130, 0), (32, 174, 230), (241, 158, 181), (255, 241, 0)]
        for sprite in self.sprites:
            self.SCREEN.blit(sprite, (x_pos, y_pos))

            x_pos += 120
            name_label = self.medium_font.render(str(names[index]), 1, colors[index])
            text_x_pos = x_pos - name_label.get_width() / 2 - sprite.get_width() / 2 - 16
            self.SCREEN.blit(name_label, (text_x_pos, y_pos + sprite.get_height()-10))
            index += 1

    def draw_leaderboard(self, all_score):
        """draw the leaderboard (only the X first scores)"""
        y = 184  # y position of the text
        max_number_of_score = 10  # will only display the top x score
        color = [35, 215, 53]  # start color of the text

        all_score.sort(reverse=True)  # sort the score

        for score in all_score[:max_number_of_score]:
            color[0] += 20
            color[1] -= 12
            # check if it is a valid color
            if color[0] > 255:
                color[0] = 255
            if color[1] < 0:
                color[0] = 0
            # draw the text
            self.text(self.SCREEN, text=f"{score[1]} : {score[0]}", font=self.normal_font, y=y, color=color)
            # change the y position of the next score text
            y += 48

    def button(self, x, y, w, h, color=(66, 173, 94), second_color=(113, 206, 129), text="", text_color=(22, 22, 22)):
        """
        make a clickable button
        x, y : x, y position of the button
        w, h : width, height of the button
        color : color of the button if the mouse is not on the button
        second_color : color of the button if the mouse is on the button
        text : text that will be written on the button
        text_color : the color of the text
        """
        # center the button
        x -= w // 2
        y -= h // 2

        button_rect = pygame.Rect(x, y, w, h)  # position and size of the button

        if button_rect.collidepoint(pygame.mouse.get_pos()):  # check if the mouse collide with the button
            color = second_color
            if pygame.mouse.get_pressed()[0]:  # check if the user is pressing the left mouse button
                return True

        pygame.draw.rect(self.SCREEN, color, button_rect)  # draw the button
        # text
        text_label = self.medium_font.render(text, 1, text_color)
        self.SCREEN.blit(text_label, (button_rect.centerx - text_label.get_width() // 2,
                                      button_rect.centery - text_label.get_height() // 2))  # write the text

    def text(self, surface, text="YOUR TEXT", x="center", y=300, font="default", shadow=True, color=(224, 175, 58)):
        """write some text on the screen"""
        if font == "default":
            font = self.normal_font

        label = font.render(text, 1, color)
        if x == "center":
            x = surface.get_width() // 2 - label.get_width() // 2

        # make  the text shadow
        if shadow is True:
            shadow_label = font.render(text, 1, (168, 88, 61))
            surface.blit(shadow_label, (x - 2, y + 2))

        # write the text on the screen
        surface.blit(label, (x, y))

    def text_input_box(self, key, y=300):
        """make a text input box in which the player can write"""
        text_color = (22, 22, 22)
        box_color = (222, 222, 222)

        if key == "delete_key":
            if len(self.user_name) > 0:
                self.user_name = self.user_name[:-1]
        # allowed keys
        elif key is not None:
            self.user_name += key
        # input box text
        label = self.normal_font.render(f" {self.user_name} ", 1, text_color, box_color)
        self.SCREEN.blit(label, (self.SCREEN.get_width() // 2 - label.get_width() // 2, y))


    def do(self, key, all_score):
        """make the menu functional"""
        # if the user is on the start screen
        if self.menu_state == "start":
            self.text(self.SCREEN, text=self.GAME_NAME, font=self.big_font, y=120)
            self.draw_characteres()

            # buttons
                # start button
            if self.button(self.SCREEN.get_width() // 2, 500, 300, 80, text="Start game"):
                self.menu_state = "name_input"
                # leaderboard button
            if self.button(self.SCREEN.get_width() // 2, 620, 300, 80, text="Leaderboard"):
                self.menu_state = "leaderboard"

            # quit button
            if self.button(self.SCREEN.get_width() // 2, 740, 300, 80, text="Quit"):
                pygame.quit()
                sys.exit()

        # if the user is on the name input screen (after clicking on start)
        elif self.menu_state == "name_input":  # if the user is on the level selection
            self.text(self.SCREEN, text="Enter your name", y=240)
            self.text_input_box(key)
            if len(self.user_name) > 2:  # if ther user has a name with at least 3 letters
                if self.button(self.SCREEN.get_width() // 2, 500, 300, 80, text="Start"):
                    return True

        # if the user is in the leaderboard
        elif self.menu_state == "leaderboard":
            self.text(self.SCREEN, text="Leaderboard", font=self.normal_font, y=72)
            if self.button(self.SCREEN.get_width() // 2, 820, 300, 80, text="Return"):
                self.menu_state = "start"

            self.draw_leaderboard(all_score)
