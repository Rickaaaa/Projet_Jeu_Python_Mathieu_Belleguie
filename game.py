import pygame
import random
from constants import *
from player import Player
from enemy import Enemy


class Game:

    def __init__(self):
        # Initialisation de la fenêtre
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mon Premier Jeu")

        # Image d'arrière-plan
        self.backgroung_image = pygame.image.load('assets/images/background.jpg')
        self.backgroung_image = pygame.transform.scale(
            self.backgroung_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        # Joueur
        self.player = Player()

        # Groupe d'ennemis
        self.enemies = pygame.sprite.Group()

        # Créer un premier ennemi
        self.spawn_enemy()

        # Score
        self.score = 0
        self.font = pygame.font.Font(None, 30)

        # Boucle du jeu
        self.running = True

        # GAME OVER
        self.game_over = False
        self.game_over_font = pygame.font.Font(None, 80)

    # Apparition d'une vague d'ennemis
    def spawn_enemy(self):
        num_enemies = random.randint(1, 3)  # 1 à 3 ennemis par vague
        for _ in range(num_enemies):
            x = SCREEN_WIDTH + random.randint(0, 200)  # légèrement hors écran
            y = GAME_FLOOR - random.randint(0, 150)  # hauteur aléatoire
            enemy = Enemy(x, y)
            # Optionnel : vitesse proportionnelle à la hauteur
            enemy.speed += (GAME_FLOOR - y) // 50
            self.enemies.add(enemy)

    # Déplacement joueur
    def keyboard(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()
        elif keys[pygame.K_LEFT]:
            self.player.move_left()

    # Réinitialiser le jeu
    def reset_game(self):
        self.player = Player()
        self.enemies.empty()
        self.spawn_enemy()
        self.score = 0
        self.game_over = False

    def run(self):
        clock = pygame.time.Clock()

        # Timer pour faire apparaître des vagues d'ennemis
        SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWN_ENEMY_EVENT, 2000)  # toutes les 2 secondes

        while self.running:
            clock.tick(60)

            # Gestion clavier
            self.keyboard()

            # Gestion des événements
            for event in pygame.event.get():

                # Quitter le jeu
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()

                # Saut ou rejouer
                if event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_UP:
                            self.player.jump()
                    else:
                        if event.key == pygame.K_RETURN:
                            self.reset_game()

                # Tir avec clic gauche
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_over and event.button == 1:
                        self.player.shoot()

                # Spawn ennemis
                if event.type == SPAWN_ENEMY_EVENT and not self.game_over:
                    self.spawn_enemy()

            # Si GAME OVER, afficher écran noir + instructions
            if self.game_over:
                self.screen.fill((0, 0, 0))

                # Texte GAME OVER
                game_over_text = self.game_over_font.render(
                    "GAME OVER", True, (255, 0, 0)
                )
                game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
                self.screen.blit(game_over_text, game_over_rect)

                # Instruction pour rejouer
                replay_font = pygame.font.Font(None, 40)
                replay_text = replay_font.render(
                    "Appuyez sur ENTREE pour rejouer", True, (255, 255, 255)
                )
                replay_rect = replay_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
                self.screen.blit(replay_text, replay_rect)

                pygame.display.flip()
                continue  # passer au prochain frame

            # Physique joueur
            self.player.apply_gravity()

            # Déplacement ennemis
            for enemy in self.enemies:
                enemy.move()

            # Déplacement projectiles
            for projectile in self.player.projectiles:
                projectile.move()

            # Collisions projectiles / ennemis
            collisions = pygame.sprite.groupcollide(
                self.player.projectiles,
                self.enemies,
                True,
                True
            )
            if collisions:
                self.score += len(collisions)

            # Collision joueur / ennemis
            if pygame.sprite.spritecollide(
                self.player,
                self.enemies,
                True
            ):
                self.player.take_damage(10)

            # Vérifier si joueur est mort
            if self.player.health <= 0:
                self.game_over = True

            # Affichage
            self.screen.blit(self.backgroung_image, (0, 0))

            # Score
            score_text = self.font.render(
                f"Score : {self.score}", True, (255, 0, 0)
            )
            self.screen.blit(score_text, (10, 10))

            # Joueur et barre de vie
            self.screen.blit(self.player.image, self.player.rect)
            self.player.draw_health_bar(self.screen)

            # Ennemi et projectiles
            self.enemies.draw(self.screen)
            self.player.projectiles.draw(self.screen)

            pygame.display.flip()
