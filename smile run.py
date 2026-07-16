import pygame
import sys
import random
import math

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH = 800
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smile Run - Animado")
clock = pygame.time.Clock()

# Colores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN_SKY = (46, 204, 64)       
GREY_HELL = (85, 85, 85)        
RED_OBSTACLE = (255, 65, 54)     
YELLOW_OBSTACLE = (255, 220, 0)  

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
dimension = "cielo"  
game_over = False

# Sistema de partículas para el polvo al correr o chispas del infierno
particles = []

def create_dust_particles(x, y, color):
    for _ in range(2):
        particles.append({
            "x": x,
            "y": y,
            "vx": -random.uniform(2, 5),
            "vy": -random.uniform(0.5, 2),
            "radius": random.randint(3, 6),
            "alpha": 255,
            "color": color
        })

def update_and_draw_particles(surface):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["alpha"] -= 10  # Se desvanecen
        if p["alpha"] <= 0:
            particles.remove(p)
        else:
            # Dibujar con transparencia
            p_surface = pygame.Surface((p["radius"]*2, p["radius"]*2), pygame.SRCALPHA)
            color_with_alpha = (p["color"][0], p["color"][1], p["color"][2], int(p["alpha"]))
            pygame.draw.circle(p_surface, color_with_alpha, (p["radius"], p["radius"]), p["radius"])
            surface.blit(p_surface, (int(p["x"] - p["radius"]), int(p["y"] - p["radius"])))

# Elementos del fondo decorativos (Árboles / Llamas)
background_elements = []

def update_background_elements():
    # Generar decoración aleatoria de fondo
    if len(background_elements) < 10 and random.random() < 0.02:
        background_elements.append({
            "x": WIDTH,
            "y": 300 if dimension == "cielo" else 260,
            "speed": game_speed * 0.5, # Moverse más lento para efecto 3D paralaje
            "type": "tree" if dimension == "cielo" else "flame"
        })
    
    for elem in background_elements[:]:
        elem["x"] -= elem["speed"]
        if elem["x"] + 100 < 0:
            background_elements.remove(elem)

def draw_background_elements(surface):
    for elem in background_elements:
        if elem["type"] == "tree":
            # Dibujar árbol minimalista caricaturesco
            pygame.draw.rect(surface, (139, 69, 19), (elem["x"] + 15, elem["y"], 10, 60)) # Tronco
            pygame.draw.circle(surface, (34, 139, 34), (int(elem["x"] + 20), int(elem["y"] - 10)), 25) # Hojas
        else:
            # Dibujar llamas animadas en el infierno
            wave = math.sin(game_time * 0.2 + elem["x"]) * 10
            points = [
                (elem["x"], elem["y"] + 100),
                (elem["x"] + 15, elem["y"] + wave),
                (elem["x"] + 30, elem["y"] + 100)
            ]
            pygame.draw.polygon(surface, (255, 69, 0), points)

# Clase Jugador (Sombra sonriente animada)
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
        
        # Variables de animación
        self.animation_timer = 0

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
            
        # Actualizar temporizador para la animación de correr
        if self.is_grounded and not self.is_ducking:
            self.animation_timer += 0.25
            # Crear partículas en los pies al correr
            dust_color = (200, 200, 200) if dimension == "cielo" else (255, 100, 0)
            if random.random() < 0.4:
                create_dust_particles(self.x + 10, 360, dust_color)

    def draw(self, surface):
        # Calcular deformaciones físicas para simular dinamismo (Squash & Stretch)
        draw_width = self.width
        draw_height = self.height
        draw_x = self.x
        draw_y = self.y

        if not self.is_grounded:
            # Estirarse verticalmente al saltar o caer
            stretch = int(abs(self.vy) * 0.7)
            draw_height += stretch
            draw_width -= stretch // 2
            draw_y -= stretch
        elif self.is_grounded and not self.is_ducking:
            # Balanceo sutil arriba/abajo y de lado al correr (bobbing effect)
            bobbing = math.sin(self.animation_timer) * 4
            draw_y += bobbing
            draw_height -= bobbing
            
        # Dibujar Cuerpo Sombra
        pygame.draw.rect(surface, BLACK, (draw_x, draw_y, draw_width, draw_height), border_radius=5)
        
        # Ojos y sonrisa blanca que siguen la cabeza
        face_y = draw_y + (12 if self.is_ducking else 18)
        
        if not self.is_ducking:
            # Ojos grandes redondos animados (parpadeo sutil opcional)
            pygame.draw.circle(surface, WHITE, (int(draw_x + draw_width * 0.3), int(face_y)), 5)
            pygame.draw.circle(surface, WHITE, (int(draw_x + draw_width * 0.7), int(face_y)), 5)
            # Sonrisa curva alegre
            pygame.draw.arc(surface, WHITE, (draw_x + draw_width * 0.25, face_y + 2, draw_width * 0.5, 12), 3.14, 0, 2)
        else:
            # Ojos rasgados al agacharse
            pygame.draw.rect(surface, WHITE, (draw_x + 8, face_y, 6, 4))
            pygame.draw.rect(surface, WHITE, (draw_x + 24, face_y, 6, 4))

# Clase Obstáculo
class Obstacle:
    def __init__(self, type):
        self.type = type
        self.x = WIDTH
        if self.type == "bajo":  
            self.y = 320
            self.width = 30
            self.height = 40
            self.color = RED_OBSTACLE
        else:  
            self.y = 240
            self.width = 40
            self.height = 30
            self.color = YELLOW_OBSTACLE

    def update(self):
        self.x -= game_speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=3)

# Función para dibujar fondos en degradado
def draw_gradient_background(surface, top_color, bottom_color):
    for y in range(HEIGHT - 40):  
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
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_DOWN:
                    player.duck()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    player.stand_up()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                player = Player()
                obstacles = []
                background_elements = []
                particles = []
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
        update_background_elements()

        # Cambiar dimensiones cada 15 segundos
        if game_time % 900 == 0:
            dimension = "infierno" if dimension == "cielo" else "cielo"
            background_elements.clear()  # Limpiar decoraciones anteriores

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
            
            # Caja de colisión
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            obs_rect = pygame.Rect(obs.x, obs.y, obs.width, obs.height)
            if player_rect.colliderect(obs_rect):
                game_over = True

    # 3. Dibujar en Pantalla
    if dimension == "cielo":
        draw_gradient_background(screen, SKY_TOP, SKY_BOTTOM)
        ground_color = GREEN_SKY
    else:
        draw_gradient_background(screen, HELL_TOP, HELL_BOTTOM)
        ground_color = GREY_HELL

    # Dibujar decoración de fondo con paralaje
    draw_background_elements(screen)

    # Suelo
    pygame.draw.rect(screen, ground_color, (0, 360, WIDTH, 40))

    # Partículas
    update_and_draw_particles(screen)

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