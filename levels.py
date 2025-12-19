import pygame
import random
from constants import *
from enemy import Enemy
from enemy_salle2 import EnemySalle2
from boss import Boss

class Room1:
    def __init__(self):
        self.id = 0
        self.floor_y = GAME_FLOOR # 500 par défaut
        self.enemies_needed = 30
        
        # Décors
        self.bg_image = pygame.image.load("assets/images/background_room1.jpg")
        self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Texte d'intro
        self.intro_lines = [
            "Bienvenue dans la salle 1...",
            "Vous devez éliminer 30 ennemis",
            "afin d'atteindre l'énigme",
            "et peut-être la salle suivante."
        ]
        
        # Énigme
        self.puzzle_question = "Quel dieu gardait les temples ?"
        self.puzzle_answers = ["1. Anubis", "2. Zeus", "3. Hadès"]
        self.correct_answer = 1

    def spawn_enemies(self, enemy_group, floor_y):
        # Spawn classique (Ennemis Salle 1)
        for _ in range(random.randint(2, 4)):
            x = SCREEN_WIDTH + random.randint(0, 300)
            y = floor_y - random.randint(0, 120)
            enemy_group.add(Enemy(x, y))

class Room2:
    def __init__(self):
        self.id = 1
        self.floor_y = 530 # Sol un peu plus haut
        self.enemies_needed = 15
        
        # Décors
        self.bg_image = pygame.image.load("assets/images/background_room2.jpg")
        self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Texte d'intro
        self.intro_lines = [
            "Bienvenue dans la salle 2...",
            "Les gardiens antiques vous attendent.",
            "Eliminez 15 ennemis",
            "pour affronter le Boss Final."
        ]
        
        # Énigme
        self.puzzle_question = "A quoi servaient les pyramides ?"
        self.puzzle_answers = ["1. Maisons", "2. Tombeaux", "3. Greniers"]
        self.correct_answer = 2

    def spawn_enemies(self, enemy_group, floor_y):
        # Spawn Salle 2 (Pyramides volantes)
        for _ in range(random.randint(2, 4)):
            x = SCREEN_WIDTH + random.randint(0, 300)
            y = floor_y - random.randint(0, 120)
            enemy_group.add(EnemySalle2(x, y))

class RoomBoss:
    def __init__(self):
        self.id = 2
        self.floor_y = 550 # Sol encore plus haut
        self.enemies_needed = 0 # Pas de vagues, juste le boss
        
        # Décors
        self.bg_image = pygame.image.load("assets/images/background_room3.jpg")
        self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Texte d'intro
        self.intro_lines = [
            "ATTENTION !",
            "Le Gardien Suprême est réveillé.",
            "Esquivez ses projectiles",
            "et tirez vers le haut pour vaincre !"
        ]
        
        # Énigme Finale (après le boss)
        self.puzzle_question = "Qui est le pharaon au masque d'or ?"
        self.puzzle_answers = ["1. Khéops", "2. Toutânkhamon", "3. Ramsès II"]
        self.correct_answer = 2

    def spawn_boss(self, floor_y):
        return Boss(SCREEN_WIDTH // 2, floor_y - 150)