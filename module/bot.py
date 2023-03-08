import random
import json
import numpy as np
import os


class Bot:
    def __init__(self, boardWidth=8, boardHeight=20, sessionID=None, data=None):
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight
        self.sessionID = sessionID

        self.SHOT_MAP = np.zeros([self.boardHeight, self.boardWidth])
        self.SIMPLE_SHOT_MAP = []

        self.TARGETS = []
        self.POTENTIAL_TARGETS = []

        data['shot_map'] = self.SHOT_MAP.tolist()
        data['simple_shot_map'] = self.SIMPLE_SHOT_MAP
        data['targets'] = self.TARGETS
        data['potential_targets'] = self.POTENTIAL_TARGETS
        self.save_file(self.sessionID, json.dumps(data))

    # -----------------------------------------------------------------------------------------------------
    def read_file(self, session_id):
        data = []
        with open("cache/" + session_id + ".json", 'r') as file:
            data = json.load(file)
        return data

    def save_file(self, session_id, data):
        if not os.path.exists("cache"):
            os.makedirs("cache")
        with open("cache/" + session_id + ".json", "w") as outfile:
            outfile.write(data)

    def shoot(self, session_id, data, max_shots):
        json_object = self.read_file(session_id)

        fire_position = []
        for i in range(0, max_shots):
            guess_row, guess_col, self.POTENTIAL_TARGETS = self.hunt_target(self.TARGETS, self.POTENTIAL_TARGETS,
                                                                            self.SHOT_MAP)
            fire_position.append([guess_row, guess_col])

            self.SHOT_MAP[guess_row][guess_col] = 2
            self.SIMPLE_SHOT_MAP.append([guess_row, guess_col])

        return fire_position

    def get_potential_targets(self, shot_map):
        potential_targets = []
        A = []
        for j in range(self.boardWidth):
            for i in range(self.boardHeight):
                if shot_map[i][j] == 1:
                    A.append((i, j))
                    if i > 0 and shot_map[i - 1][j] == 0:
                        potential_targets.append((i - 1, j))
                    if i < self.boardHeight - 1 and shot_map[i + 1][j] == 0:
                        potential_targets.append((i + 1, j))
                    if j > 0 and shot_map[i][j - 1] == 0:
                        potential_targets.append((i, j - 1))
                    if j < self.boardWidth - 1 and shot_map[i][j + 1] == 0:
                        potential_targets.append((i, j + 1))
        return potential_targets


    def get_longest_adjacent_points(self, shot_map):
        A = []
        for j in range(self.boardWidth):
            for i in range(self.boardHeight):
                if shot_map[i][j] == 1:
                    A.append((i, j))
        points_by_row = {}
        points_by_col = {}
        for point in A:
            x, y = point
            if x not in points_by_row:
                points_by_row[x] = []
            if y not in points_by_col:
                points_by_col[y] = []
            points_by_row[x].append(point)
            points_by_col[y].append(point)

        max_adjacent_points = []
        isRow = True
        for row in points_by_row.values():
            row.sort()
            adjacent_points = []
            for i in range(len(row) - 1):
                if row[i + 1][1] - row[i][1] == 1:
                    if row[i] not in adjacent_points:
                        adjacent_points.append(row[i])
                    adjacent_points.append(row[i + 1])
                else:
                    if len(adjacent_points) > len(max_adjacent_points):
                        max_adjacent_points = adjacent_points
                    adjacent_points = []
            if len(adjacent_points) > len(max_adjacent_points):
                max_adjacent_points = adjacent_points

        for col in points_by_col.values():
            col.sort()
            adjacent_points = []
            for i in range(len(col) - 1):
                if col[i + 1][0] - col[i][0] == 1:
                    if col[i] not in adjacent_points:
                        adjacent_points.append(col[i])
                    adjacent_points.append(col[i + 1])
                else:
                    if len(adjacent_points) > len(max_adjacent_points):
                        max_adjacent_points = adjacent_points
                        isRow = False
                    adjacent_points = []
            if len(adjacent_points) > len(max_adjacent_points):
                max_adjacent_points = adjacent_points
                isRow = False

        potential_targets = []
        if len(max_adjacent_points) > 0:
            if isRow:
                guess_X = max_adjacent_points[0][0]
                guess_Y = max_adjacent_points[0][1]
                if guess_Y > 0 and shot_map[guess_X, guess_Y - 1] == 0:
                    potential_targets.append((guess_X, guess_Y - 1))
                guess_Y = max_adjacent_points[len(max_adjacent_points) - 1][1]
                if guess_Y < 7 and shot_map[guess_X, guess_Y + 1] == 0:
                    potential_targets.append((guess_X, guess_Y + 1))
            else:
                guess_X = max_adjacent_points[0][0]
                guess_Y = max_adjacent_points[0][1]
                if guess_X > 0 and shot_map[guess_X - 1, guess_Y] == 0:
                    potential_targets.append((guess_X - 1, guess_Y))
                guess_X = max_adjacent_points[len(max_adjacent_points) - 1][0]
                if guess_X < 19 and shot_map[guess_X + 1, guess_Y] == 0:
                    potential_targets.append((guess_X + 1, guess_Y))
        if len(max_adjacent_points) >= 4:
            if isRow:
                guess_X = max_adjacent_points[0][0]
                guess_Y = max_adjacent_points[1][1]
                if guess_X > 0 and shot_map[guess_X - 1, guess_Y] == 0:
                    potential_targets.append((guess_X - 1, guess_Y))
            else:
                guess_X = max_adjacent_points[1][0]
                guess_Y = max_adjacent_points[0][1]
                if guess_Y > 0 and shot_map[guess_X, guess_Y - 1] == 0:
                    potential_targets.append((guess_X, guess_Y - 1))

        return potential_targets

    def notify(self, session_id, data):
        json_object = self.read_file(session_id)

        print(data)

        if data['playerId'] == 'little_tonmoe':

            shot_map = np.array(json_object['shot_map'])
            targets = np.array(json_object['targets'])
            potential_targets = json_object['potential_targets']

            for shot in data['shots']:
                guess_row = shot['coordinate'][0]
                guess_col = shot['coordinate'][1]
                if shot['status'] == "HIT":
                    is_sunk = False
                    sunk_ships = []

                    self.SHOT_MAP[guess_row][guess_col] = 1

                    self.TARGETS, self.POTENTIAL_TARGETS = self.target_hit(guess_row, guess_col, is_sunk, sunk_ships,
                                                                           self.TARGETS, self.POTENTIAL_TARGETS,
                                                                           self.SHOT_MAP)
                elif shot['status'] == "MISS":
                    self.SHOT_MAP[guess_row][guess_col] = 2
                    self.POTENTIAL_TARGETS = self.target_miss(self.TARGETS, self.POTENTIAL_TARGETS, self.SHOT_MAP)

            if len(data['sunkShips']) > 0:
                for ship in data['sunkShips']:
                    sunk_ships.extend(ship['coordinates'])
                    for c in ship['coordinates']:
                        self.SHOT_MAP[c[0]][c[1]] = 2

            json_object['targets'] = self.TARGETS
            json_object['shot_map'] = self.SHOT_MAP.tolist()
            json_object['potential_targets'] = self.POTENTIAL_TARGETS
            self.save_file(session_id, json.dumps(json_object))

    def game_over(self, session_id, data):
        self.save_file(session_id + "_game_over", json.dumps(data))

    # -----------------------------------------------------------------------------------------------------
    def guess_random(self, shot_map):
        while True:
            guess_row, guess_col = self.guest_odd_even(shot_map)
            
            if [guess_row, guess_col] == [0, 0]:
                guess_row, guess_col = random.randint(0, (self.boardHeight - 1)), random.randint(0, (self.boardWidth - 1))

                if shot_map[guess_row, guess_col] == 0:
                        break
            else:
                break

        return guess_row, guess_col

    def guest_odd_even(self, shot_map):
        guess_row, guess_col = 0, 0
        for i in range(0, 10):
            guess_row, guess_col = random.randint(0, (self.boardHeight - 1)), random.randint(0, (self.boardWidth - 1))

            if shot_map[guess_row, guess_col] == 0 and (guess_row + guess_col) % 2 != 0:
                break

        return guess_row, guess_col

    # -----------------------------------------------------------------------------------------------------
    def target_hit(self, target_row, target_col, is_sunk, ship_hit, targets, potential_targets, shot_map):
        if is_sunk:
            potential_targets = []

        targets.append((target_row, target_col))

        potential_targets = [(target_row + 1, target_col), (target_row, target_col + 1),
                             (target_row - 1, target_col), (target_row, target_col - 1)]

        potential_targets = self.calculate_targets(potential_targets, targets, shot_map)

        return targets, potential_targets

    def target_miss(self, targets, potential_targets, shot_map):
        data = []
        potential_targets = []
        for target_row, target_col in targets:
            data = [(target_row + 1, target_col), (target_row, target_col + 1),
                    (target_row - 1, target_col), (target_row, target_col - 1)]
            potential_targets.extend(data)

        potential_targets = self.calculate_targets(potential_targets, targets, shot_map)

        return potential_targets

    def calculate_targets(self, potential_targets, targets, shot_map):
        data = []
        for guess_row, guess_col in potential_targets:
            if (0 <= guess_row < self.boardHeight) and \
                    (0 <= guess_col < self.boardWidth) and \
                    (shot_map[guess_row][guess_col] == 0) and \
                    ((guess_row, guess_col) not in targets):
                data.append((guess_row, guess_col))
        return data

    # -----------------------------------------------------------------------------------------------------
    def hunt_target(self, targets, potential_targets, shot_map):
        potential_targets = self.get_longest_adjacent_points(shot_map)

        if len(potential_targets) == 0:
            potential_targets = self.get_potential_targets(shot_map)
        random.shuffle(potential_targets)
        
        if len(potential_targets) > 0:
            guess_row, guess_col = potential_targets.pop()
            print("Target: " + str([guess_row, guess_col]))
        else:
            guess_row, guess_col = self.guess_random(shot_map)
            print("Hunt: " + str([guess_row, guess_col]))

        return guess_row, guess_col, potential_targets
