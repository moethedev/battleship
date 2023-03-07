import pprint, sys

class Map:
    def __init__(self, boardWidth, boardHeight):
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight

    # -----------------------------------------------------------------------------------------------------
    def draw(self, ships, shot_map):
        # Initialize the map
        map = [[' . ' for x in range(self.boardHeight)] for y in range(self.boardWidth)]

        total_ship = 0
        for ship in ships:
            total_ship = total_ship + 1
            for pos in ship['coordinates']:
                try:
                    map[pos[1]][pos[0]] = ' x '
                except:
                    print("Place ship issue: " + str(pos))
                    pass
        
        # for pos in shot_map:
        #     try:
        #         map[pos[1]][pos[0]] = ' * '
        #     except:
        #         print("Shot issue: " + str(pos))
        #         pass
        
        hit_rate = self.hit_rate(ships, shot_map)
        total = self.boardWidth * self.boardHeight
        str_hit = " => Total: " + str(hit_rate) + "%" + "\n"
        print(" Battleship hit: " + str(len(shot_map)) + "/" + str(total) + " = " + str(round(len(shot_map)/total * 100)) + "% -- [Ship fleet: " + str(total_ship) +"]")

        # Draw the map
        for i in reversed(range(self.boardWidth)):
            for j in range(self.boardHeight):
                print(map[i][j], end=" ")
            print("\n")

    # -----------------------------------------------------------------------------------------------------
    def hit_rate(self, ships, shot_map):
        coordinates = []
        for ship in ships:
            for pos in ship['coordinates']:
                coordinates.append(pos)

        hit = 0
        for pos in coordinates:
            if pos in shot_map:
                hit = hit + 1

        return round(hit/len(coordinates) * 100)

    # -----------------------------------------------------------------------------------------------------
    def is_sunk_ship(self, ships, shot_map, guess_row, guess_col):
        is_sunk = False

        ship_hit = None
        ship_coordinates = []
        for ship in ships:
            if [guess_row, guess_col] in ship['coordinates']:
                ship_hit = ship
                ship_coordinates = ship['coordinates']
                break

        hit_count = 0
        for pos in ship_coordinates:
            if pos in shot_map:
                hit_count = hit_count + 1

        if hit_count == len(ship['coordinates']):
            is_sunk = True
            # print(is_sunk)
            # print(ship)

        return is_sunk, ship_hit