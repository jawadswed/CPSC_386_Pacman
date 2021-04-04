
import time


class Anim:
    def __init__(self, sprites, speed=1):
        self.sprite = sprites
        self.current_sprite = self.sprite[0]
        self.speed = speed
        self.timer = 0
        self.s_index = 0

    def do(self):
        t = time.time()
        if t > self.timer:
            self.timer = t + self.speed
            self.s_index += 1
            if self.s_index > len(self.sprite) - 1:
                self.s_index = 0
                return "end"
            self.current_sprite = self.sprite[self.s_index]
