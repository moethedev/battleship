# -*- coding: utf-8 -*-
import os, sys, json, pprint
import numpy as np
import traceback

from flask import Flask
from flask import request

from module.bot import Bot
from module.position import Position

BOARD_WIDTH = 20
BOARD_HEIGHT = 8

APP_PATH = os.getcwd()

app = Flask(__name__)
BOT = None

def read_file(session_id):
    data =[]
    with open("cache/" + session_id + ".json", 'r') as file:
        data = json.load(file)
    return data

def save_file(session_id, data):
    with open("cache/" + session_id + ".json", "w") as outfile:
        outfile.write(data)

# -----------------------------------------------------------------------------------------------------
@app.route("/game-over", methods=["POST"])
def game_over():
    try:
        data = request.json
        session_id = request.headers['X-Session-Id']

        BOT.game_over(session_id, data)
    except Exception as err:
        print(err)
        pass
    
    return { 'success': True }

# -----------------------------------------------------------------------------------------------------
@app.route("/notify", methods=["POST"])
def notify():
    try:
        data = request.json
        session_id = request.headers['X-Session-Id']

        global BOT
        BOT.notify(session_id, data)
    except Exception as err:
        print(err)
        traceback.print_exc()
        pass

    return { 'success': True }

# -----------------------------------------------------------------------------------------------------
@app.route("/shoot", methods=["POST"])
def shoot():
    try:
        data = request.json
        session_id = request.headers['X-Session-Id']

        global BOT
        fire_position = BOT.shoot(session_id, data, data['maxShots'])
    except Exception as err:
        print(err)
        traceback.print_exc()
        pass
    
    return {"coordinates" : fire_position}

# -----------------------------------------------------------------------------------------------------
@app.route("/place-ships", methods=["POST"])
def place_ships():
    session_id = request.headers['X-Session-Id']
    json_object = read_file(session_id)

    pos = Position(json_object['ships'])
    positions = pos.generate()
    pprint.pprint(positions)

    return {"ships": positions}

# -----------------------------------------------------------------------------------------------------
@app.route("/invite", methods=["POST"])
def invite():
    try:
        data = request.json
        session_id = request.headers['X-Session-Id']

        global BOT
        BOT = Bot(BOARD_HEIGHT, BOARD_WIDTH, session_id, data)
    except Exception as err:
        print(err)
        traceback.print_exc()
        pass
    
    return { 'success': True }

@app.route("/")
def index():
    print(request.headers['X-Session-Id'])
    return "Moemoe Tonton"

# -----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        if os.name == 'nt':
            # os.system('cls')
            app.run(debug=True)
            app.run(host="10.10.2.58", port=5000, debug=False, threaded=True)

        else:
            os.system('clear')

            app.run(debug=True)
            app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)
    except Exception as err:
        print(err)
        pass