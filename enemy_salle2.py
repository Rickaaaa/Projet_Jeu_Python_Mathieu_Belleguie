import pygame
from constants import *
import os

class EnemySalle2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Charger l'image de l'ennemi
        self.image = pygame.image.load(os.path.join("assets/images/enemy2.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # adapter la taille si nécessaire
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Barre de vie
        self.max_health = 100
        self.health = self.max_health

        # Vitesse
        self.speed = 2

    def move(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

    def take_damage(self, amount=50):
        self.health -= amount

    def draw_health_bar(self, screen):
        bar_width = self.rect.width
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)
        pygame.draw.rect(screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(screen, (0, 0, 0), outline_rect, 1)
