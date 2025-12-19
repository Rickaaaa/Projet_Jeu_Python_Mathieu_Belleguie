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

        # --- CHARGEMENT DES IMAGES ---
        # Image de l'écran titre
        try:
            self.menu_background = pygame.image.load("assets/images/loading_background.jpg")
            self.menu_background = pygame.transform.scale(self.menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            self.menu_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.menu_background.fill((0, 0, 0))

        # Décors par salle
        self.backgrounds = [
            "assets/images/background_room1.jpg",
            "assets/images/background_room2.jpg",
        ]
        self.current_room = 0
        self.background_image = pygame.image.load(self.backgrounds[self.current_room])
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # --- GESTION DU SOL ---
        self.level_floor = GAME_FLOOR

        # Joueur
        self.player = Player()
        self.player.floor_y = self.level_floor 
        self.player.rect.y = self.level_floor

        # Ennemis
        self.enemies = pygame.sprite.Group()

        # États du jeu
        self.state = "start_menu" 
        self.game_over = False

        # Score et Polices
        self.score = 0
        self.font = pygame.font.Font(None, 32)
        self.font_title = pygame.font.Font(None, 90)
        self.font_subtitle = pygame.font.Font(None, 40)
        self.game_over_font = pygame.font.Font(None, 80)

        # Énigme
        self.puzzle_question = "Quel dieu gardait les temples ?"
        self.puzzle_answers = ["1. Anubis", "2. Zeus", "3. Hadès"]
        self.correct_answer = 1
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
        if self.current_room < 2:
            for _ in range(random.randint(2, 4)):
                x = SCREEN_WIDTH + random.randint(0, 300)
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
    # CHECKPOINT / RESET
    # =====================
    def reset_game(self):
        self.player.health = self.player.max_health
        self.game_over = False
        self.enemies.empty()
        self.player.projectiles.empty()
        self.boss_projectiles.empty()
        self.attempts_left = 2

        # --- CHECKPOINT ---
        if self.current_room == 0:
            # RESET SALLE 1 -> MENU
            self.level_floor = GAME_FLOOR
            self.score = 0
            self.state = "start_menu" 
            self.intro_displayed = False
            self.wave_active = True
            self.enemies_killed = 0
            self.enemies_needed = 30
            self.puzzle_question = "Quel dieu gardait les temples ?"
            self.puzzle_answers = ["1. Anubis", "2. Zeus", "3. Hadès"]
            self.correct_answer = 1
            self.spawn_enemy()

        elif self.current_room == 1:
            # RESET SALLE 2
            self.level_floor = 530
            self.state = "combat"
            self.wave_active = True
            self.enemies_killed = 0
            self.enemies_needed = 15
            self.puzzle_question = "A quoi servaient les pyramides ?"
            self.puzzle_answers = ["1. Maisons", "2. Tombeaux", "3. Greniers"]
            self.correct_answer = 2
            self.spawn_enemy()

        elif self.current_room == 2:
            # RESET SALLE 3 (BOSS)
            self.level_floor = 550
            self.state = "combat_boss"
            self.boss = Boss(SCREEN_WIDTH // 2, self.level_floor - 150)
            self.boss_defeated = False

        self.player.floor_y = self.level_floor
        self.player.rect.y = self.player.floor_y - self.player.rect.height
        
        if self.current_room < len(self.backgrounds):
            bg_path = self.backgrounds[self.current_room]
            self.background_image = pygame.image.load(bg_path)
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # =====================
    # Boucle principale
    # =====================
    def run(self):
        clock = pygame.time.Clock()
        SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWN_ENEMY_EVENT, 2000)

        while self.running:
            clock.tick(60)
            
            if self.state not in ["start_menu", "victory", "game_over"]:
                self.keyboard()

            # --- ÉVÉNEMENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    # MENU
                    if self.state == "start_menu":
                        if event.key == pygame.K_RETURN:
                            self.state = "intro"
                    
                    # SAUT
                    if self.state in ["combat", "combat_boss"] and not self.game_over and event.key == pygame.K_UP:
                        self.player.jump()

                    # ÉNIGME
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
                                    self.attempts_left = 2
                                    self.state = "combat"
                                    self.enemies_killed = 0
                                    self.spawn_enemy()

                    # RESET GAME OVER
                    if self.game_over and event.key == pygame.K_RETURN:
                        self.reset_game()

                # TIR
                if event.type == pygame.MOUSEBUTTONDOWN and self.state in ["combat", "combat_boss"] and not self.game_over:
                    if event.button == 1:
                        if self.current_room == 2:
                            self.player.shoot(target_y=0)
                        else:
                            self.player.shoot()

                # SPAWN
                if event.type == SPAWN_ENEMY_EVENT and self.state == "combat" and not self.game_over and self.wave_active:
                    if len(self.enemies) < 4:
                        self.spawn_enemy()
            
            if not self.running:
                break

            # =====================
            # TRANSITIONS
            # =====================
            if self.state == "transition_salle2":
                countdown = 3
                font_big = pygame.font.Font(None, 60)
                font_small = pygame.font.Font(None, 40)
                for i in range(countdown, 0, -1):
                    self.screen.fill((0, 0, 0))
                    msg1 = font_big.render("Bravo, vous avez réussi la salle 1 !", True, (255, 255, 255))
                    msg2 = font_small.render(f"Salle 2 dans {i}...", True, (255, 255, 255))
                    self.screen.blit(msg1, msg1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
                    self.screen.blit(msg2, msg2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
                    pygame.display.flip()
                    pygame.time.delay(1000)

                self.current_room = 1
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

            if self.state == "transition_salle3":
                countdown = 3
                font_big = pygame.font.Font(None, 60)
                font_small = pygame.font.Font(None, 40)
                for i in range(countdown, 0, -1):
                    self.screen.fill((0, 0, 0))
                    msg1 = font_big.render("Bravo, vous avez réussi la salle 2 !", True, (255, 255, 255))
                    msg2 = font_small.render(f"BOSS FINAL dans {i}...", True, (255, 255, 255))
                    self.screen.blit(msg1, msg1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
                    self.screen.blit(msg2, msg2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
                    pygame.display.flip()
                    pygame.time.delay(1000)

                self.current_room = 2
                self.backgrounds.append("assets/images/background_room3.jpg")
                self.background_image = pygame.image.load(self.backgrounds[self.current_room])
                self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.level_floor = 550  
                self.player.floor_y = self.level_floor
                self.player.rect.y = self.player.floor_y - self.player.rect.height
                self.player.health = self.player.max_health
                self.enemies.empty()
                self.boss = Boss(SCREEN_WIDTH // 2, self.level_floor - 150)
                self.boss_projectiles.empty()
                self.state = "combat_boss"

            # =====================
            # LOGIQUES JEU
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
                if self.enemies_killed >= self.enemies_needed:
                    self.state = "puzzle"
                    self.wave_active = False
                    if self.current_room == 0:
                        self.puzzle_question = "Quel dieu gardait les temples ?"
                        self.puzzle_answers = ["1. Anubis", "2. Zeus", "3. Hadès"]
                        self.correct_answer = 1
                    elif self.current_room == 1:
                        self.puzzle_question = "A quoi servaient les pyramides ?"
                        self.puzzle_answers = ["1. Maisons", "2. Tombeaux", "3. Greniers"]
                        self.correct_answer = 2

            if self.state == "combat_boss" and not self.game_over:
                self.player.apply_gravity()
                for projectile in self.player.projectiles:
                    projectile.move()
                if self.boss:
                    self.boss.move()
                    projectile = self.boss.shoot(self.player.rect.center)
                    if projectile:
                        self.boss_projectiles.add(projectile)
                for proj in self.boss_projectiles:
                    proj.move()
                if pygame.sprite.spritecollide(self.player, self.boss_projectiles, True):
                    self.player.take_damage(20)
                if self.boss:
                    collisions = pygame.sprite.spritecollide(self.boss, self.player.projectiles, True)
                    for _ in collisions:
                        self.boss.take_damage(10)
                        if self.boss.health <= 0:
                            self.boss.kill()
                            self.boss = None
                            self.boss_defeated = True
                            self.state = "victory"

            if self.player.health <= 0:
                self.game_over = True

            # =====================
            # AFFICHAGE
            # =====================
            
            # --- MENU PRINCIPAL ---
            if self.state == "start_menu":
                self.screen.blit(self.menu_background, (0, 0))
                
                title_text = self.font_title.render("BIENVENUE DANS LES RUINES", True, (255, 215, 0))
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
                self.screen.blit(title_text, title_rect)

                desc_text = self.font_subtitle.render("Survivez aux ennemis et répondez aux énigmes des Dieux...", True, (255, 255, 255))
                desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
                self.screen.blit(desc_text, desc_rect)

                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    # --- CORRECTION ICI : ROUGE POUR LE MENU ---
                    start_text = self.font.render("Appuyez sur ENTREE pour commencer", True, (255, 0, 0))
                    self.screen.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140)))
            
            # --- JEU ---
            else:
                self.screen.blit(self.background_image, (0, 0))
                self.screen.blit(self.font.render(f"Score : {self.score}", True, (255, 0, 0)), (10, 10))

                if self.state == "intro" and not self.intro_displayed:
                    intro_text = self.font.render("Eliminez 30 ennemis pour ouvrir la salle !", True, (0, 0, 0))
                    self.screen.blit(intro_text, intro_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    self.state = "combat"
                    self.intro_displayed = True

                if self.state in ["combat", "combat_boss"] and not self.game_over:
                    color = (255, 255, 255) if self.current_room >= 1 else (0, 0, 0)
                    if self.state == "combat":
                        text_surface = self.font.render(
                            f"Ennemis : {self.enemies_killed} / {self.enemies_needed}", True, color
                        )
                        self.screen.blit(text_surface, (SCREEN_WIDTH // 2 - 50, 50))

                if self.state == "puzzle" and not self.game_over:
                    color = (255, 255, 255) if self.current_room >= 1 else (0, 0, 0)
                    question_surface = self.font.render(self.puzzle_question, True, color)
                    question_rect = question_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
                    self.screen.blit(question_surface, question_rect)
                    for i, ans in enumerate(self.puzzle_answers):
                        ans_surface = self.font.render(ans, True, color)
                        ans_rect = ans_surface.get_rect(center=(SCREEN_WIDTH // 2, 100 + i * 40))
                        self.screen.blit(ans_surface, ans_rect)
                    attempts_surface = self.font.render(f"Essais restants : {self.attempts_left}", True, (255, 0, 0))
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
                    victory_text = self.font.render("BRAVO ! BOSS VAINCU !", True, (255, 255, 255))
                    self.screen.blit(victory_text, victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

                if self.game_over:
                    self.screen.fill((0, 0, 0))
                    self.screen.blit(
                        self.game_over_font.render("GAME OVER", True, (255, 0, 0)),
                        (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 40)
                    )
                    
                    if self.current_room == 0:
                        msg_replay = "Appuyez sur ENTREE pour revenir au menu"
                    else:
                        msg_replay = "Appuyez sur ENTREE pour reprendre le niveau"
                    
                    # --- CORRECTION ICI : ROUGE POUR LE GAME OVER AUSSI ---
                    replay_text = self.font.render(msg_replay, True, (255, 0, 0))
                    self.screen.blit(replay_text, replay_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)))

            pygame.display.flip()

        pygame.quit()