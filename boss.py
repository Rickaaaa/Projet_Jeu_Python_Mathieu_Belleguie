import pygame
import random
from projectile_boss import ProjectileBoss
from constants import *

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/images/boss.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.health = 300  # Vie du boss
        self.max_health = 300
        self.speed = 2
        self.direction = 1  # 1 = droite, -1 = gauche
        self.shoot_cooldown = 90  # frames entre chaque tir
        self.shoot_timer = 0

    def move(self):
        # Déplacement horizontal simple de gauche à droite
        self.rect.x += self.speed * self.direction
        if self.rect.right >= SCREEN_WIDTH - 50:
            self.direction = -1
        elif self.rect.left <= 50:
            self.direction = 1

        # Timer pour tir
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def shoot(self, player_pos):
        # Tir si cooldown terminé
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_cooldown
            return ProjectileBoss(self.rect.center, player_pos)
        return None

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw_health_bar(self, screen):
        # Barre de vie au-dessus du boss
        bar_width = 100
        bar_height = 10
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.rect.centerx - bar_width // 2, self.rect.top - 20, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.centerx - bar_width // 2, self.rect.top - 20, fill, bar_height)
        pygame.draw.rect(screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), outline_rect, 2)
