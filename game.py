import pygame
import random
from constants import *
from player import Player
from enemy import Enemy
from enemy_salle2 import EnemySalle2
from boss import Boss
from projectile import Projectile

class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ruines Mythologiques")

        # Décors par salle
        self.backgrounds = [
            "assets/images/background_room1.jpg",
            "assets/images/background_room2.jpg",
        ]
        self.current_room = 0
        self.background_image = pygame.image.load(self.backgrounds[self.current_room])
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # --- GESTION DU SOL ---
        # Salle 1 (défaut) : Le sol est à 500
        self.level_floor = GAME_FLOOR

        # Joueur
        self.player = Player()
        self.player.floor_y = self.level_floor 
        self.player.rect.y = self.level_floor

        # Ennemis
        self.enemies = pygame.sprite.Group()

        # États du jeu
        self.state = "intro" 
        self.game_over = False

        # Score
        self.score = 0
        self.font = pygame.font.Font(None, 32)
        self.game_over_font = pygame.font.Font(None, 80)

        # Énigme
        self.puzzle_question = "Quel dieu gardait les temples ?"
        self.puzzle_answers = ["1. Anubis", "2. Zeus", "3. Hadès"]
        self.correct_answer = 1
        
        # --- MODIFICATION ---
        # On passe à 2 tentatives pour éviter le "brute force"
        self.attempts_left = 2

        # Vagues
        self.enemies_killed = 0
        self.enemies_needed = 30
        self.wave_active = True

        # Salle 3 (boss)
        self.boss = None
        self.boss_projectiles = pygame.sprite.Group()
        self.boss_defeated = False

        self.intro_displayed = False
        self.spawn_enemy()
        self.running = True

    # =====================
    # Spawn ennemis
    # =====================
    def spawn_enemy(self):
        for _ in range(random.randint(2, 4)):
            x = SCREEN_WIDTH + random.randint(0, 300)
            
            # Les ennemis apparaissent sur le sol actuel
            y = self.level_floor - random.randint(0, 120)
            
            if self.current_room == 0:
                self.enemies.add(Enemy(x, y))
            else:
                self.enemies.add(EnemySalle2(x, y))
        self.wave_active = True

    # =====================
    # Déplacement joueur
    # =====================
    def keyboard(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()
        elif keys[pygame.K_LEFT]:
            self.player.move_left()

    # =====================
    # Reset complet
    # =====================
    def reset_game(self):
        # Reset au sol par défaut (Salle 1)
        self.level_floor = GAME_FLOOR
        
        self.player = Player()
        self.player.floor_y = self.level_floor
        self.player.health = self.player.max_health
        
        self.enemies.empty()
        self.player.projectiles.empty()
        self.boss_projectiles.empty()
        self.score = 0
        self.state = "intro"
        self.game_over = False
        self.current_room = 0
        
        # --- MODIFICATION ---
        # Reset à 2 tentatives
        self.attempts_left = 2
        
        self.wave_active = True
        self.enemies_killed = 0
        self.intro_displayed = False
        
        # Reset question Salle 1
        self.puzzle_question = "Quel dieu gardait les temples ?"
        self.puzzle_answers = ["1. Anubis", "2. Zeus", "3. Hadès"]
        self.correct_answer = 1
        
        self.background_image = pygame.image.load(self.backgrounds[self.current_room])
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.spawn_enemy()

    # =====================
    # Boucle principale
    # =====================
    def run(self):
        clock = pygame.time.Clock()
        SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWN_ENEMY_EVENT, 2000)

        while self.running:
            clock.tick(60)
            self.keyboard()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if self.state in ["combat", "combat_boss"] and not self.game_over and event.key == pygame.K_UP:
                        self.player.jump()

                    if self.state == "puzzle" and not self.game_over:
                        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                            answer = event.key - pygame.K_0
                            if answer == self.correct_answer:
                                if self.current_room == 0:
                                    self.state = "transition_salle2"
                                elif self.current_room == 1:
                                    self.state = "transition_salle3"
                            else:
                                self.attempts_left -= 1
                                if self.attempts_left <= 0:
                                    # --- MODIFICATION ---
                                    # Si on rate, on remet à 2 tentatives pour la prochaine fois
                                    self.attempts_left = 2
                                    self.state = "combat"
                                    self.spawn_enemy()

                    if self.game_over and event.key == pygame.K_RETURN:
                        self.reset_game()

                if event.type == pygame.MOUSEBUTTONDOWN and self.state in ["combat", "combat_boss"] and not self.game_over:
                    if event.button == 1:
                        if self.current_room == 2:
                            self.player.shoot(target_y=0)
                        else:
                            self.player.shoot()

                if event.type == SPAWN_ENEMY_EVENT and self.state == "combat" and not self.game_over and self.wave_active:
                    if len(self.enemies) < 4:
                        self.spawn_enemy()

            # =====================
            # Transition salle 2
            # =====================
            if self.state == "transition_salle2":
                countdown = 3
                font_big = pygame.font.Font(None, 60)
                font_small = pygame.font.Font(None, 40)
                for i in range(countdown, 0, -1):
                    self.screen.fill((0, 0, 0))
                    msg1 = font_big.render("Bravo, vous avez réussi la salle 1 !", True, (255, 255, 255))
                    msg2 = font_small.render(f"Vous allez entrer dans la salle 2 dans {i}...", True, (255, 255, 255))
                    self.screen.blit(msg1, msg1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
                    self.screen.blit(msg2, msg2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
                    pygame.display.flip()
                    pygame.time.delay(1000)

                self.current_room = 1
                
                # --- HAUTEUR SALLE 2 (Ta valeur : 530) ---
                self.level_floor = 530  
                
                self.player.floor_y = self.level_floor
                self.player.rect.y = self.player.floor_y - self.player.rect.height
                
                self.background_image = pygame.image.load(self.backgrounds[self.current_room])
                self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.enemies.empty()
                self.spawn_enemy()
                
                self.player.health = self.player.max_health
                self.enemies_needed = 15
                self.state = "combat"
                self.enemies_killed = 0
                self.wave_active = True

            # =====================
            # Transition salle 3 (boss)
            # =====================
            if self.state == "transition_salle3":
                countdown = 3
                font_big = pygame.font.Font(None, 60)
                font_small = pygame.font.Font(None, 40)
                for i in range(countdown, 0, -1):
                    self.screen.fill((0, 0, 0))
                    msg1 = font_big.render("Bravo, vous avez réussi la salle 2 !", True, (255, 255, 255))
                    msg2 = font_small.render(f"Le boss arrive dans {i}...", True, (255, 255, 255))
                    self.screen.blit(msg1, msg1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
                    self.screen.blit(msg2, msg2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
                    pygame.display.flip()
                    pygame.time.delay(1000)

                self.current_room = 2
                self.backgrounds.append("assets/images/background_room3.jpg")
                self.background_image = pygame.image.load(self.backgrounds[self.current_room])
                self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # --- HAUTEUR SALLE 3 (Ta valeur : 550) ---
                self.level_floor = 550  
                
                self.player.floor_y = self.level_floor
                self.player.rect.y = self.player.floor_y - self.player.rect.height
                self.player.health = self.player.max_health

                self.boss = Boss(SCREEN_WIDTH // 2, self.level_floor - 150)
                self.boss_projectiles.empty()

                self.state = "combat_boss"

            # =====================
            # LOGIQUE COMBAT
            # =====================
            if self.state == "combat" and not self.game_over:
                self.player.apply_gravity()
                for enemy in self.enemies:
                    enemy.move()
                for projectile in self.player.projectiles:
                    projectile.move()

                collisions = pygame.sprite.groupcollide(self.player.projectiles, self.enemies, True, False)
                for projectile, enemies_hit in collisions.items():
                    for enemy in enemies_hit:
                        if hasattr(enemy, 'take_damage'):
                            enemy.take_damage()
                            if enemy.health <= 0:
                                enemy.kill()
                                self.score += 1
                                self.enemies_killed += 1
                        else:
                            enemy.kill()
                            self.score += 1
                            self.enemies_killed += 1

                if pygame.sprite.spritecollide(self.player, self.enemies, True):
                    self.player.take_damage(20)

                if self.player.health <= 0:
                    self.game_over = True

                if self.enemies_killed >= self.enemies_needed:
                    self.state = "puzzle"
                    self.wave_active = False

                    # Questions
                    if self.current_room == 0:
                        self.puzzle_question = "Quel dieu gardait les temples ?"
                        self.puzzle_answers = ["1. Anubis", "2. Zeus", "3. Hadès"]
                        self.correct_answer = 1
                    elif self.current_room == 1:
                        self.puzzle_question = "A quoi servaient les pyramides ?"
                        self.puzzle_answers = ["1. Maisons", "2. Tombeaux", "3. Greniers"]
                        self.correct_answer = 2

            # =====================
            # LOGIQUE BOSS
            # =====================
            if self.state == "combat_boss" and not self.game_over:
                self.player.apply_gravity()
                
                # --- CORRECTION : AJOUTE CES 2 LIGNES ICI ---
                for projectile in self.player.projectiles:
                    projectile.move()
                # ---------------------------------------------

                if self.boss:
                    self.boss.move()
                    projectile = self.boss.shoot(self.player.rect.center)
                    if projectile:
                        self.boss_projectiles.add(projectile)

                for proj in self.boss_projectiles:
                    proj.move()
                
                # ... (la suite reste la même : collisions, etc.)
                if pygame.sprite.spritecollide(self.player, self.boss_projectiles, True):
                    self.player.take_damage(20)

            # =====================
            # AFFICHAGE
            # =====================
            self.screen.blit(self.background_image, (0, 0))
            self.screen.blit(self.font.render(f"Score : {self.score}", True, (255, 0, 0)), (10, 10))

            if self.state == "intro" and not self.intro_displayed:
                intro_lines = [
                    "Bienvenue dans la salle 1",
                    "Vous devez éliminer 30 ennemis avant de pouvoir",
                    "répondre à l'énigme et accéder à la salle 2"
                ]
                for i, line in enumerate(intro_lines):
                    text_surface = self.font.render(line, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50 + i * 40))
                    self.screen.blit(text_surface, text_rect)
                pygame.display.flip()
                pygame.time.delay(5000)
                self.state = "combat"
                self.intro_displayed = True

            if self.state in ["combat", "combat_boss"] and not self.game_over:
                color = (255, 255, 255) if self.current_room == 1 else (0, 0, 0)
                if self.state == "combat":
                    text_surface = self.font.render(
                        f"Ennemis tués : {self.enemies_killed} / {self.enemies_needed}", True, color
                    )
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
                    self.screen.blit(text_surface, text_rect)

            if self.state == "puzzle" and not self.game_over:
                color = (255, 255, 255) if self.current_room == 1 else (0, 0, 0)
                question_surface = self.font.render(self.puzzle_question, True, color)
                question_rect = question_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
                self.screen.blit(question_surface, question_rect)
                for i, ans in enumerate(self.puzzle_answers):
                    ans_surface = self.font.render(ans, True, color)
                    ans_rect = ans_surface.get_rect(center=(SCREEN_WIDTH // 2, 100 + i * 40))
                    self.screen.blit(ans_surface, ans_rect)
                attempts_surface = self.font.render(f"Tentatives restantes : {self.attempts_left}", True, (255, 0, 0))
                attempts_rect = attempts_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
                self.screen.blit(attempts_surface, attempts_rect)

            self.screen.blit(self.player.image, self.player.rect)
            self.player.draw_health_bar(self.screen)
            for enemy in self.enemies:
                self.screen.blit(enemy.image, enemy.rect)
                if hasattr(enemy, 'draw_health_bar'):
                    enemy.draw_health_bar(self.screen)
            self.player.projectiles.draw(self.screen)
            self.boss_projectiles.draw(self.screen)

            if self.boss:
                self.screen.blit(self.boss.image, self.boss.rect)
                self.boss.draw_health_bar(self.screen)

            if self.state == "victory":
                self.screen.fill((0, 0, 0))
                victory_text = self.font.render("BRAVO ! Vous avez vaincu le boss !", True, (255, 255, 255))
                self.screen.blit(victory_text, victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

            if self.game_over:
                self.screen.fill((0, 0, 0))
                self.screen.blit(
                    self.game_over_font.render("GAME OVER", True, (255, 0, 0)),
                    (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 40)
                )
                replay_text = self.font.render("Appuyez sur ENTREE pour rejouer", True, (255, 255, 255))
                self.screen.blit(replay_text, replay_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

            pygame.display.flip()