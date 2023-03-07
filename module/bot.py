import random
import json
import numpy as np
import os
import logging

logging.basicConfig(filename="log.txt", level=logging.DEBUG)

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
            logging.debug("TARGETS: " + str(self.TARGETS))
            logging.debug("POTENTIAL_TARGETS: " + str(self.POTENTIAL_TARGETS))
            # logging.debug("SHOT_MAP: " + str(self.SHOT_MAP))
            logging.debug("SIMPLE_SHOT_MAP: " + str(self.SIMPLE_SHOT_MAP))

            guess_row, guess_col, self.POTENTIAL_TARGETS = self.hunt_target(self.TARGETS, self.POTENTIAL_TARGETS,
                                                                            self.SHOT_MAP)
            fire_position.append([guess_row, guess_col])

            self.SHOT_MAP[guess_row][guess_col] = 2
            self.SIMPLE_SHOT_MAP.append([guess_row, guess_col])

        return fire_position

    def getPotential_targets(self, shot_map):
        potential_targets = []
        for j in range(self.boardWidth):
            for i in range(self.boardHeight):
                if shot_map[i][j] == 1:
                    if i > 0 and shot_map[i - 1][j] == 0:
                        potential_targets.append((i - 1, j))
                    if i < self.boardHeight - 1 and shot_map[i + 1][j] == 0:
                        potential_targets.append((i + 1, j))
                    if j > 0 and shot_map[i][j - 1] == 0:
                        potential_targets.append((i, j - 1))
                    if j < self.boardWidth - 1 and shot_map[i][j + 1] == 0:
                        potential_targets.append((i, j + 1))
        return potential_targets

    def notify(self, session_id, data):
        json_object = self.read_file(session_id)

        logging.debug("notify: " + str(data))

        # if data['playerId'] == 'Double-L-tmp':
        shot_map = np.array(json_object['shot_map'])
        targets = np.array(json_object['targets'])
        potential_targets = json_object['potential_targets']

        if data['shots'][0]['status'] == "HIT":
            is_sunk = False
            sunk_ships = []
            guess_row = data['shots'][0]['coordinate'][0]
            guess_col = data['shots'][0]['coordinate'][1]

            self.SHOT_MAP[guess_row][guess_col] = 1

            if len(data['sunkShips']) > 0:
                is_sunk = True
                for ship in data['sunkShips']:
                    sunk_ships.extend(ship['coordinates'])
                    for c in ship['coordinates']:
                        self.SHOT_MAP[c[0]][c[1]] = 2

            self.TARGETS, self.POTENTIAL_TARGETS = self.target_hit(guess_row, guess_col, is_sunk, sunk_ships,
                                                                    self.TARGETS, self.POTENTIAL_TARGETS,
                                                                    self.SHOT_MAP)
        elif data['shots'][0]['status'] == "MISS":
            self.POTENTIAL_TARGETS = self.target_miss(self.TARGETS, self.POTENTIAL_TARGETS, self.SHOT_MAP)

        json_object['targets'] = self.TARGETS
        json_object['shot_map'] = self.SHOT_MAP.tolist()
        json_object['potential_targets'] = self.POTENTIAL_TARGETS
        self.save_file(session_id, json.dumps(json_object))
            

    def game_over(self, session_id, data):
        self.save_file(session_id + "_game_over", json.dumps(data))

    # -----------------------------------------------------------------------------------------------------
    def guess_random(self, shot_map):
        while True:
            guess_row, guess_col = random.randint(0, (self.boardHeight - 1)), random.randint(0, (self.boardWidth - 1))

            if shot_map[guess_row, guess_col] == 0 and (guess_row + guess_col) % 2 == 0:
                break

        return guess_row, guess_col

    # -----------------------------------------------------------------------------------------------------
    def target_hit(self, target_row, target_col, is_sunk, ship_hit, targets, potential_targets, shot_map):
        if is_sunk:
            potential_targets = []

        targets.append((target_row, target_col))

        potential_targets = [(target_row + 1, target_col), (target_row, target_col + 1),
                             (target_row - 1, target_col), (target_row, target_col - 1)]

        # if len(targets) > 1:
        #     potential_targets = self.guest_target(targets, shot_map)

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
        # if targets and len(potential_targets) > 0:
        potential_targets = self.getPotential_targets(shot_map)
        if len(potential_targets) > 0:
            guess_row, guess_col = potential_targets.pop()
            print("Target: " + str([guess_row, guess_col]))
            logging.debug("Target: " + str([guess_row, guess_col]))
        else:
            guess_row, guess_col = self.guess_random(shot_map)
            print("Hunt: " + str([guess_row, guess_col]))
            logging.debug("Hunt: " + str([guess_row, guess_col]))

        return guess_row, guess_col, potential_targets