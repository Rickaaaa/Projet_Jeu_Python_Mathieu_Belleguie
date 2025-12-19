import pygame
from constants import *

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, vertical=False, target_pos=None):
        super().__init__()
        self.image = pygame.image.load("assets/images/arme1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = 8
        self.speed_x = 0
        self.speed_y = 0

        if vertical:
            self.speed_x = 0
            self.speed_y = -self.speed
        elif target_pos is not None:
            dx = target_pos[0] - x
            dy = target_pos[1] - y
            distance = max((dx**2 + dy**2) ** 0.5, 1) 
            self.speed_x = dx / distance * self.speed
            self.speed_y = dy / distance * self.speed
        else:
            self.speed_x = self.speed
            self.speed_y = 0

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if (self.rect.right > SCREEN_WIDTH or
            self.rect.left < 0 or
            self.rect.bottom < 0 or
            self.rect.top > SCREEN_HEIGHT):
            self.kill()