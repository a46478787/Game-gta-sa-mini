import pygame
import math
import random
import sys
import time

# Инициализация pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
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
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)

class Car:
    def __init__(self, x, y, color=RED, is_player=False):
        self.x = x
        self.y = y
        self.angle = random.randint(0, 360) if not is_player else 0
        self.speed = 0
        self.max_speed = 8 if is_player else 3
        self.acceleration = 0.3 if is_player else 0.1
        self.deceleration = 0.2
        self.turn_speed = 0
        self.max_turn_speed = 5 if is_player else 2
        self.width = 30
        self.height = 15
        self.health = 100
        self.wanted_level = 0
        self.color = color
        self.is_player = is_player
        self.is_police = False
        self.target_x = None
        self.target_y = None
        self.ai_timer = 0
        
    def update(self, keys=None):
        if self.is_player and keys:
            self.update_player(keys)
        else:
            self.update_ai()
        
        # Движение
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        
        # Границы экрана - с телепортацией на противоположную сторону
        if self.x < -self.width:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = -self.width
        if self.y < -self.height:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = -self.height
    
    def update_player(self, keys):
        # Управление игрока
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
    
    def update_ai(self):
        self.ai_timer += 1
        
        # Простая AI логика
        if self.ai_timer > 60:  # Каждую секунду
            self.ai_timer = 0
            
            # Случайное изменение направления
            if random.random() < 0.3:
                self.angle += random.randint(-45, 45)
            
            # Случайное изменение скорости
            if random.random() < 0.5:
                self.speed = random.uniform(0.5, self.max_speed)
            else:
                self.speed = max(self.speed - 0.1, 0)
        
        # Избегание границ
        if self.x < 100:
            self.angle = random.randint(-45, 45)
        elif self.x > SCREEN_WIDTH - 100:
            self.angle = random.randint(135, 225)
        
        if self.y < 100:
            self.angle = random.randint(45, 135)
        elif self.y > SCREEN_HEIGHT - 100:
            self.angle = random.randint(225, 315)
    
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
        
        pygame.draw.polygon(screen, self.color, points)
        
        # Индикатор направления
        front_x = self.x + cos_angle * self.width/2
        front_y = self.y + sin_angle * self.width/2
        indicator_color = YELLOW if self.is_player else WHITE
        pygame.draw.circle(screen, indicator_color, (int(front_x), int(front_y)), 3)
        
        # Индикатор полиции
        if self.is_police:
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y - 20)), 8)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y - 20)), 4)

class Building:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = random.choice([GRAY, DARK_GRAY, BROWN])
        self.building_type = random.choice(['office', 'house', 'shop'])
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Окна
        if self.building_type == 'office':
            for i in range(0, self.width, 15):
                for j in range(0, self.height, 15):
                    if i + 8 < self.width and j + 8 < self.height:
                        window_color = YELLOW if random.random() > 0.7 else DARK_GRAY
                        pygame.draw.rect(screen, window_color, (self.x + i + 2, self.y + j + 2, 8, 8))

