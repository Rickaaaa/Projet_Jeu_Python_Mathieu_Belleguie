import pygame
import random
from constants import *
from projectile import Projectile

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/images/boss.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.max_health = 300
        self.health = 300
        self.speed = 2
        self.direction = 1 

        self.state = "move"
        self.state_timer = 180
        self.shoot_cooldown = 90
        self.shoot_timer = 0
        self.shots_left = 0
        self.rapid_fire_delay = 15
        self.rapid_fire_timer = 0

    def move(self):
        self.state_timer -= 1
        if self.state_timer <= 0:
            if self.state == "move":
                self.state = "shoot"
                self.state_timer = 120
                self.shots_left = random.randint(3, 6)
            else:
                self.state = "move"
                self.state_timer = 180

        if self.state == "move":
            self.rect.x += self.speed * self.direction
            if self.rect.right >= SCREEN_WIDTH - 50:
                self.direction = -1
            elif self.rect.left <= 50:
                self.direction = 1

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1

    def shoot(self, player_pos):
        if self.state != "shoot":
            return None

        if self.shots_left > 0 and self.rapid_fire_timer <= 0:
            self.rapid_fire_timer = self.rapid_fire_delay
            self.shots_left -= 1
            return Projectile(self.rect.centerx, self.rect.centery, target_pos=player_pos)

        return None

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw_health_bar(self, screen):
        bar_width = 100
        bar_height = 10
        health_ratio = self.health / self.max_health

        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 20

        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)