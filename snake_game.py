"""
Проект «Изгиб Питона" — классическая игра Змейка на Python с ООП.
"""

import pygame
from random import randint, choice
from typing import List, Tuple, Optional

# Константы игры
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
CELLS_WIDTH = SCREEN_WIDTH // GRID_SIZE  # 32 ячейки
CELLS_HEIGHT = SCREEN_HEIGHT // GRID_SIZE  # 24 ячейки

BOARD_BACKGROUND_COLOR = (0, 0, 0)
SNAKE_COLOR = (0, 255, 0)
APPLE_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)

# Направления движения: (dx, dy)
DIRECTION_RIGHT = (1, 0)
DIRECTION_LEFT = (-1, 0)
DIRECTION_UP = (0, -1)
DIRECTION_DOWN = (0, 1)

# Карта для изменения направления (клавиша, текущее направление) -> новое направление
DIRECTION_MAP = {
    (pygame.K_UP, DIRECTION_LEFT): DIRECTION_UP,
    (pygame.K_UP, DIRECTION_RIGHT): DIRECTION_UP,
    (pygame.K_DOWN, DIRECTION_LEFT): DIRECTION_DOWN,
    (pygame.K_DOWN, DIRECTION_RIGHT): DIRECTION_DOWN,
    (pygame.K_LEFT, DIRECTION_UP): DIRECTION_LEFT,
    (pygame.K_LEFT, DIRECTION_DOWN): DIRECTION_LEFT,
    (pygame.K_RIGHT, DIRECTION_UP): DIRECTION_RIGHT,
    (pygame.K_RIGHT, DIRECTION_DOWN): DIRECTION_RIGHT,
}


class GameObject:
    """
    Базовый класс для игровых объектов.
    
    Содержит общие атрибуты и методы для всех игровых объектов,
    такие как позиция и цвет объекта.
    """
    
    def __init__(self, position: Tuple[int, int], color: Tuple[int, int, int]):
        """
        Инициализирует базовые атрибуты объекта.
        
        Args:
            position: Позиция объекта на игровом поле (x, y).
            color: Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = color
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Абстрактный метод для отрисовки объекта на экране.
        
        Должен быть переопределён в дочерних классах.
        По умолчанию не выполняет никаких действий.
        
        Args:
            screen: Поверхность Pygame, на которой нужно отрисовать объект.
        """
        pass


class Apple(GameObject):
    """
    Класс яблока, наследуется от GameObject.
    
    Яблоко появляется в случайных клетках игрового поля
    и отрисовывается как красный квадрат размером 20x20.
    """
    
    def __init__(self, snake_positions: Optional[List[Tuple[int, int]]] = None):
        """
        Инициализирует яблоко с случайной позицией.
        
        Args:
            snake_positions: Список позиций змейки (для исключения появления яблока на змейке).
        """
        self.body_color = APPLE_COLOR
        temp_position = (0, 0)
        super().__init__(temp_position, self.body_color)
        self.randomize_position(snake_positions)
    
    def randomize_position(self, snake_positions: Optional[List[Tuple[int, int]]] = None) -> None:
        """
        Устанавливает случайное положение яблока на игровом поле.
        
        Координаты выбираются так, чтобы яблоко оказалось в пределах игрового поля
        и не совпадало с позициями змейки.
        
        Args:
            snake_positions: Список позиций змейки.
        """
        while True:
            x = randint(0, CELLS_WIDTH - 1) * GRID_SIZE
            y = randint(0, CELLS_HEIGHT - 1) * GRID_SIZE
            position = (x, y)
            
            if snake_positions is None or position not in snake_positions:
                self.position = position
                break
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовывает яблоко на игровой поверхности.
        
        Args:
            screen: Поверхность Pygame, на которой нужно отрисовать яблоко.
        """
        rect = pygame.Rect(self.position[0], self.position[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, self.body_color, rect)


class Snake(GameObject):
    """
    Класс змейки, наследуется от GameObject.
    
    Змейка состоит из сегментов, каждый из которых — это ячейка игрового поля.
    Класс управляет движением, отрисовкой, обработкой ввода и столкновениями.
    """
    
    def __init__(self):
        """
        Инициализирует начальное состояние змейки.
        
        Змейка начинается с длины 1 в центре экрана, движется вправо.
        """
        center_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions: List[Tuple[int, int]] = [center_position]
        self.direction = DIRECTION_RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.body_color = SNAKE_COLOR
        self.last: Optional[Tuple[int, int]] = None
        
        super().__init__(center_position, self.body_color)
    
    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы змейки.
        
        Returns:
            Координаты головы змейки (первый элемент списка positions).
        """
        return self.positions[0]
    
    def update_direction(self) -> None:
        """
        Обновляет направление движения змейки.
        
        Применяет следующее направление (next_direction), если оно установлено
        и не противоположно текущему направлению.
        """
        if self.next_direction is not None:
            if (self.next_direction[0] != -self.direction[0] or 
                self.next_direction[1] != -self.direction[1]):
                self.direction = self.next_direction
            self.next_direction = None
    
    def move(self) -> bool:
        """
        Обновляет позицию змейки на одну ячейку.
        
        Добавляет новую голову в начало списка positions и удаляет последний элемент,
        если длина змейки не увеличилась. Обрабатывает столкновение с собой.
        
        Returns:
            True, если произошло столкновение с собой. False — если движение успешно.
        """
        current_head = self.get_head_position()
        dx, dy = self.direction
        
        new_head = (
            (current_head[0] + dx * GRID_SIZE) % SCREEN_WIDTH,
            (current_head[1] + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        
        if new_head in self.positions[2:]:
            self.reset()
            return True
        
        self.last = self.positions[-1]
        self.positions.insert(0, new_head)
        
        if len(self.positions) > self.length:
            self.positions.pop()
        
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовывает змейку на экране, затирая след.
        
        Args:
            screen: Поверхность Pygame, на которой нужно отрисовать змейку.
        """
        for position in self.positions:
            rect = pygame.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, self.body_color, rect)
        
        if self.last is not None:
            rect = pygame.Rect(self.last[0], self.last[1], GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
    
    def reset(self) -> None:
        """
        Сбрасывает змейку в начальное состояние после столкновения с собой.
        
        Длина устанавливается равной 1, позиции сбрасываются к центру экрана,
        направление движения меняется на случайное.
        """
        self.length = 1
        center_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [center_position]
        self.direction = choice([DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT])
        self.next_direction = None
        self.last = None


def handle_keys(snake: Snake) -> None:
    """
    Обработка нажатия клавиш для изменения направления движения змейки.
    
    Args:
        snake: Экземпляр класса Snake, у которого нужно обновить направление.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return
            
            new_direction = DIRECTION_MAP.get((event.key, snake.direction))
            if new_direction is not None:
                snake.next_direction = new_direction


def main() -> None:
    """
    Основной игровой цикл.
    
    Создаёт объекты змейки и яблока, обрабатывает события, обновляет состояние
    игры, проверяет столкновения и отрисовывает объекты на экране.
    """
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Изгиб Питона — Змейка")
    
    snake = Snake()
    apple = Apple(snake.positions)
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        handle_keys(snake)
        snake.update_direction()
        
        if snake.move():
            apple.randomize_position(snake.positions)
        
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        
        screen.fill(BOARD_BACKGROUND_COLOR)
        
        snake.draw(screen)
        apple.draw(screen)
        
        pygame.display.update()
        
        clock.tick(20)
    
    pygame.quit()


if __name__ == "__main__":
    main()