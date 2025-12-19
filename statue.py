import pygame

class Statue(pygame.sprite.Sprite):

    def __init__(self, x, y, symbol, image_path):
        super().__init__()
        self.symbol = symbol
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.activated = False

    def activate(self):
        self.activated = True
