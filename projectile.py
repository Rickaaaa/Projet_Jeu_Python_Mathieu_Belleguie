import pygame

class Projectile(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/images/arme1.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 8

    def move(self):
        self.rect.x += self.speed

        # Supprimer le tir s'il sort de l'écran
        if self.rect.left > 1080:
            self.kill()
