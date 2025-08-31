import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class Vector2:
    """Простой 2D вектор для позиций и скоростей"""
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)
    
    def distance_to(self, other):
        return (self - other).magnitude()


class BallState(Enum):
    """Состояния шарика"""
    FREE = "free"           # Свободно движется
    IN_INVENTORY = "inventory"  # В инвентаре
    BEING_ABSORBED = "absorbing"  # Процесс всасывания
    BEING_RELEASED = "releasing"  # Процесс выплевывания


class Color:
    """Класс для работы с цветами в RGB"""
    
    def __init__(self, r: int, g: int, b: int):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
    
    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b
    
    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"
    
    def to_tuple(self):
        return (self.r, self.g, self.b)
    
    def is_white(self, threshold=240):
        """Проверка, является ли цвет близким к белому (плохой результат)"""
        return self.r >= threshold and self.g >= threshold and self.b >= threshold
    
    @classmethod
    def random_vibrant(cls):
        """Создает случайный яркий цвет"""
        colors = [
            (255, 100, 100),  # Красный
            (100, 255, 100),  # Зеленый
            (100, 100, 255),  # Синий
            (255, 255, 100),  # Желтый
            (255, 100, 255),  # Пурпурный
            (100, 255, 255),  # Циан
            (255, 150, 50),   # Оранжевый
            (150, 50, 255),   # Фиолетовый
        ]
        r, g, b = random.choice(colors)
        # Добавляем небольшое случайное отклонение
        r += random.randint(-30, 30)
        g += random.randint(-30, 30)
        b += random.randint(-30, 30)
        return cls(r, g, b)


class ColorMixer:
    """Класс для математического смешивания цветов через RGB-модель"""
    
    @staticmethod
    def mix_colors(color1: Color, color2: Color) -> Color:
        """
        Математическое смешивание двух цветов в RGB пространстве.
        Использует усреднение компонентов RGB для точного результата.
        """
        # Простое усреднение RGB компонентов
        r = (color1.r + color2.r) // 2
        g = (color1.g + color2.g) // 2
        b = (color1.b + color2.b) // 2
        
        return Color(r, g, b)


class Ball:
    """Класс шарика с логикой движения и взаимодействия"""
    
    def __init__(self, position: Vector2, radius: float = 20, color: Color = None):
        self.id = random.randint(1000, 9999)  # Уникальный ID
        self.position = position
        self.velocity = Vector2(
            random.uniform(-50, 50),  # Случайная скорость
            random.uniform(-50, 50)
        )
        self.radius = radius
        self.color = color or Color.random_vibrant()
        self.state = BallState.FREE
        self.mass = radius * 0.1  # Масса зависит от размера
        
        # Для анимации всасывания/выплевывания
        self.target_position: Optional[Vector2] = None
        self.absorption_progress = 0.0  # От 0 до 1
        
    def update(self, dt: float, screen_width: int, screen_height: int):
        """Обновление состояния шарика"""
        if self.state == BallState.FREE:
            self._update_free_movement(dt, screen_width, screen_height)
        elif self.state == BallState.BEING_ABSORBED:
            self._update_absorption(dt)
        elif self.state == BallState.BEING_RELEASED:
            self._update_release(dt)
    
    def _update_free_movement(self, dt: float, screen_width: int, screen_height: int):
        """Обновление свободного движения"""
        # Обновляем позицию
        self.position = self.position + self.velocity * dt
        
        # Отражение от границ экрана
        if self.position.x <= self.radius or self.position.x >= screen_width - self.radius:
            self.velocity.x *= -0.8  # Немного теряем энергию при отражении
        if self.position.y <= self.radius or self.position.y >= screen_height - self.radius:
            self.velocity.y *= -0.8
        
        # Корректируем позицию, чтобы шарик не выходил за границы
        self.position.x = max(self.radius, min(screen_width - self.radius, self.position.x))
        self.position.y = max(self.radius, min(screen_height - self.radius, self.position.y))
        
        # Добавляем небольшое трение
        friction = 0.99
        self.velocity = self.velocity * friction
    
    def _update_absorption(self, dt: float):
        """Обновление процесса всасывания"""
        if self.target_position is None:
            return
        
        self.absorption_progress += dt * 3.0  # Скорость всасывания
        
        if self.absorption_progress >= 1.0:
            self.absorption_progress = 1.0
            self.state = BallState.IN_INVENTORY
            self.position = self.target_position
        else:
            # Плавное движение к цели
            start_pos = self.position
            progress = self._ease_in_out(self.absorption_progress)
            self.position = Vector2(
                start_pos.x + (self.target_position.x - start_pos.x) * progress,
                start_pos.y + (self.target_position.y - start_pos.y) * progress
            )
    
    def _update_release(self, dt: float):
        """Обновление процесса выплевывания"""
        self.absorption_progress -= dt * 4.0  # Скорость выплевывания
        
        if self.absorption_progress <= 0.0:
            self.absorption_progress = 0.0
            self.state = BallState.FREE
        else:
            # Плавное движение от цели
            progress = self._ease_in_out(1.0 - self.absorption_progress)
            if self.target_position:
                self.position = Vector2(
                    self.target_position.x + (self.position.x - self.target_position.x) * progress,
                    self.target_position.y + (self.position.y - self.target_position.y) * progress
                )
    
    def _ease_in_out(self, t: float) -> float:
        """Функция сглаживания для плавной анимации"""
        return t * t * (3.0 - 2.0 * t)
    
    def start_absorption(self, target_pos: Vector2):
        """Начать процесс всасывания"""
        self.state = BallState.BEING_ABSORBED
        self.target_position = target_pos
        self.absorption_progress = 0.0
    
    def start_release(self, release_pos: Vector2, release_velocity: Vector2):
        """Начать процесс выплевывания"""
        self.state = BallState.BEING_RELEASED
        self.position = release_pos
        self.velocity = release_velocity
        self.absorption_progress = 1.0
    
    def can_collide_with(self, other: 'Ball') -> bool:
        """Проверка возможности столкновения с другим шариком"""
        return (self.state == BallState.FREE and 
                other.state == BallState.FREE and 
                self.id != other.id)
    
    def collides_with(self, other: 'Ball') -> bool:
        """Проверка столкновения с другим шариком"""
        if not self.can_collide_with(other):
            return False
        
        distance = self.position.distance_to(other.position)
        return distance <= (self.radius + other.radius)
    
    def merge_with(self, other: 'Ball') -> 'Ball':
        """Слияние с другим шариком"""
        # Новая позиция - средняя между шариками
        new_pos = Vector2(
            (self.position.x + other.position.x) / 2,
            (self.position.y + other.position.y) / 2
        )
        
        # Новый размер учитывает массы обоих шариков
        new_radius = math.sqrt(self.radius**2 + other.radius**2) * 0.8  # Немного уменьшаем
        
        # Смешиваем цвета
        new_color = ColorMixer.mix_colors(self.color, other.color)
        
        # Новая скорость - сохранение импульса
        total_mass = self.mass + other.mass
        new_velocity = Vector2(
            (self.velocity.x * self.mass + other.velocity.x * other.mass) / total_mass,
            (self.velocity.y * self.mass + other.velocity.y * other.mass) / total_mass
        )
        
        # Создаем новый шарик
        new_ball = Ball(new_pos, new_radius, new_color)
        new_ball.velocity = new_velocity
        
        return new_ball


