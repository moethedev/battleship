import json
import random
import sys

class Position:
    
    def __init__(self, ships):
        self.boardHeight = 20
        self.boardWidth = 8
        self.ships = ships
        self.ship_type = {
            "CV": 4, # Carrier
            "BB": 4, # Battleship
            "OR": 2, # Oil rig
            "CA": 3, # Cruiser
            "DD": 2, # Destroyer
        }
        self.positions = []
        self.filter_positions = []

    # -----------------------------------------------------------------------------------------------------
    def generate(self):

        mode = random.choice([1, 2, 3])
        mode = 1

        if len(self.ships) > 7:
            mode = 0

        for ship in self.ships:
            for i in range(0, ship['quantity']):
                is_exist = False
                while not is_exist:
                    size = self.ship_type.get(ship['type'], [])
                    position = self.generate_position_randomly(size, ship['type'], mode)

                    if not self.is_ship_exist(position):
                        is_exist = True
                        self.positions.append({'coordinates': position, 'type': ship['type']})
                        self.filter_positions.extend(position)
                    else:
                        continue

        return self.positions

    # -----------------------------------------------------------------------------------------------------
    def is_ship_exist(self, positions):
        is_exist = False
        filter_position = self.get_filter_position()
        for pos in positions:
            if pos in self.filter_positions:
                is_exist = True
        return is_exist

    def generate_position_randomly(self, size, ship_type, mode):
        # odd for horizontal and even for vertical, pick row and column
        direction = random.randint(1, size)

        row = random.randint(0, 19)
        col = random.randint(0, 7)

        row, col = self.place_mode(row, col, mode, ship_type, direction)

        positions = self.get_simple_position(direction, row, col, size)

        if ship_type == "OR":
            if (direction % 2 != 0) :
                extra_positions = self.get_simple_position(direction, row, col + 1, size)
            else:
                extra_positions = self.get_simple_position(direction, row + 1, col, size)
            positions.extend(extra_positions)
        elif ship_type == "CV":
            if (direction % 2 != 0) :
                if (row - size > 0):
                    fix_row = row - 2
                else:
                    fix_row = row + 1
                extra_positions = self.get_simple_position(direction, fix_row, col - 1, 1)
            else:
                if (col - size > 0):
                    fix_col = col - 2
                else:
                    fix_col = col + 1
                extra_positions = self.get_simple_position(direction, row - 1, fix_col, 1)
            positions.extend(extra_positions)

        return positions

    def get_simple_position(self, direction, row, col, size):
        positions = []
        if (direction % 2 != 0) :
            # left first, then right
            if (row - size > 0):
                for i in range(0, size):
                    positions.append([row - i, col])
            else: # row
                for i in range(0, size):
                    positions.append([row + i, col])
        else:
            # top first, then bottom
            if (col - size > 0):
                for i in range(0, size):
                    positions.append([row, col - i])
            else: # row
                for i in range(0, size):
                    positions.append([row, col + i])
        return positions
    
    # -----------------------------------------------------------------------------------------------------
    def get_filter_position(self):
        filter_position = []
        for target_row, target_col in self.filter_positions:
            filter_position.extend([(target_row + 1, target_col), (target_row, target_col + 1),
                            (target_row - 1, target_col), (target_row, target_col - 1)])

        data = []
        for guess_row, guess_col in filter_position:
                if (0 <= guess_row < self.boardHeight) and \
                        (0 <= guess_col < self.boardWidth) and \
                        ([guess_row, guess_col] not in self.positions):
                    data.append((guess_row, guess_col))

        return filter_position

    # -----------------------------------------------------------------------------------------------------
    def place_mode(self, row, col, mode, ship_type, direction):

        if ship_type == "CV":
                row = random.randint(1, 19) 
                col = random.randint(1, 6)
        if ship_type == "OR":
                if (direction % 2 != 0) :
                    col = random.randint(1, 6)
                else:
                    row = random.randint(1, 18)
                    
        if direction == 1: # horizontal
            if ship_type == "DD":
                row = random.randint(0, 19)
        else:
            if ship_type == "DD":
                col = random.choice([0, 7])

        if mode == 1:
            if ship_type == "DD":
                    row = random.choice([1, 18])
                    col = random.choice([1, 6])
            if ship_type == "CA":
                    row = random.choice([1, 18])
                    col = random.choice([1, 6])

        return row, col