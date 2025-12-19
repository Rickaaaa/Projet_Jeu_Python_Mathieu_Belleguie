import pygame
from constants import *

class Projectile(pygame.sprite.Sprite):
    
    # Cache pour optimiser (éviter le lag quand on spam)
    image_cache = None

    def __init__(self, x, y, vertical=False, target_pos=None):
        super().__init__()
        
        # Chargement intelligent de l'image
        if Projectile.image_cache is None:
            img = pygame.image.load("assets/images/arme1.png").convert_alpha()
            Projectile.image_cache = pygame.transform.scale(img, (40, 40))
        
        # On prend l'image du cache
        self.image = Projectile.image_cache
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Vitesse de base
        self.speed = 8
        self.speed_x = 0
        self.speed_y = 0

        # --- LOGIQUE TIR VERTICAL ---
        if vertical:
            self.speed_x = 0
            self.speed_y = -self.speed
            # AJOUT : On pivote l'image de 90 degrés vers la gauche (pour pointer en haut)
            self.image = pygame.transform.rotate(self.image, 90)
            # On met à jour le rect car la rotation change les dimensions
            self.rect = self.image.get_rect(center=(x, y))

        # Tir vers une position spécifique (ex: Boss qui vise joueur)
        elif target_pos is not None:
            dx = target_pos[0] - x
            dy = target_pos[1] - y
            distance = max((dx**2 + dy**2) ** 0.5, 1) 
            self.speed_x = dx / distance * self.speed
            self.speed_y = dy / distance * self.speed
            
        # Tir horizontal classique
        else:
            self.speed_x = self.speed
            self.speed_y = 0

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Supprimer le projectile s'il sort de l'écran
        if (self.rect.right > SCREEN_WIDTH or
            self.rect.left < 0 or
            self.rect.bottom < 0 or
            self.rect.top > SCREEN_HEIGHT):
            self.kill()