class DeletionZone:
    """Зона удаления шариков"""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def contains_point(self, position: Vector2) -> bool:
        """Проверка, находится ли точка в зоне удаления"""
        return (self.x <= position.x <= self.x + self.width and
                self.y <= position.y <= self.y + self.height)
    
    def contains_ball(self, ball: Ball) -> bool:
        """Проверка, находится ли шарик в зоне удаления"""
        return (ball.state == BallState.FREE and 
                self.contains_point(ball.position))


class Inventory:
    """Инвентарь для хранения шариков"""
    
    def __init__(self, max_size: int = 10):
        self.balls: List[Ball] = []
        self.max_size = max_size
        self.position = Vector2(50, 50)  # Позиция инвентаря на экране
    
    def can_add_ball(self) -> bool:
        """Проверка возможности добавления шарика"""
        return len(self.balls) < self.max_size
    
    def add_ball(self, ball: Ball):
        """Добавление шарика в инвентарь"""
        if self.can_add_ball():
            ball.start_absorption(self._get_slot_position(len(self.balls)))
            self.balls.append(ball)
    
    def remove_ball(self, index: int = -1) -> Optional[Ball]:
        """Удаление шарика из инвентаря (последний по умолчанию)"""
        if self.balls:
            return self.balls.pop(index)
        return None
    
    def _get_slot_position(self, slot_index: int) -> Vector2:
        """Получение позиции слота в инвентаре"""
        slot_size = 50
        return Vector2(
            self.position.x + (slot_index % 5) * slot_size,
            self.position.y + (slot_index // 5) * slot_size
        )
    
    def get_ball_at_position(self, pos: Vector2) -> Optional[Ball]:
        """Получение шарика в указанной позиции"""
        for ball in self.balls:
            if ball.position.distance_to(pos) <= ball.radius:
                return ball
        return None


class GameLogic:
    """Основной класс игровой логики"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.balls: List[Ball] = []
        self.inventory = Inventory()
        self.deletion_zone = DeletionZone(
            screen_width - 100, 0, 100, 100  # Правый верхний угол
        )
        
        # Параметры всасывания
        self.absorption_radius = 80  # Радиус всасывания мышкой
        self.mouse_position = Vector2(400, 300)
        
        # Генерируем начальные шарики
        self._generate_initial_balls(5)
    
    def _generate_initial_balls(self, count: int):
        """Генерация начальных шариков"""
        for _ in range(count):
            # Случайная позиция с отступом от краев
            pos = Vector2(
                random.uniform(50, self.screen_width - 50),
                random.uniform(50, self.screen_height - 50)
            )
            
            # Случайный размер
            radius = random.uniform(15, 35)
            
            ball = Ball(pos, radius)
            self.balls.append(ball)
    
    def update(self, dt: float):
        """Обновление игровой логики"""
        # Обновляем все шарики
        for ball in self.balls[:]:  # Копия списка для безопасного изменения
            ball.update(dt, self.screen_width, self.screen_height)
            
            # Проверяем удаление в зоне удаления
            if self.deletion_zone.contains_ball(ball):
                self.balls.remove(ball)
        
        # Обновляем шарики в инвентаре
        for ball in self.inventory.balls:
            ball.update(dt, self.screen_width, self.screen_height)
        
        # Проверяем столкновения и слияния
        self._handle_collisions()
    
    def _handle_collisions(self):
        """Обработка столкновений шариков"""
        merged_pairs = set()
        
        for i, ball1 in enumerate(self.balls):
            for j, ball2 in enumerate(self.balls[i+1:], i+1):
                if (i, j) in merged_pairs or (j, i) in merged_pairs:
                    continue
                
                if ball1.collides_with(ball2):
                    # Создаем новый шарик из слияния
                    new_ball = ball1.merge_with(ball2)
                    
                    # Удаляем старые шарики
                    self.balls.remove(ball1)
                    self.balls.remove(ball2)
                    
                    # Добавляем новый
                    self.balls.append(new_ball)
                    
                    merged_pairs.add((i, j))
                    break
    
    def set_mouse_position(self, x: float, y: float):
        """Установка позиции мыши"""
        self.mouse_position = Vector2(x, y)
    
    def try_absorb_ball(self) -> bool:
        """Попытка всосать шарик мышкой"""
        if not self.inventory.can_add_ball():
            return False
        
        # Ищем ближайший шарик в радиусе всасывания
        closest_ball = None
        closest_distance = float('inf')
        
        for ball in self.balls:
            if ball.state == BallState.FREE:
                distance = ball.position.distance_to(self.mouse_position)
                if distance <= self.absorption_radius and distance < closest_distance:
                    closest_ball = ball
                    closest_distance = distance
        
        if closest_ball:
            self.balls.remove(closest_ball)
            self.inventory.add_ball(closest_ball)
            return True
        
        return False
    
    def release_ball(self, direction: Vector2 = None) -> bool:
        """Выплевывание шарика из инвентаря"""
        ball = self.inventory.remove_ball()
        if ball is None:
            return False
        
        # Позиция выплевывания - рядом с мышкой
        release_pos = Vector2(
            self.mouse_position.x + random.uniform(-30, 30),
            self.mouse_position.y + random.uniform(-30, 30)
        )
        
        # Скорость выплевывания
        if direction is None:
            direction = Vector2(
                random.uniform(-100, 100),
                random.uniform(-100, 100)
            )
        
        ball.start_release(release_pos, direction)
        self.balls.append(ball)
        return True
    
    def add_random_ball(self):
        """Добавление случайного шарика"""
        pos = Vector2(
            random.uniform(50, self.screen_width - 50),
            random.uniform(50, self.screen_height - 50)
        )
        radius = random.uniform(15, 35)
        ball = Ball(pos, radius)
        self.balls.append(ball)
    
    def get_game_state(self) -> dict:
        """Получение текущего состояния игры для интерфейса"""
        return {
            'balls': [
                {
                    'id': ball.id,
                    'position': ball.position.to_tuple() if hasattr(ball.position, 'to_tuple') else (ball.position.x, ball.position.y),
                    'radius': ball.radius,
                    'color': ball.color.to_tuple(),
                    'state': ball.state.value
                }
                for ball in self.balls
            ],
            'inventory_balls': [
                {
                    'id': ball.id,
                    'position': (ball.position.x, ball.position.y),
                    'radius': ball.radius,
                    'color': ball.color.to_tuple(),
                    'state': ball.state.value
                }
                for ball in self.inventory.balls
            ],
            'inventory_slots_used': len(self.inventory.balls),
            'inventory_max_slots': self.inventory.max_size,
            'deletion_zone': {
                'x': self.deletion_zone.x,
                'y': self.deletion_zone.y,
                'width': self.deletion_zone.width,
                'height': self.deletion_zone.height
            },
            'mouse_position': (self.mouse_position.x, self.mouse_position.y),
            'absorption_radius': self.absorption_radius
        }


# Пример использования (для тестирования без интерфейса)
if __name__ == "__main__":
    # Создаем игру
    game = GameLogic(800, 600)
    
    # Симуляция игрового цикла
    dt = 1/60  # 60 FPS
    
    for frame in range(300):  # 5 секунд симуляции
        game.update(dt)
        
        # Каждые 60 кадров пытаемся всосать шарик
        if frame % 60 == 0:
            game.set_mouse_position(400, 300)
            absorbed = game.try_absorb_ball()
            if absorbed:
                print(f"Кадр {frame}: Шарик всосан")
        
        # Каждые 120 кадров выплевываем шарик
        if frame % 120 == 0 and frame > 0:
            released = game.release_ball()
            if released:
                print(f"Кадр {frame}: Шарик выплеван")
        
        # Выводим состояние каждые 60 кадров
        if frame % 60 == 0:
            state = game.get_game_state()
            print(f"Кадр {frame}: Шариков на экране: {len(state['balls'])}, в инвентаре: {state['inventory_slots_used']}")
