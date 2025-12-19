import pygame
import random
from constants import *
from player import Player
from enemy_salle2 import EnemySalle2  # On utilise les ennemis de la salle 2

class GameSalle2:

    def __init__(self):
        # Fenêtre
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ruines Mythologiques - Salle 2")

        # Background salle 2
        self.background_image = pygame.image.load("assets/images/background_room2.jpg")
        self.background_image = pygame.transform.scale(
            self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        # Joueur
        self.player = Player()

        # Ennemis
        self.enemies = pygame.sprite.Group()

        # États du jeu
        self.state = "intro"  # intro | combat | puzzle | transition
        self.game_over = False

        # Score
        self.score = 0
        self.font = pygame.font.Font(None, 32)
        self.game_over_font = pygame.font.Font(None, 80)

        # =====================
        # ÉNIGME SALLE 2
        # =====================
        self.puzzle_question = "Quel dieu protège la salle 2 ?"
        self.puzzle_answers = ["1. Athéna", "2. Poséidon", "3. Apollon"]
        self.correct_answer = 1
        self.attempts_left = 3

        # Vagues
        self.enemies_killed = 0
        self.enemies_needed = 20  # moins d'ennemis pour salle 2
        self.wave_active = True

        # Intro affichée
        self.intro_displayed = False

        # Lancer la première vague
        self.spawn_enemy()

        # Boucle principale
        self.running = True

    # =====================
    # Spawn ennemis salle 2
    # =====================
    def spawn_enemy(self):
        for _ in range(random.randint(2, 4)):
            x = SCREEN_WIDTH + random.randint(0, 300)
            y = GAME_FLOOR - random.randint(0, 120)
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
    # Reset complet salle 2
    # =====================
    def reset_game(self):
        self.player = Player()
        self.player.health = self.player.max_health
        self.enemies.empty()
        self.player.projectiles.empty()
        self.score = 0
        self.state = "intro"
        self.game_over = False
        self.attempts_left = 3
        self.wave_active = True
        self.enemies_killed = 0
        self.intro_displayed = False
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

            # =====================
            # Événements
            # =====================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    # Saut
                    if self.state == "combat" and not self.game_over and event.key == pygame.K_UP:
                        self.player.jump()

                    # Énigme
                    if self.state == "puzzle" and not self.game_over:
                        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                            answer = event.key - pygame.K_0
                            if answer == self.correct_answer:
                                self.state = "transition"
                            else:
                                self.attempts_left -= 1
                                if self.attempts_left <= 0:
                                    self.attempts_left = 3
                                    self.state = "combat"
                                    self.spawn_enemy()

                    # Rejouer après Game Over
                    if self.game_over and event.key == pygame.K_RETURN:
                        self.reset_game()

                # Tir souris
                if event.type == pygame.MOUSEBUTTONDOWN and self.state == "combat" and not self.game_over:
                    if event.button == 1:
                        self.player.shoot()

                # Spawn ennemis
                if event.type == SPAWN_ENEMY_EVENT and self.state == "combat" and not self.game_over and self.wave_active:
                    if len(self.enemies) < 4:
                        self.spawn_enemy()

            # =====================
            # LOGIQUE COMBAT
            # =====================
            if self.state == "combat" and not self.game_over:
                self.player.apply_gravity()

                for enemy in self.enemies:
                    enemy.move()

                for projectile in self.player.projectiles:
                    projectile.move()

                # Collisions projectiles / ennemis salle 2
                collisions = pygame.sprite.groupcollide(
                    self.player.projectiles,
                    self.enemies,
                    True,
                    False  # on ne supprime pas directement, car 2 coups nécessaires
                )
                for enemy_list in collisions.values():
                    for enemy in enemy_list:
                        enemy.take_damage(50)  # 50 par projectile
                        if enemy.health <= 0:
                            enemy.kill()
                            self.score += 1
                            self.enemies_killed += 1

                # Collision joueur / ennemis
                if pygame.sprite.spritecollide(self.player, self.enemies, False):
                    self.player.take_damage(20)

                # Game Over
                if self.player.health <= 0:
                    self.game_over = True

                # Passage à l’énigme
                if self.enemies_killed >= self.enemies_needed:
                    self.state = "puzzle"
                    self.wave_active = False

            # =====================
            # TRANSITION FIN ENIGME
            # =====================
            if self.state == "transition":
                self.screen.fill((0, 0, 0))
                text = self.game_over_font.render("Salle 1 suivante...", True, (255, 255, 255))
                self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
                pygame.display.flip()
                pygame.time.delay(2000)

                # On relance le jeu de la salle 1
                from game import Game
                game = Game()
                game.run()
                return  # quitte la salle 2

            # =====================
            # AFFICHAGE
            # =====================
            self.screen.blit(self.background_image, (0, 0))
            self.screen.blit(self.font.render(f"Score : {self.score}", True, (255, 0, 0)), (10, 10))

            # =====================
            # INTRO
            # =====================
            if self.state == "intro" and not self.intro_displayed:
                intro_lines = [
                    "Bienvenue dans la salle 2",
                    "Vous devez éliminer 20 ennemis avant de pouvoir",
                    "répondre à l'énigme et revenir à la salle 1"
                ]
                for i, line in enumerate(intro_lines):
                    text_surface = self.font.render(line, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50 + i * 40))
                    self.screen.blit(text_surface, text_rect)
                pygame.display.flip()
                pygame.time.delay(5000)
                self.state = "combat"
                self.intro_displayed = True

            # =====================
            # COMBAT
            # =====================
            if self.state == "combat" and not self.game_over:
                text_surface = self.font.render(
                    f"Ennemis tués : {self.enemies_killed} / {self.enemies_needed}", True, (0, 0, 0)
                )
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
                self.screen.blit(text_surface, text_rect)

            # =====================
            # ÉNIGME
            # =====================
            if self.state == "puzzle" and not self.game_over:
                question_surface = self.font.render(self.puzzle_question, True, (0, 0, 0))
                question_rect = question_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
                self.screen.blit(question_surface, question_rect)

                for i, ans in enumerate(self.puzzle_answers):
                    ans_surface = self.font.render(ans, True, (0, 0, 0))
                    ans_rect = ans_surface.get_rect(center=(SCREEN_WIDTH // 2, 100 + i * 40))
                    self.screen.blit(ans_surface, ans_rect)

                attempts_surface = self.font.render(
                    f"Tentatives restantes : {self.attempts_left}", True, (255, 0, 0)
                )
                attempts_rect = attempts_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
                self.screen.blit(attempts_surface, attempts_rect)

            # =====================
            # Joueur et sprites
            # =====================
            self.screen.blit(self.player.image, self.player.rect)
            self.player.draw_health_bar(self.screen)
            for enemy in self.enemies:
                self.screen.blit(enemy.image, enemy.rect)
                enemy.draw_health_bar(self.screen)
            self.player.projectiles.draw(self.screen)

            # =====================
            # GAME OVER
            # =====================
            if self.game_over:
                self.screen.fill((0, 0, 0))
                self.screen.blit(
                    self.game_over_font.render("GAME OVER", True, (255, 0, 0)),
                    (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 40)
                )
                replay_text = self.font.render("Appuyez sur ENTREE pour rejouer", True, (255, 255, 255))
                self.screen.blit(replay_text, replay_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

            pygame.display.flip()
