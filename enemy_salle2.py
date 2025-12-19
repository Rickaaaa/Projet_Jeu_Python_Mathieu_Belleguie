import pygame
from constants import *

class EnemySalle2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Image spécifique ou différente de salle 1
        self.image = pygame.image.load("assets/images/enemy2.png")
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Statistiques
        self.speed = 3
        self.max_health = 2  # 2 coups pour mourir
        self.health = 2

    def move(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

    def take_damage(self, amount=1):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        # Barre au-dessus de l'ennemi
        bar_width = 40
        bar_height = 5
        x = self.rect.x + (self.rect.width - bar_width) // 2
        y = self.rect.y - 10

        # Fond rouge
        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
        # Vie restante verte
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (0, 255, 0), (x, y, bar_width * health_ratio, bar_height))
