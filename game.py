import pygame
from constants import *
from player import Player
from projectile import Projectile
# On importe nos nouvelles salles
from levels import Room1, Room2, RoomBoss

class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ruines Mythologiques")

        # Chargement écran titre
        try:
            self.menu_background = pygame.image.load("assets/images/loading_background.jpg")
            self.menu_background = pygame.transform.scale(self.menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            self.menu_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.menu_background.fill((0, 0, 0))

        # --- SYSTÈME DE SALLES ---
        # On stocke les 3 objets salles dans une liste
        self.rooms_list = [Room1(), Room2(), RoomBoss()]
        self.current_room_index = 0
        self.current_level = self.rooms_list[self.current_room_index]

        # Joueur & Groupes
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.boss_projectiles = pygame.sprite.Group()
        self.boss = None

        # Configuration Initiale
        self.apply_room_settings()

        # États et Polices
        self.state = "start_menu"
        self.game_over = False
        self.score = 0
        
        self.font = pygame.font.Font(None, 32)
        self.font_title = pygame.font.Font(None, 90)
        self.font_subtitle = pygame.font.Font(None, 40)
        self.game_over_font = pygame.font.Font(None, 80)

        # Logique de jeu
        self.attempts_left = 2
        self.enemies_killed = 0
        self.wave_active = True
        self.intro_displayed = False
        self.running = True

    # =====================
    # CONFIGURATION SALLE
    # =====================
    def apply_room_settings(self):
        """Applique les paramètres de la salle actuelle (Sol, Fond, Ennemis...)"""
        level = self.current_level
        
        # Sol et Fond
        self.level_floor = level.floor_y
        self.background_image = level.bg_image
        
        # Placement Joueur
        self.player.floor_y = self.level_floor
        self.player.rect.y = self.player.floor_y - self.player.rect.height
        
        # Reset Ennemis
        self.enemies.empty()
        self.boss_projectiles.empty()
        self.boss = None
        
        # Si c'est la salle 3, on crée le boss
        if self.current_room_index == 2:
            self.boss = level.spawn_boss(self.level_floor)
        else:
            # Sinon on lance le spawn classique
            level.spawn_enemies(self.enemies, self.level_floor)
            
        self.enemies_killed = 0
        self.wave_active = True
        self.intro_displayed = False

    # =====================
    # GESTION INPUTS
    # =====================
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: self.player.move_right()
        elif keys[pygame.K_LEFT]: self.player.move_left()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # -- MENU --
                if self.state == "start_menu" and event.key == pygame.K_RETURN:
                    self.state = "intro"
                
                # -- JEU --
                if self.state in ["combat", "combat_boss"] and not self.game_over and event.key == pygame.K_UP:
                    self.player.jump()

                # -- ÉNIGMES (Classique ou Boss) --
                if self.state in ["puzzle", "puzzle_boss"] and not self.game_over:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        answer = event.key - pygame.K_0
                        if answer == self.current_level.correct_answer:
                            # Bonne réponse
                            if self.state == "puzzle_boss":
                                self.state = "victory"
                            else:
                                if self.current_room_index == 0: self.state = "transition_salle2"
                                elif self.current_room_index == 1: self.state = "transition_salle3"
                        else:
                            # Mauvaise réponse
                            self.attempts_left -= 1
                            if self.attempts_left <= 0:
                                if self.state == "puzzle_boss": self.reset_game() # Boss : Reset direct
                                else:
                                    # Salles normales : on recommence le combat
                                    self.attempts_left = 2
                                    self.state = "combat"
                                    self.enemies_killed = 0
                                    self.current_level.spawn_enemies(self.enemies, self.level_floor)

                # -- GAME OVER --
                if self.game_over and event.key == pygame.K_RETURN:
                    self.reset_game()

            # -- TIR --
            if event.type == pygame.MOUSEBUTTONDOWN and self.state in ["combat", "combat_boss"] and not self.game_over:
                if event.button == 1:
                    # Tir vertical si salle 3 (index 2), sinon normal
                    if self.current_room_index == 2: self.player.shoot(target_y=0)
                    else: self.player.shoot()

            # -- SPAWN ENNEMIS (Salles 1 et 2) --
            SPAWN_EVENT = pygame.USEREVENT + 1
            if event.type == SPAWN_EVENT and self.state == "combat" and not self.game_over and self.wave_active:
                if len(self.enemies) < 4:
                    self.current_level.spawn_enemies(self.enemies, self.level_floor)

    # =====================
    # RESET / CHECKPOINT
    # =====================
    def reset_game(self):
        self.player.health = self.player.max_health
        self.game_over = False
        self.attempts_left = 2
        
        # Logique de Checkpoint
        if self.current_room_index == 0:
            self.state = "start_menu"
            self.score = 0
        elif self.current_room_index == 1:
            self.state = "combat"
        elif self.current_room_index == 2:
            self.state = "combat_boss"
            
        self.apply_room_settings()

    # =====================
    # FONCTIONS D'AFFICHAGE
    # =====================
    def draw_intro_text(self):
        """Affiche le bandeau noir et le texte spécifique à la salle"""
        lines = self.current_level.intro_lines
        
        # Configuration
        text_color = (255, 215, 0)
        bg_color = (0, 0, 0, 180)
        start_y = 120
        line_spacing = 50
        
        # Fond
        total_height = len(lines) * line_spacing + 40
        bg_surface = pygame.Surface((SCREEN_WIDTH, total_height), pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        self.screen.blit(bg_surface, (0, start_y - 20))

        # Texte
        for i, line in enumerate(lines):
            text_surf = self.font_subtitle.render(line, True, text_color)
            rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * line_spacing))
            self.screen.blit(text_surf, rect)

    def transition_sequence(self, next_room_idx, msg_bravo):
        """Gère l'écran noir de chargement"""
        for i in range(3, 0, -1):
            self.screen.fill((0, 0, 0))
            t1 = pygame.font.Font(None, 60).render(msg_bravo, True, (255, 255, 255))
            t2 = pygame.font.Font(None, 40).render(f"Chargement dans {i}...", True, (255, 255, 255))
            self.screen.blit(t1, t1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
            self.screen.blit(t2, t2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
            pygame.display.flip()
            pygame.time.delay(1000)
        
        # Changement de salle effectif
        self.current_room_index = next_room_idx
        self.current_level = self.rooms_list[self.current_room_index]
        self.apply_room_settings()

    # =====================
    # BOUCLE PRINCIPALE
    # =====================
    def run(self):
        clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT + 1, 2000)

        while self.running:
            clock.tick(60)
            if self.state not in ["start_menu", "victory", "game_over"]:
                self.player.apply_gravity()
            
            self.handle_input()
            if not self.running: break

            # --- LOGIQUE TRANSITIONS ---
            if self.state == "transition_salle2":
                self.transition_sequence(1, "Bravo, salle 1 terminée !")
                # On affiche l'intro de la salle 2
                self.screen.blit(self.background_image, (0, 0))
                self.screen.blit(self.player.image, self.player.rect)
                for e in self.enemies: self.screen.blit(e.image, e.rect)
                self.draw_intro_text()
                pygame.display.flip()
                pygame.time.delay(4000)
                self.state = "combat"

            if self.state == "transition_salle3":
                self.transition_sequence(2, "Bravo, salle 2 terminée !")
                # On affiche l'intro du boss
                self.screen.blit(self.background_image, (0, 0))
                self.screen.blit(self.player.image, self.player.rect)
                if self.boss: self.screen.blit(self.boss.image, self.boss.rect)
                self.draw_intro_text()
                pygame.display.flip()
                pygame.time.delay(4000)
                self.state = "combat_boss"


            # --- LOGIQUE COMBAT ---
            if self.state == "combat" and not self.game_over:
                for enemy in self.enemies: enemy.move()
                for proj in self.player.projectiles: proj.move()
                
                # Collisions Tirs -> Ennemis
                hits = pygame.sprite.groupcollide(self.player.projectiles, self.enemies, True, False)
                for proj, enemy_list in hits.items():
                    for e in enemy_list:
                        if hasattr(e, 'take_damage'): e.take_damage() # Salle 2
                        else: e.kill() # Salle 1
                        if e.health <= 0 or not hasattr(e, 'health'):
                            e.kill()
                            self.score += 1
                            self.enemies_killed += 1

                # Collisions Ennemis -> Joueur
                if pygame.sprite.spritecollide(self.player, self.enemies, True):
                    self.player.take_damage(20)

                if self.enemies_killed >= self.current_level.enemies_needed:
                    self.state = "puzzle"

            # --- LOGIQUE BOSS ---
            if self.state == "combat_boss" and not self.game_over:
                for proj in self.player.projectiles: proj.move()
                if self.boss:
                    self.boss.move()
                    p = self.boss.shoot(self.player.rect.center)
                    if p: self.boss_projectiles.add(p)
                    
                    # Collisions Tirs -> Boss
                    if pygame.sprite.spritecollide(self.boss, self.player.projectiles, True):
                        self.boss.take_damage(10)
                        if self.boss.health <= 0:
                            self.boss.kill()
                            self.boss = None
                            self.state = "puzzle_boss" # Enigme finale

                for p in self.boss_projectiles: p.move()
                if pygame.sprite.spritecollide(self.player, self.boss_projectiles, True):
                    self.player.take_damage(20)

            if self.player.health <= 0: self.game_over = True

            # --- DESSIN (DRAW) ---
            if self.state == "start_menu":
                self.screen.blit(self.menu_background, (0, 0))
                t = self.font_title.render("BIENVENUE DANS LES RUINES", True, (255, 215, 0))
                self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, 100)))
                d = self.font_subtitle.render("Survivez aux ennemis et répondez aux énigmes...", True, (255, 255, 255))
                self.screen.blit(d, d.get_rect(center=(SCREEN_WIDTH//2, 180)))
                
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    s = self.font.render("Appuyez sur ENTREE pour commencer", True, (255, 0, 0))
                    self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 180)))

            else:
                self.screen.blit(self.background_image, (0, 0))
                self.screen.blit(self.font.render(f"Score : {self.score}", True, (255, 0, 0)), (10, 10))

                # Intro Salle 1
                if self.state == "intro" and not self.intro_displayed:
                    self.draw_intro_text()
                    pygame.display.flip()
                    pygame.time.delay(4000)
                    self.state = "combat"
                    self.intro_displayed = True

                # UI Combat
                if self.state == "combat":
                    t = self.font.render(f"Ennemis : {self.enemies_killed} / {self.current_level.enemies_needed}", True, (255, 255, 255))
                    self.screen.blit(t, (SCREEN_WIDTH//2 - 50, 50))

                # UI Puzzle
                if self.state in ["puzzle", "puzzle_boss"] and not self.game_over:
                    if self.state == "puzzle_boss":
                        t = self.font_subtitle.render("ULTIME ÉPREUVE :", True, (255, 215, 0))
                        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, 30)))
                    
                    q = self.font.render(self.current_level.puzzle_question, True, (255, 255, 255))
                    self.screen.blit(q, q.get_rect(center=(SCREEN_WIDTH//2, 70)))
                    
                    for i, ans in enumerate(self.current_level.puzzle_answers):
                        a = self.font.render(ans, True, (255, 255, 255))
                        self.screen.blit(a, a.get_rect(center=(SCREEN_WIDTH//2, 120 + i * 40)))
                    
                    att = self.font.render(f"Essais restants : {self.attempts_left}", True, (255, 0, 0))
                    self.screen.blit(att, att.get_rect(center=(SCREEN_WIDTH//2, 250)))

                # Sprites
                self.screen.blit(self.player.image, self.player.rect)
                self.player.draw_health_bar(self.screen)
                for e in self.enemies: 
                    self.screen.blit(e.image, e.rect)
                    if hasattr(e, 'draw_health_bar'): e.draw_health_bar(self.screen)
                
                self.player.projectiles.draw(self.screen)
                self.boss_projectiles.draw(self.screen)
                if self.boss: 
                    self.screen.blit(self.boss.image, self.boss.rect)
                    self.boss.draw_health_bar(self.screen)

                # Victoire
                if self.state == "victory":
                    self.screen.fill((0, 0, 0))
                    v = self.font.render("BRAVO ! VICTOIRE TOTALE !", True, (255, 215, 0))
                    self.screen.blit(v, v.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
                    q = self.font.render("Appuyez sur la croix pour quitter", True, (255, 255, 255))
                    self.screen.blit(q, q.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))

                # Game Over
                if self.game_over:
                    self.screen.fill((0, 0, 0))
                    g = self.game_over_font.render("GAME OVER", True, (255, 0, 0))
                    self.screen.blit(g, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 40))
                    
                    msg = "Appuyez sur ENTREE pour revenir au menu" if self.current_room_index == 0 else "Appuyez sur ENTREE pour reprendre le niveau"
                    r = self.font.render(msg, True, (255, 0, 0))
                    self.screen.blit(r, r.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))

            pygame.display.flip()
        
        pygame.quit()