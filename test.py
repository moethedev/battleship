# -*- coding: utf-8 -*-
import os, sys
import random, pprint, json
import numpy as np
import logging

from module.bot import Bot
from module.map import Map
from module.position import Position

logging.basicConfig(filename="log.txt", level=logging.DEBUG)

inviteRequest =  {
    "boardWidth": 20,
    "boardHeight": 8,
    "ships": [
            {
            "type": "CV",
            "quantity": 1
            },
            {
            "type": "BB",
            "quantity": 2
            },
            {
            "type": "OR",
            "quantity": 3
            },
            {
            "type": "CA",
            "quantity": 2
            },
            {
            "type": "DD",
            "quantity": 1
            }
        ]
    }

map = Map(inviteRequest['boardHeight'], inviteRequest['boardWidth'])

def get_ships(request_ships):
    positions = []
    all_position = []

    for ship in request_ships:
        for i in range(0, ship['quantity']):
            pos = Position()
            position = pos.generate_position(ship['type'], all_position)
            positions.append({'coordinates': position, 'type': ship['type']})
            all_position.extend(position)

    return positions

def play_battleship(mode, positions):
    ship_map = np.zeros([inviteRequest['boardWidth'], inviteRequest['boardHeight']])
    for item in positions:
        for s_pos in item['coordinates']:
            ship_map[s_pos[0], s_pos[1]] = 1

    bot = Bot(inviteRequest['boardHeight'], inviteRequest['boardWidth'])

    hit_rate = 0
    shot_map = np.zeros([inviteRequest['boardWidth'], inviteRequest['boardHeight']])
    simple_shot_map = []
    targets = []
    potential_targets = []

    cnt = 0
    while hit_rate < 100:
        if mode == 'hunt':
            guess_row, guess_col =bot.guess_random(shot_map)
        else:
            guess_row, guess_col, potential_targets = bot.hunt_target(targets, potential_targets, shot_map)

        # if cnt == 0:
        #     guess_row, guess_col = (8, 4)
        # elif cnt == 1:
        #     guess_row, guess_col = (8, 3)
        # elif cnt == 2:
        #     guess_row, guess_col = (8, 2)
        # elif cnt == 3:
        #     guess_row, guess_col = (8, 1)
        # elif cnt == 4:
        #     guess_row, guess_col = (7, 3)

        logging.debug("---------------")
        logging.debug("Shoot: " + str([guess_row, guess_col]))
        
        shot_map[guess_row][guess_col] = 1
        simple_shot_map.append([guess_row, guess_col])
        if ship_map[guess_row, guess_col] == 1:
            logging.debug("Hit")
            is_sunk, ship_hit = map.is_sunk_ship(positions, simple_shot_map, guess_row, guess_col)
            targets, potential_targets = bot.target_hit(guess_row, guess_col, is_sunk, ship_hit, targets, potential_targets, shot_map)

            if is_sunk:
                logging.debug("Sunk")
        elif(len(targets) > 0 and len(potential_targets) == 0):
            logging.debug("Miss")
            potential_targets = bot.target_miss(targets, potential_targets, shot_map)

        logging.debug("Targets: " + str(targets))
        logging.debug("Potential_targets: " + str(potential_targets))

        hit_rate = map.hit_rate(positions, simple_shot_map)
        cnt = cnt + 1

    rate = round(len(simple_shot_map)/(inviteRequest['boardHeight']*inviteRequest['boardWidth']) * 100)
    return rate, simple_shot_map

def simulators(mode, positions, limit):
    lst = []
    result = 0
    for i in range(0, limit):
        rate, simple_shot_map = play_battleship(mode, positions)
        lst.append(simple_shot_map) 
        result = result + rate
    return lst, result

def play():
    pos = Position(inviteRequest['ships'])
    positions = pos.generate()

    limit = 10
    lst, result = simulators('hunt', positions, limit)
    print(" Hunt: " + str(round(result/limit)) + "%")
    lst, result = simulators('target', positions, limit)
    print(" Target: " + str(round(result/limit)) + "%")

    simple_shot_map = []
    map.draw(positions, simple_shot_map)

def demo():
    # positions = [{'coordinates': [[4, 3], [5, 3], [6, 3], [7, 3], [5, 2]], 'type': 'CV'},
    #             {'coordinates': [[8, 1], [8, 2], [8, 3], [8, 4], [7, 2]], 'type': 'CV'}]
    # positions = [{'coordinates': [[8, 7], [8, 6], [8, 5], [8, 4]], 'type': 'BB'},
    # {'coordinates': [[1, 4], [1, 5], [1, 6], [1, 7]], 'type': 'BB'},
    # {'coordinates': [[17, 1], [16, 1], [15, 1]], 'type': 'CA'},
    # {'coordinates': [[6, 6], [5, 6], [4, 6]], 'type': 'CA'}]

    pos = Position(inviteRequest['ships'])
    positions = pos.generate()

    # rate, simple_shot_map = play_battleship('target', positions)

    pprint.pprint(positions)
    simple_shot_map = []
    map.draw(positions, simple_shot_map)

# -----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    os.system('clear')
    os.system('echo "" > log.txt')

    # play()
    demo()

    