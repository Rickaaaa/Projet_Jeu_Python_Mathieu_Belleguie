import pygame
from constants import *

class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/images/bat.png")
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3

    def move(self):
        self.rect.x -= self.speed

        # Supprimer l'ennemi s'il sort de l'écran
        if self.rect.right < 0:
            self.kill()