class Mission:
    def __init__(self, target_x, target_y, description, mission_type='go_to', reward=100):
        self.target_x = target_x
        self.target_y = target_y
        self.description = description
        self.mission_type = mission_type
        self.reward = reward
        self.completed = False
        self.active = True
        self.timer = 0
    
    def check_completion(self, player):
        distance = math.sqrt((player.x - self.target_x)**2 + (player.y - self.target_y)**2)
        if distance < 50:
            self.completed = True
            return True
        return False
    
    def draw(self, screen):
        if self.active and not self.completed:
            # Мигающий целевой маркер
            self.timer += 1
            if self.timer % 20 < 10:
                pygame.draw.circle(screen, GREEN, (int(self.target_x), int(self.target_y)), 40, 4)
            pygame.draw.circle(screen, YELLOW, (int(self.target_x), int(self.target_y)), 8)
            
            # Стрелка направления
            if hasattr(self, 'player_ref'):
                dx = self.target_x - self.player_ref.x
                dy = self.target_y - self.player_ref.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 100:
                    arrow_length = 30
                    arrow_x = self.player_ref.x + (dx / distance) * arrow_length
                    arrow_y = self.player_ref.y + (dy / distance) * arrow_length
                    pygame.draw.circle(screen, ORANGE, (int(arrow_x), int(arrow_y)), 5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GTA San Andreas Mini - Расширенная версия")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Игрок
        self.player = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, RED, True)
        
        # NPC машины
        self.npcs = []
        self.generate_npcs()
        
        # Полиция
        self.police_cars = []
        
        # Здания
        self.buildings = []
        self.generate_city()
        
        # Миссии
        self.missions = [
            Mission(150, 150, "Доберись до банка", 'go_to', 200),
            Mission(SCREEN_WIDTH - 150, 150, "Найди магазин", 'go_to', 150),
            Mission(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150, "Посети больницу", 'go_to', 300),
            Mission(150, SCREEN_HEIGHT - 150, "Вернись домой", 'go_to', 250),
            Mission(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "Встреча в центре", 'go_to', 500)
        ]
        
        for mission in self.missions:
            mission.player_ref = self.player
            
        self.current_mission = 0
        self.score = 0
        self.money = 1000
        self.wanted_level = 0
        self.time_of_day = 0  # 0-100, где 0 - ночь, 50 - день
        
        # Шрифты
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Эффекты
        self.explosions = []
        self.messages = []
        
        # Звуки (заглушки)
        self.sounds_enabled = False
    
    def generate_npcs(self):
        colors = [BLUE, GREEN, YELLOW, ORANGE, PURPLE, PINK, WHITE]
        for _ in range(15):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            color = random.choice(colors)
            npc = Car(x, y, color, False)
            self.npcs.append(npc)
    
    def generate_city(self):
        # Генерируем более сложный город
        for x in range(0, SCREEN_WIDTH, 180):
            for y in range(0, SCREEN_HEIGHT, 180):
                if random.random() > 0.2:  # 80% шанс здания
                    width = random.randint(80, 150)
                    height = random.randint(80, 150)
                    building_x = x + random.randint(20, 40)
                    building_y = y + random.randint(20, 40)
                    
                    # Проверяем, что здание не пересекается с начальной позицией игрока
                    if not (building_x < SCREEN_WIDTH//2 + 50 and building_x + width > SCREEN_WIDTH//2 - 50 and
                            building_y < SCREEN_HEIGHT//2 + 50 and building_y + height > SCREEN_HEIGHT//2 - 50):
                        self.buildings.append(Building(building_x, building_y, width, height))
    
    def spawn_police(self):
        if self.wanted_level > 0 and len(self.police_cars) < self.wanted_level:
            # Спавним полицию подальше от игрока
            spawn_x = random.choice([0, SCREEN_WIDTH])
            spawn_y = random.randint(0, SCREEN_HEIGHT)
            
            police_car = Car(spawn_x, spawn_y, BLUE, False)
            police_car.is_police = True
            police_car.max_speed = 6
            self.police_cars.append(police_car)
    
    def update_wanted_level(self):
        # Система розыска
        if self.wanted_level > 0:
            self.wanted_level -= 0.001  # Медленно уменьшается
            if self.wanted_level < 0:
                self.wanted_level = 0
        
        # Увеличиваем розыск при высокой скорости
        if abs(self.player.speed) > 6:
            self.wanted_level += 0.002
        
        self.wanted_level = min(self.wanted_level, 5)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_SPACE:
                    self.wanted_level += 1  # Для тестирования
                elif event.key == pygame.K_m:
                    self.money += 500  # Читы
    
    def restart_game(self):
        self.player = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, RED, True)
        self.current_mission = 0
        self.score = 0
        self.money = 1000
        self.wanted_level = 0
        self.police_cars = []
        self.explosions = []
        self.messages = []
        
        for mission in self.missions:
            mission.completed = False
            mission.active = True
            mission.player_ref = self.player
        
        self.npcs = []
        self.generate_npcs()
    
    def add_message(self, text, color=WHITE, duration=180):
        self.messages.append({
            'text': text,
            'color': color,
            'timer': duration,
            'y_offset': len(self.messages) * 25
        })
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Обновляем игрока
        self.player.update(keys)
        
        # Обновляем NPC
        for npc in self.npcs:
            npc.update()
        
        # Обновляем полицию
        for police in self.police_cars:
            police.update()
            # Простое преследование игрока
            dx = self.player.x - police.x
            dy = self.player.y - police.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                police.angle = math.degrees(math.atan2(dy, dx))
                police.speed = police.max_speed
        
        # Проверка выполнения миссий
        if self.current_mission < len(self.missions):
            mission = self.missions[self.current_mission]
            if mission.check_completion(self.player):
                self.score += mission.reward
                self.money += mission.reward
                self.add_message(f"Миссия выполнена! +{mission.reward}$", GREEN)
                self.current_mission += 1
                if self.current_mission >= len(self.missions):
                    self.add_message("ВСЕ МИССИИ ВЫПОЛНЕНЫ!", YELLOW)
        
        # Обновляем систему розыска
        self.update_wanted_level()
        self.spawn_police()
        
        # Обновляем время суток
        self.time_of_day += 0.1
        if self.time_of_day > 100:
            self.time_of_day = 0
        
        # Обновляем сообщения
        for message in self.messages[:]:
            message['timer'] -= 1
            if message['timer'] <= 0:
                self.messages.remove(message)
    
    def get_sky_color(self):
        # Меняем цвет неба в зависимости от времени суток
        if self.time_of_day < 25:  # Ночь
            return (20, 20, 40)
        elif self.time_of_day < 50:  # Рассвет
            return (100, 50, 100)
        elif self.time_of_day < 75:  # День
            return (135, 206, 235)
        else:  # Закат
            return (255, 140, 0)
    
    def draw(self):
        # Небо
        sky_color = self.get_sky_color()
        self.screen.fill(sky_color)
        
        # Трава
        grass_color = (34, 139, 34) if self.time_of_day > 25 else (20, 80, 20)
        pygame.draw.rect(self.screen, grass_color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Дороги
        road_color = DARK_GRAY if self.time_of_day > 25 else BLACK
        for x in range(0, SCREEN_WIDTH, 180):
            pygame.draw.rect(self.screen, road_color, (x, 0, 50, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 180):
            pygame.draw.rect(self.screen, road_color, (0, y, SCREEN_WIDTH, 50))
        
        # Разметка дорог
        line_color = YELLOW if self.time_of_day > 25 else GRAY
        for x in range(0, SCREEN_WIDTH, 180):
            for y in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.rect(self.screen, line_color, (x + 22, y, 6, 20))
        for y in range(0, SCREEN_HEIGHT, 180):
            for x in range(0, SCREEN_WIDTH, 40):
                pygame.draw.rect(self.screen, line_color, (x, y + 22, 20, 6))
        
        # Здания
        for building in self.buildings:
            building.draw(self.screen)
        
        # Миссии
        if self.current_mission < len(self.missions):
            self.missions[self.current_mission].draw(self.screen)
        
        # NPC машины
        for npc in self.npcs:
            npc.draw(self.screen)
        
        # Полиция
        for police in self.police_cars:
            police.draw(self.screen)
        
        # Игрок
        self.player.draw(self.screen)
        
        # UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Полупрозрачная панель для UI
        ui_surface = pygame.Surface((SCREEN_WIDTH, 150))
        ui_surface.set_alpha(128)
        ui_surface.fill(BLACK)
        self.screen.blit(ui_surface, (0, 0))
        
        # Основная информация
        info_texts = [
            f"Деньги: ${self.money}",
            f"Счет: {self.score}",
            f"Здоровье: {self.player.health}%",
            f"Скорость: {abs(self.player.speed):.1f} км/ч"
        ]
        
        for i, text in enumerate(info_texts):
            color = WHITE
            if i == 2 and self.player.health < 30:
                color = RED
            elif i == 3 and abs(self.player.speed) > 6:
                color = YELLOW
            
            rendered_text = self.small_font.render(text, True, color)
            self.screen.blit(rendered_text, (10, 10 + i * 25))
        
        # Уровень розыска
        if self.wanted_level > 0:
            wanted_text = f"Розыск: {'★' * int(self.wanted_level)}"
            wanted_surface = self.small_font.render(wanted_text, True, RED)
            self.screen.blit(wanted_surface, (10, 110))
        
        # Текущая миссия
        if self.current_mission < len(self.missions):
            mission = self.missions[self.current_mission]
            mission_text = self.small_font.render(f"Миссия: {mission.description}", True, GREEN)
            self.screen.blit(mission_text, (250, 10))
            
            # Расстояние до цели
            distance = math.sqrt((self.player.x - mission.target_x)**2 + (self.player.y - mission.target_y)**2)
            distance_text = self.small_font.render(f"Расстояние: {int(distance)}м", True, WHITE)
            self.screen.blit(distance_text, (250, 35))
        else:
            complete_text = self.large_font.render("ВСЕ МИССИИ ВЫПОЛНЕНЫ!", True, YELLOW)
            text_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(complete_text, text_rect)
        
        # Время суток
        time_text = "День" if 25 < self.time_of_day < 75 else "Ночь"
        if self.time_of_day <= 25 or self.time_of_day >= 75:
            time_color = BLUE
        else:
            time_color = YELLOW
        
        time_surface = self.small_font.render(f"Время: {time_text}", True, time_color)
        self.screen.blit(time_surface, (250, 60))
        
        # Управление
        controls = [
            "WASD/Стрелки - движение",
            "R - рестарт",
            "SPACE - увеличить розыск",
            "M - добавить деньги",
            "ESC - выход"
        ]
        
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 280, 10 + i * 20))
        
        # Сообщения
        for message in self.messages:
            alpha = min(255, message['timer'] * 2)
            text_surface = self.small_font.render(message['text'], True, message['color'])
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, (SCREEN_WIDTH//2 - 100, 200 + message['y_offset']))
    
    def run(self):
        self.add_message("Добро пожаловать в GTA San Andreas Mini!", GREEN)
        
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