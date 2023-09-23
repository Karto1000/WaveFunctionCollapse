import random
from enum import Enum
from typing import Optional

import pygame

pygame.init()

SW, SH = 1000, 1000
SCREEN = pygame.display.set_mode((SW, SH))
CELL_SIZE = 10, 10


class CellType(Enum):
    UP = [True, False, True, False]
    RIGHT = [False, True, False, True]

    UP_RIGHT = [False, True, True, False]
    UP_LEFT = [False, False, True, True]
    DOWN_RIGHT = [True, True, False, False]
    DOWN_LEFT = [True, False, False, True]

    FORK_UP_RIGHT = [True, True, True, False]
    FORK_UP_LEFT = [True, False, True, True]
    FORK_RIGHT_UP = [True, True, False, True]
    FORK_RIGHT_DOWN = [False, True, True, True]

    CROSS = [True, True, True, True]


class CellSide(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def get_opposite(self) -> 'CellSide':
        if self == CellSide.RIGHT:
            return CellSide.LEFT
        elif self == CellSide.LEFT:
            return CellSide.RIGHT
        elif self == CellSide.UP:
            return CellSide.DOWN
        elif self == CellSide.DOWN:
            return CellSide.UP


class Cell:
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y
        self.type = None
        self.available_options = list(CellType)
        self.is_collapsed = False
        self.color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))

    def remove_cell_side(self, side: CellSide, has_connection: bool):
        new_options = self.available_options.copy()

        for option in self.available_options:
            o_side = option.value[side.get_opposite().value]

            if not o_side and has_connection:
                new_options.remove(option)
            elif o_side and not has_connection:
                new_options.remove(option)

        self.available_options = new_options

    def get_entropy(self) -> int:
        return len(self.available_options)

    def draw(self):
        if not self.type:
            return

        # Draw rectangles based on cell connections of type
        # UP RIGHT DOWN LEFT

        rect_width = CELL_SIZE[0] // 4
        rect_height = CELL_SIZE[1] // 4

        horizontal_center = self.x * CELL_SIZE[0] + CELL_SIZE[0] // 2
        vertical_center = self.y * CELL_SIZE[1] + CELL_SIZE[1] // 2

        # pygame.draw.rect(
        #     SCREEN,
        #     self.color,
        #     (self.x * CELL_SIZE[0], self.y * CELL_SIZE[1], CELL_SIZE[0], CELL_SIZE[1])
        # )

        # UP
        if self.type.value[0]:
            pygame.draw.rect(
                SCREEN,
                (0, 0, 0),
                (horizontal_center - rect_width // 2, self.y * CELL_SIZE[1], rect_width,
                 CELL_SIZE[1] / 2 + rect_height // 2)
            )

        # Right
        if self.type.value[1]:
            pygame.draw.rect(
                SCREEN,
                (0, 0, 0),
                (horizontal_center - rect_width // 2, vertical_center - rect_height // 2,
                 CELL_SIZE[0] / 2 + rect_width // 2, rect_height)
            )

        if self.type.value[2]:
            pygame.draw.rect(
                SCREEN,
                (0, 0, 0),
                (horizontal_center - rect_width // 2, vertical_center - rect_height // 2, rect_width,
                 CELL_SIZE[1] // 2 + rect_height // 2)
            )

        if self.type.value[3]:
            pygame.draw.rect(
                SCREEN,
                (0, 0, 0),
                (self.x * CELL_SIZE[0], vertical_center - rect_height // 2, rect_width + rect_width, rect_height)

            )

    def collapse(self):
        cell_type = random.choice(self.available_options)
        self.type = cell_type
        self.is_collapsed = True
        return self.type


class CellManager:
    def __init__(self):
        self.cells = []

        for y in range(0, SH // CELL_SIZE[1]):
            y_list = []

            for x in range(0, SW // CELL_SIZE[0]):
                y_list.append(Cell(x, y))

            self.cells.append(y_list)

    def draw(self):
        for cell in self.cells:
            for c in cell:
                c.draw()

    def get_lowest_entropy(self) -> Optional[Cell]:
        smallest = 100
        tiles = []

        for y in self.cells:
            for x in y:
                if x.is_collapsed:
                    continue
                if x.get_entropy() == smallest:
                    tiles.append(x)
                elif x.get_entropy() < smallest:
                    smallest = x.get_entropy()
                    tiles = [x]

        if len(tiles) == 0:
            return None

        return random.choice(tiles)

    def get_cell_at(self, x: int, y: int):
        if y < 0 or y >= SH // CELL_SIZE[1]:
            return None
        if x < 0 or x >= SW // CELL_SIZE[0]:
            return None
        return self.cells[y][x]

    def update(self):
        smallest = self.get_lowest_entropy()

        if smallest is None:
            return

        chosen_type: CellType = smallest.collapse()

        up = self.get_cell_at(smallest.x, smallest.y - 1)
        right = self.get_cell_at(smallest.x, smallest.y)
        down = self.get_cell_at(smallest.x, smallest.y + 1)
        left = self.get_cell_at(smallest.x - 1, smallest.y)

        if up:
            up.remove_cell_side(CellSide.UP, chosen_type.value[0])

        if right:
            right.remove_cell_side(CellSide.RIGHT, chosen_type.value[1])

        if down:
            down.remove_cell_side(CellSide.DOWN, chosen_type.value[2])

        if left:
            left.remove_cell_side(CellSide.LEFT, chosen_type.value[3])


manager = CellManager()

while True:
    SCREEN.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    manager.draw()
    manager.update()

    pygame.display.update()
