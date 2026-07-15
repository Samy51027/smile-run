import pygame
import sys
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH = 800
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smile Run - Prototipo")
clock = pygame.time.Clock()

# Colores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN_SKY = (46, 204, 64)       # Pasto del cielo
GREY_HELL = (85, 85, 85)        # Suelo del infierno
RED_OBSTACLE = (255, 65, 54)     # Pinchos
YELLOW_OBSTACLE = (255, 220, 0)  # Nube eléctrica

# Fondos (Cielo e Infierno)
SKY_TOP = (135, 206, 235)
SKY_BOTTOM = (224, 246, 255)
HELL_TOP = (253, 94, 83)
HELL_BOTTOM = (139, 0, 0)

# Variables del juego
score = 0
game_speed = 6
spawn_timer = 0
game_time = 0
dimension = "cielo"  # "cielo" o "infierno"
game_over = False

# Clase Jugador (Sombra sonriente)
class Player:
    def __init__(self):
        self.x = 100
        self.original_height = 60
        self.duck_height = 30
        self.width = 40
        self.height = self.original_height
        self.y = 360 - self.height
        
        self.vy = 0
        self.gravity = 1.0
        self.jump_force = -16
        self.is_grounded = True
        self.is_ducking = False

    def jump(self):
        if self.is_grounded and not self.is_ducking:
            self.vy = self.jump_force
            self.is_grounded = False

    def duck(self):
        if self.is_grounded:
            self.is_ducking = True
            self.height = self.duck_height
            self.y = 360 - self.duck_height

    def stand_up(self):
        self.is_ducking = False
        self.height = self.original_height
        self.y = 360 - self.original_height

    def update(self):
        # Aplicar gravedad
        self.vy += self.gravity
        self.y += self.vy

        # Límite del suelo
        ground_y = 360 - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.vy = 0
            self.is_grounded = True

    def draw(self, surface):
        # Cuerpo negro del personaje
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height))
        
        # Ojos y sonrisa blanca
        if not self.is_ducking:
            # Ojos grandes redondos
            pygame.draw.circle(surface, WHITE, (self.x + 12, int(self.y + 18)), 5)
            pygame.draw.circle(surface, WHITE, (self.x + 28, int(self.y + 18)), 5)
            # Sonrisa (arco simple)
            pygame.draw.arc(surface, WHITE, (self.x + 10, self.y + 20, 20, 12), 3.14, 0, 2)
        else:
            # Ojos achicados al agacharse
            pygame.draw.rect(surface, WHITE, (self.x + 10, self.y + 12, 6, 4))
            pygame.draw.rect(surface, WHITE, (self.x + 24, self.y + 12, 6, 4))

# Clase Obstáculo
class Obstacle:
    def __init__(self, type):
        self.type = type
        self.x = WIDTH
        if self.type == "bajo":  # Pincho (se salta)
            self.y = 320
            self.width = 30
            self.height = 40
            self.color = RED_OBSTACLE
        else:  # Nube eléctrica (se pasa agachado)
            self.y = 240
            self.width = 40
            self.height = 30
            self.color = YELLOW_OBSTACLE

    def update(self):
        self.x -= game_speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

# Función para dibujar fondos en degradado
def draw_gradient_background(surface, top_color, bottom_color):
    for y in range(HEIGHT - 40):  # Dejar espacio para el suelo
        color = [
            top_color[i] + (bottom_color[i] - top_color[i]) * y // (HEIGHT - 40)
            for i in range(3)
        ]
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

# Inicialización de objetos
player = Player()
obstacles = []

# Fuentes de texto
font = pygame.font.SysFont("Arial", 24)
font_large = pygame.font.SysFont("Arial", 40)

# Bucle principal del juego
running = True
while running:
    # 1. Eventos y Controles
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_DOWN:
                    player.duck()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    player.stand_up()
        else:
            # Reiniciar si presionas ENTER tras el Game Over
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                player = Player()
                obstacles = []
                score = 0
                game_speed = 6
                spawn_timer = 0
                game_time = 0
                dimension = "cielo"
                game_over = False

    if not game_over:
        # 2. Actualizar Lógica
        game_time += 1
        score += 1
        player.update()

        # Cambiar dimensiones cada 15 segundos (900 fotogramas a 60fps)
        if game_time % 900 == 0:
            dimension = "infierno" if dimension == "cielo" else "cielo"

        # Aumentar dificultad
        if game_time % 600 == 0:
            game_speed += 1

        # Generar obstáculos aleatorios
        spawn_timer += 1
        max_spawn_time = max(40, 120 - game_speed * 5)
        if spawn_timer > max_spawn_time:
            obs_type = "bajo" if random.random() > 0.5 else "alto"
            obstacles.append(Obstacle(obs_type))
            spawn_timer = 0

        # Mover y comprobar colisiones de obstáculos
        for obs in obstacles[:]:
            obs.update()
            if obs.x + obs.width < 0:
                obstacles.remove(obs)
            
            # Caja de colisión (AABB)
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            obs_rect = pygame.Rect(obs.x, obs.y, obs.width, obs.height)
            if player_rect.colliderect(obs_rect):
                game_over = True

    # 3. Dibujar en Pantalla
    # Fondo según la dimensión
    if dimension == "cielo":
        draw_gradient_background(screen, SKY_TOP, SKY_BOTTOM)
        ground_color = GREEN_SKY
    else:
        draw_gradient_background(screen, HELL_TOP, HELL_BOTTOM)
        ground_color = GREY_HELL

    # Suelo
    pygame.draw.rect(screen, ground_color, (0, 360, WIDTH, 40))

    # Jugador y Obstáculos
    player.draw(screen)
    for obs in obstacles:
        obs.draw(screen)

    # Textos de Interfaz
    score_text = font.render(f"Puntos: {score}", True, BLACK)
    dimension_text = font.render(f"Mundo: {dimension.upper()}", True, BLACK)
    screen.blit(score_text, (20, 20))
    screen.blit(dimension_text, (20, 50))

    # Pantalla de Game Over
    if game_over:
        # Capa traslúcida oscura
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        go_text = font_large.render("¡JUEGO TERMINADO!", True, RED_OBSTACLE)
        restart_text = font.render("Presiona [ENTER] para volver a jugar", True, WHITE)
        final_score = font.render(f"Puntuación final: {score}", True, WHITE)

        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 + 10))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()