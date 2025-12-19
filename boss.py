import pygame
import random
from projectile_boss import ProjectileBoss
from constants import *


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Image
        self.image = pygame.image.load("assets/images/boss.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect(midbottom=(x, y))

        # Vie
        self.max_health = 300
        self.health = 300

        # Déplacement
        self.speed = 2
        self.direction = 1  # 1 = droite, -1 = gauche

        # États du boss
        self.state = "move"  # move | shoot
        self.state_timer = 180

        # Tir
        self.shoot_cooldown = 90
        self.shoot_timer = 0

        # Tir en rafale
        self.shots_left = 0
        self.rapid_fire_delay = 15
        self.rapid_fire_timer = 0

    # =====================
    # Déplacement + logique boss
    # =====================
    def move(self):
        # Gestion des états
        self.state_timer -= 1
        if self.state_timer <= 0:
            if self.state == "move":
                self.state = "shoot"
                self.state_timer = 120
                self.shots_left = random.randint(3, 6)
            else:
                self.state = "move"
                self.state_timer = 180

        # Déplacement seulement en état MOVE
        if self.state == "move":
            self.rect.x += self.speed * self.direction
            if self.rect.right >= SCREEN_WIDTH - 50:
                self.direction = -1
            elif self.rect.left <= 50:
                self.direction = 1

        # Timers
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1

    # =====================
    # Tir du boss
    # =====================
    def shoot(self, player_pos):
        if self.state != "shoot":
            return None

        if self.shots_left > 0 and self.rapid_fire_timer <= 0:
            self.rapid_fire_timer = self.rapid_fire_delay
            self.shots_left -= 1
            return ProjectileBoss(self.rect.center, player_pos)

        return None

    # =====================
    # Dégâts
    # =====================
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    # =====================
    # Barre de vie
    # =====================
    def draw_health_bar(self, screen):
        bar_width = 100
        bar_height = 10
        health_ratio = self.health / self.max_health

        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 20

        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
