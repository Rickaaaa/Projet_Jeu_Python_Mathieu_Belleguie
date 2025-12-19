import pygame
from constants import *

class ProjectileBoss(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=start_pos)
        # Calculer la direction vers le joueur
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = (dx**2 + dy**2) ** 0.5
        self.speed = 6
        if distance != 0:
            self.velocity = (dx / distance * self.speed, dy / distance * self.speed)
        else:
            self.velocity = (0, 0)

    def move(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # Supprimer si sort de l'écran
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
