import pygame
import sys
import math
from logic import GameLogic, BallState, Vector2

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
BACKGROUND_COLOR = (255, 255, 255)  # Белый фон

# Цвета интерфейса
UI_COLOR = (240, 240, 240)
BORDER_COLOR = (200, 200, 200)
TEXT_COLOR = (50, 50, 50)
DELETION_ZONE_COLOR = (255, 100, 100, 100)  # Полупрозрачный красный
ABSORPTION_CIRCLE_COLOR = (100, 150, 255, 80)  # Полупрозрачный синий

# Настройки игры
INITIAL_BALLS_COUNT = 8  # Стартовое количество шариков


class GameRenderer:
    """Класс для отрисовки игровых элементов"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Создаем поверхности для полупрозрачных элементов
        self.transparent_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    def draw_ball(self, ball):
        """Отрисовка одного шарика"""
        x, y = int(ball.position.x), int(ball.position.y)
        radius = int(ball.radius)
        color = ball.color.to_tuple()
        
        # Основной шарик
        pygame.draw.circle(self.screen, color, (x, y), radius)
        
        # Блик для объема
        highlight_color = tuple(min(255, c + 60) for c in color)
        highlight_offset = radius // 3
        pygame.draw.circle(
            self.screen, 
            highlight_color, 
            (x - highlight_offset, y - highlight_offset), 
            radius // 3
        )
        
        # Тонкая обводка
        outline_color = tuple(max(0, c - 40) for c in color)
        pygame.draw.circle(self.screen, outline_color, (x, y), radius, 2)
        
        # Анимация всасывания/выплевывания
        if ball.state == BallState.BEING_ABSORBED:
            self._draw_absorption_effect(ball)
        elif ball.state == BallState.BEING_RELEASED:
            self._draw_release_effect(ball)
    
    def _draw_absorption_effect(self, ball):
        """Эффект всасывания"""
        progress = ball.absorption_progress
        effect_radius = int(ball.radius * (1.5 - progress * 0.5))
        effect_alpha = int(100 * (1 - progress))
        
        if effect_alpha > 0:
            # Создаем поверхность для эффекта
            effect_surface = pygame.Surface((effect_radius * 2, effect_radius * 2), pygame.SRCALPHA)
            effect_color = (*ball.color.to_tuple(), effect_alpha)
            pygame.draw.circle(effect_surface, effect_color, (effect_radius, effect_radius), effect_radius, 3)
            
            x, y = int(ball.position.x), int(ball.position.y)
            self.screen.blit(effect_surface, (x - effect_radius, y - effect_radius))
    
    def _draw_release_effect(self, ball):
        """Эффект выплевывания"""
        progress = 1.0 - ball.absorption_progress
        effect_radius = int(ball.radius * (1 + progress * 0.8))
        effect_alpha = int(80 * progress)
        
        if effect_alpha > 0:
            effect_surface = pygame.Surface((effect_radius * 2, effect_radius * 2), pygame.SRCALPHA)
            effect_color = (*ball.color.to_tuple(), effect_alpha)
            pygame.draw.circle(effect_surface, effect_color, (effect_radius, effect_radius), effect_radius, 2)
            
            x, y = int(ball.position.x), int(ball.position.y)
            self.screen.blit(effect_surface, (x - effect_radius, y - effect_radius))
    
    def draw_inventory(self, inventory):
        """Отрисовка инвентаря"""
        # Фон инвентаря
        inventory_rect = pygame.Rect(10, 10, 260, 120)
        pygame.draw.rect(self.screen, UI_COLOR, inventory_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, inventory_rect, 2)
        
        # Заголовок
        title_text = self.font.render("Инвентарь", True, TEXT_COLOR)
        self.screen.blit(title_text, (20, 20))
        
        # Счетчик шариков
        count_text = f"{len(inventory.balls)}/{inventory.max_size}"
        count_surface = self.small_font.render(count_text, True, TEXT_COLOR)
        self.screen.blit(count_surface, (220, 22))
        
        # Слоты инвентаря
        slot_size = 40
        slots_per_row = 5
        start_x, start_y = 20, 50
        
        for i in range(inventory.max_size):
            slot_x = start_x + (i % slots_per_row) * (slot_size + 5)
            slot_y = start_y + (i // slots_per_row) * (slot_size + 5)
            
            # Рамка слота
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            pygame.draw.rect(self.screen, (250, 250, 250), slot_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, slot_rect, 1)
            
            # Шарик в слоте
            if i < len(inventory.balls):
                ball = inventory.balls[i]
                ball_x = slot_x + slot_size // 2
                ball_y = slot_y + slot_size // 2
                ball_radius = min(15, int(ball.radius * 0.8))
                
                # Отрисовка мини-шарика
                pygame.draw.circle(self.screen, ball.color.to_tuple(), (ball_x, ball_y), ball_radius)
                pygame.draw.circle(self.screen, BORDER_COLOR, (ball_x, ball_y), ball_radius, 1)
    
    def draw_deletion_zone(self, deletion_zone):
        """Отрисовка зоны удаления"""
        # Полупрозрачный красный прямоугольник
        self.transparent_surface.fill((0, 0, 0, 0))  # Очищаем
        zone_rect = pygame.Rect(
            deletion_zone.x, deletion_zone.y, 
            deletion_zone.width, deletion_zone.height
        )
        pygame.draw.rect(self.transparent_surface, DELETION_ZONE_COLOR, zone_rect)
        self.screen.blit(self.transparent_surface, (0, 0))
        
        # Обводка
        pygame.draw.rect(self.screen, (255, 0, 0), zone_rect, 2)
        
        # Текст
        text = self.small_font.render("УДАЛЕНИЕ", True, (255, 0, 0))
        text_rect = text.get_rect(center=(zone_rect.centerx, zone_rect.centery))
        self.screen.blit(text, text_rect)
    
    def draw_absorption_radius(self, mouse_pos, radius):
        """Отрисовка радиуса всасывания вокруг мыши"""
        self.transparent_surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.transparent_surface, ABSORPTION_CIRCLE_COLOR, mouse_pos, radius, 3)
        self.screen.blit(self.transparent_surface, (0, 0))
    
    def draw_ui_info(self, game_logic):
        """Отрисовка дополнительной информации"""
        # Информационная панель
        info_rect = pygame.Rect(SCREEN_WIDTH - 200, 10, 180, 80)
        pygame.draw.rect(self.screen, UI_COLOR, info_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, info_rect, 2)
        
        # Количество шариков на экране
        balls_count = len([ball for ball in game_logic.balls if ball.state == BallState.FREE])
        balls_text = f"Шариков: {balls_count}"
        balls_surface = self.small_font.render(balls_text, True, TEXT_COLOR)
        self.screen.blit(balls_surface, (SCREEN_WIDTH - 190, 20))
        
        # Инструкции
        instructions = [
            "ЛКМ - всосать",
            "ПКМ - выплюнуть", 
            "SPACE - новый шарик"
        ]
        for i, instruction in enumerate(instructions):
            inst_surface = self.small_font.render(instruction, True, TEXT_COLOR)
            self.screen.blit(inst_surface, (SCREEN_WIDTH - 190, 40 + i * 15))


class BallGame:
    """Основной класс игры"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Игра про шарики")
        self.clock = pygame.time.Clock()
        
        # Игровая логика
        self.game_logic = GameLogic(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Генерируем дополнительные шарики до нужного количества
        current_balls = len(self.game_logic.balls)
        for _ in range(max(0, INITIAL_BALLS_COUNT - current_balls)):
            self.game_logic.add_random_ball()
        
        # Рендерер
        self.renderer = GameRenderer(self.screen)
        
        # Состояние мыши
        self.mouse_pressed = {"left": False, "right": False}
        
        # Настройки управления
        self.absorption_cooldown = 0
        self.release_cooldown = 0
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    self.mouse_pressed["left"] = True
                elif event.button == 3:  # ПКМ
                    self.mouse_pressed["right"] = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed["left"] = False
                elif event.button == 3:
                    self.mouse_pressed["right"] = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Добавить новый случайный шарик
                    self.game_logic.add_random_ball()
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def update(self, dt):
        """Обновление игровой логики"""
        # Обновляем позицию мыши
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.game_logic.set_mouse_position(mouse_x, mouse_y)
        
        # Обновляем кулдауны
        self.absorption_cooldown = max(0, self.absorption_cooldown - dt)
        self.release_cooldown = max(0, self.release_cooldown - dt)
        
        # Обработка всасывания (ЛКМ с кулдауном)
        if self.mouse_pressed["left"] and self.absorption_cooldown <= 0:
            if self.game_logic.try_absorb_ball():
                self.absorption_cooldown = 0.2  # Кулдаун 200мс
        
        # Обработка выплевывания (ПКМ с кулдауном)
        if self.mouse_pressed["right"] and self.release_cooldown <= 0:
            if self.game_logic.release_ball():
                self.release_cooldown = 0.3  # Кулдаун 300мс
        
        # Обновляем игровую логику
        self.game_logic.update(dt)
    
    def render(self):
        """Отрисовка игры"""
        # Очищаем экран
        self.screen.fill(BACKGROUND_COLOR)
        
        # Отрисовываем зону удаления
        self.renderer.draw_deletion_zone(self.game_logic.deletion_zone)
        
        # Отрисовываем радиус всасывания при нажатой ЛКМ
        if self.mouse_pressed["left"]:
            mouse_pos = pygame.mouse.get_pos()
            self.renderer.draw_absorption_radius(mouse_pos, self.game_logic.absorption_radius)
        
        # Отрисовываем все шарики
        for ball in self.game_logic.balls:
            if ball.state in [BallState.FREE, BallState.BEING_ABSORBED, BallState.BEING_RELEASED]:
                self.renderer.draw_ball(ball)
        
        # Отрисовываем интерфейс
        self.renderer.draw_inventory(self.game_logic.inventory)
        self.renderer.draw_ui_info(self.game_logic)
        
        # Обновляем экран
        pygame.display.flip()
    
    def run(self):
        """Основной игровой цикл"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Время в секундах
            
            # Обрабатываем события
            running = self.handle_events()
            
            # Обновляем логику
            self.update(dt)
            
            # Отрисовываем
            self.render()
        
        pygame.quit()
        sys.exit()


def main():
    """Точка входа в программу"""
    print("🎮 Запуск игры про шарики...")
    print(f"📊 Стартовое количество шариков: {INITIAL_BALLS_COUNT}")
    print("🎯 Управление:")
    print("   • ЛКМ - всасывать шарики")
    print("   • ПКМ - выплевывать шарики")
    print("   • SPACE - добавить новый шарик")
    print("   • ESC - выход")
    print("🎨 Шарики смешивают цвета при столкновении")
    print("🗑️ Красная зона - удаление шариков")
    print()
    
    try:
        game = BallGame()
        game.run()
    except Exception as e:
        print(f"❌ Ошибка запуска игры: {e}")
        print("💡 Убедитесь, что установлен pygame: pip install pygame")
        sys.exit(1)


if __name__ == "__main__":
    main()
