import pygame
from constants import *
from projectile import Projectile


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        # Image
        self.image = pygame.image.load('assets/images/player.png')
        self.image = pygame.transform.scale(
            self.image, (PLAYER_WIDTH, PLAYER_HEIGHT)
        )
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = GAME_FLOOR

        # Déplacement
        self.speed = 5

        # Saut / gravité
        self.velocity_y = 0
        self.on_ground = True

        # Projectiles
        self.projectiles = pygame.sprite.Group()

        # ❤️ Vie
        self.max_health = 100
        self.health = 100

    def move_right(self):
        if self.rect.x + self.speed + PLAYER_WIDTH < SCREEN_WIDTH:
            self.rect.x += self.speed

    def move_left(self):
        if self.rect.x - self.speed > 0:
            self.rect.x -= self.speed

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_FORCE
            self.on_ground = False

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        if self.rect.y >= GAME_FLOOR:
            self.rect.y = GAME_FLOOR
            self.velocity_y = 0
            self.on_ground = True

    def shoot(self):
        projectile = Projectile(
            self.rect.right,
            self.rect.centery
        )
        self.projectiles.add(projectile)

    # ❤️ Prendre des dégâts
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    # ❤️ Dessiner la barre de vie avec texte PV
    def draw_health_bar(self, screen):
        bar_width = 80
        bar_height = 8

        # Position au-dessus du joueur
        x = self.rect.x + 10
        y = self.rect.y - 25  # un peu plus haut pour le texte

        # Fond rouge
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            (x, y, bar_width, bar_height)
        )

        # Barre verte (vie restante)
        health_ratio = self.health / self.max_health
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (x, y, bar_width * health_ratio, bar_height)
        )

        # Afficher le texte des PV
        health_text = pygame.font.Font(None, 20).render(
            f"{self.health} / {self.max_health} PV", True, (0, 0, 0)
        )
        screen.blit(health_text, (x, y - 15))
