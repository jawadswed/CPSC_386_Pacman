
import pygame
import sys
import os
import world as wo
import menu as me


os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 32)  # windows position
pygame.init()
pygame.display.set_caption('Pac Man')
SCREEN_WIDTH = 798
SCREEN_HEIGHT = 882
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

mainClock = pygame.time.Clock()


sprites = {"pac_man": {"moving": {}, "portals": {}}, "ghosts": {}, "menu": []}

sprites_path = "Images"

sprites["pac_man"]["death"] = [pygame.image.load(f"{sprites_path}/pac_man/death/deathPac{nb}.png") for nb in range(11)]
sprites["pac_man"]["moving"]["right"] = [pygame.image.load(f"{sprites_path}/pac_man/moving/moving{nb}.png") for nb in
                                         range(3)]
sprites["pac_man"]["moving"]["left"] = [pygame.transform.rotate(sprite, 180) for sprite in
                                        sprites["pac_man"]["moving"]["right"]]
sprites["pac_man"]["moving"]["up"] = [pygame.transform.rotate(sprite, 90) for sprite in
                                      sprites["pac_man"]["moving"]["right"]]
sprites["pac_man"]["moving"]["down"] = [pygame.transform.rotate(sprite, -90) for sprite in
                                        sprites["pac_man"]["moving"]["right"]]

for color in ("blue", "orange"):
    sprites["pac_man"]["portals"][color] = pygame.transform.scale(
                                             pygame.image.load(f"{sprites_path}/pac_man/portals/{color}.png"),
                                              (42, 42))



for ghost_name in ("blinky-red", "clyde-orange", "inky-turquoise", "pinky-pink"):
    sprites["ghosts"][ghost_name] = {}
    for direction in ("down", "right", "left", "up"):
        dir_prefix = direction[0]
        sprites["ghosts"][ghost_name][direction] = [
            pygame.image.load(f"{sprites_path}/ghosts/{ghost_name}/{dir_prefix}{nb}.png") for nb in range(2)]
        # blue version
    sprites["ghosts"][ghost_name]["chased"] = [pygame.image.load(f"{sprites_path}/ghosts/chased/chased{nb}.png") for nb
                                               in range(2)]
    sprites["ghosts"][ghost_name]["chased_white"] = [pygame.image.load(f"{sprites_path}/ghosts/chased/chased{nb}.png")
                                                     for nb in range(2, 4)]

for ghost_name in ("blinky-red", "clyde-orange", "inky-turquoise", "pinky-pink"):
    sprite = pygame.image.load(f"{sprites_path}/ghosts/{ghost_name}/r1.png")
    sprite_resized = pygame.transform.scale(sprite, (100, 100))
    sprites["menu"].append(sprite_resized)
sprites["menu"].append(pygame.transform.scale(sprites["pac_man"]["moving"]["left"][1], (100, 100)))


sounds = {"theme_music_remix": pygame.mixer.Sound(f"Sounds/theme_music_remix.wav"),
          "beginning": pygame.mixer.Sound(f"Sounds/beginning.wav"),
          "death": pygame.mixer.Sound(f"Sounds/death.wav"),
          "chomp": pygame.mixer.Sound(f"Sounds/chomp.wav"),
          "ghost_moving": pygame.mixer.Sound(f"Sounds/ghost_moving.wav")
          }

sounds["theme_music_remix"].set_volume(0.17)
sounds["theme_music_remix"].play(-1)

sounds["beginning"].set_volume(0.18)

# change the volume of the music
sounds["chomp"].set_volume(0.18)

sounds["ghost_moving"].set_volume(0.18)


main_font = pygame.font.SysFont("coopbl", 22)


start_level = 1  # the user will start at the level X
game_state = "menu"
# score for leaderboard
with open("score.txt", 'r') as file:  # open and read the score file
    all_score = [score.split("_,_") for score in file.read().splitlines()]  # make a list with all scores

for score in all_score:
    score[0] = int(score[0])  # make the score number an integer


BG_COLOR = (11, 11, 11)




# Creation ---------------------------------------------------------#
menu = me.Menu(SCREEN, sprites["menu"])


# Functions ------------------------------------------------------- #
def write_score(score, name):
    """write the score of the player in the score text file"""
    with open("score.txt", 'a') as score_file:
        text = f"{score}_,_{name}"
        score_file.write(text + "\n")


def redraw():
    SCREEN.fill(BG_COLOR)
    """ draw and make the game functional"""
    global game_state, world

    # when the user is in  the menu
    if game_state == "menu":
        if menu.do(key, all_score):
            game_state = "game"
            world = wo.World(SCREEN, sprites, sounds, start_level, BG_COLOR, menu.user_name)
            menu.reset()
            sounds["theme_music_remix"].stop()

    elif game_state == "game":
        if world.do() == "end":
            sounds["theme_music_remix"].play(-1)
            game_state = "menu"
            menu.menu_state = "leaderboard"
            write_score(world.player.score, world.user_name)
            all_score.append([world.player.score, world.user_name])


def buttons():
    global key

    key = None

    for event in pygame.event.get():

        if event.type == pygame.QUIT:  # if the user want to close the game
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            key = event.unicode

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_BACKSPACE:
                key = "delete_key"


def update():
    pygame.display.update()
    mainClock.tick(90)


def main():
    # Loop ------------------------------------------------------- #
    while True:
        # Buttons ------------------------------------------------ #
        buttons()

        # draw --------------------------------------------- #
        redraw()

        # Update ------------------------------------------------- #
        update()


if __name__ == '__main__':
    main()
