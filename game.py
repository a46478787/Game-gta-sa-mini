import pygame
import math
import random
import sys

# Инициализация pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (101, 67, 33)

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.3
        self.deceleration = 0.2
        self.turn_speed = 0
        self.max_turn_speed = 5
        self.width = 30
        self.height = 15
        self.health = 100
        self.wanted_level = 0
        
    def update(self, keys):
        # Управление
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed/2)
        else:
            if self.speed > 0:
                self.speed = max(self.speed - self.deceleration, 0)
            else:
                self.speed = min(self.speed + self.deceleration, 0)
        
        # Поворот только при движении
        if abs(self.speed) > 0.1:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle -= self.max_turn_speed * (abs(self.speed) / self.max_speed)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle += self.max_turn_speed * (abs(self.speed) / self.max_speed)
        
        # Движение
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        
        # Границы экрана
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
    
    def draw(self, screen):
        # Создаем точки для машины
        points = []
        cos_angle = math.cos(math.radians(self.angle))
        sin_angle = math.sin(math.radians(self.angle))
        
        # Углы машины
        corners = [
            (-self.width/2, -self.height/2),
            (self.width/2, -self.height/2),
            (self.width/2, self.height/2),
            (-self.width/2, self.height/2)
        ]
        
        for corner in corners:
            x = corner[0] * cos_angle - corner[1] * sin_angle + self.x
            y = corner[0] * sin_angle + corner[1] * cos_angle + self.y
            points.append((x, y))
        
        pygame.draw.polygon(screen, RED, points)
        
        # Индикатор направления
        front_x = self.x + cos_angle * self.width/2
        front_y = self.y + sin_angle * self.width/2
        pygame.draw.circle(screen, YELLOW, (int(front_x), int(front_y)), 3)

class Building:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = random.choice([GRAY, DARK_GRAY, BROWN])
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

class Mission:
    def __init__(self, target_x, target_y, description):
        self.target_x = target_x
        self.target_y = target_y
        self.description = description
        self.completed = False
        self.active = True
    
    def check_completion(self, player):
        distance = math.sqrt((player.x - self.target_x)**2 + (player.y - self.target_y)**2)
        if distance < 50:
            self.completed = True
            return True
        return False
    
    def draw(self, screen):
        if self.active and not self.completed:
            pygame.draw.circle(screen, GREEN, (int(self.target_x), int(self.target_y)), 30, 3)
            pygame.draw.circle(screen, YELLOW, (int(self.target_x), int(self.target_y)), 5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GTA San Andreas Mini - Русская версия")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Игрок
        self.player = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Здания
        self.buildings = []
        self.generate_city()
        
        # Миссии
        self.missions = [
            Mission(100, 100, "Доберись до точки A"),
            Mission(900, 100, "Доберись до точки B"),
            Mission(900, 600, "Доберись до точки C"),
            Mission(100, 600, "Доберись до точки D")
        ]
        self.current_mission = 0
        self.score = 0
        
        # Шрифт
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def generate_city(self):
        # Генерируем простую сетку зданий
        for x in range(0, SCREEN_WIDTH, 150):
            for y in range(0, SCREEN_HEIGHT, 150):
                if random.random() > 0.3:  # 70% шанс здания
                    width = random.randint(60, 120)
                    height = random.randint(60, 120)
                    # Оставляем место для дорог
                    building_x = x + random.randint(10, 30)
                    building_y = y + random.randint(10, 30)
                    self.buildings.append(Building(building_x, building_y, width, height))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.restart_game()
    
    def restart_game(self):
        self.player = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.current_mission = 0
        self.score = 0
        for mission in self.missions:
            mission.completed = False
            mission.active = True
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Проверка выполнения миссий
        if self.current_mission < len(self.missions):
            mission = self.missions[self.current_mission]
            if mission.check_completion(self.player):
                self.score += 100
                self.current_mission += 1
                if self.current_mission >= len(self.missions):
                    print("Все миссии выполнены!")
    
    def draw(self):
        self.screen.fill(GREEN)  # Трава
        
        # Дороги
        for x in range(0, SCREEN_WIDTH, 150):
            pygame.draw.rect(self.screen, DARK_GRAY, (x, 0, 40, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 150):
            pygame.draw.rect(self.screen, DARK_GRAY, (0, y, SCREEN_WIDTH, 40))
        
        # Здания
        for building in self.buildings:
            building.draw(self.screen)
        
        # Миссии
        if self.current_mission < len(self.missions):
            self.missions[self.current_mission].draw(self.screen)
        
        # Игрок
        self.player.draw(self.screen)
        
        # UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Счет
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Текущая миссия
        if self.current_mission < len(self.missions):
            mission_text = self.small_font.render(f"Миссия: {self.missions[self.current_mission].description}", True, WHITE)
            self.screen.blit(mission_text, (10, 50))
        else:
            complete_text = self.font.render("ВСЕ МИССИИ ВЫПОЛНЕНЫ!", True, YELLOW)
            self.screen.blit(complete_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))
        
        # Здоровье
        health_text = self.small_font.render(f"Здоровье: {self.player.health}%", True, WHITE)
        self.screen.blit(health_text, (10, 80))
        
        # Скорость
        speed_text = self.small_font.render(f"Скорость: {abs(self.player.speed):.1f}", True, WHITE)
        self.screen.blit(speed_text, (10, 110))
        
        # Управление
        controls = [
            "Управление: WASD или стрелки",
            "R - рестарт",
            "ESC - выход"
        ]
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 250, 10 + i * 25))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()