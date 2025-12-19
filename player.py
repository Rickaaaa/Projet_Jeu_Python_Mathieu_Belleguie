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
        
        # --- MODIFICATION ---
        # On définit le sol actuel du joueur (initialisé avec la constante par défaut)
        self.floor_y = GAME_FLOOR
        
        self.rect.x = 100
        self.rect.y = self.floor_y

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

        # --- MODIFICATION ---
        # On utilise self.floor_y au lieu de la constante globale GAME_FLOOR
        if self.rect.y >= self.floor_y:
            self.rect.y = self.floor_y
            self.velocity_y = 0
            self.on_ground = True

    # Tir avec option verticale
    def shoot(self, target=None, target_y=None):
        if target_y is not None:
            projectile = Projectile(
                self.rect.centerx,
                self.rect.top,
                target_pos=(self.rect.centerx, target_y)
            )
        elif target:
            projectile = Projectile(
                self.rect.centerx,
                self.rect.centery,
                target_pos=(target.rect.centerx, target.rect.centery)
            )
        else:
            projectile = Projectile(
                self.rect.right,
                self.rect.centery
            )
        self.projectiles.add(projectile)


    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw_health_bar(self, screen):
        bar_width = 80
        bar_height = 8

        x = self.rect.x + 10
        y = self.rect.y - 25

        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (0, 255, 0), (x, y, bar_width * health_ratio, bar_height))

        health_text = pygame.font.Font(None, 20).render(
            f"{self.health} / {self.max_health} PV", True, (0, 0, 0)
        )
        screen.blit(health_text, (x, y - 15))