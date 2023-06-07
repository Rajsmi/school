from tkinter import Tk, Canvas, Label, Button
from random import randint
from battleship import Battleship
import read_settings as config

SIZE = config.SIZE
COLORS = config.COLORS
FIELD = config.FIELD

class Square:
    def __init__(self, root, x, y):
        self.x = x
        self.y = y
        self.root = root
        self.ship = None # original ship on the square
        self.ship_all_ships = [] # list of all ships on the square
        self.zone_all_ships = [] # list of ships' zones on the square

        self.square = self.root.create_rectangle(x*SIZE, y*SIZE, (x+1)*SIZE, (y+1)*SIZE, fill=COLORS["blank"],
                                              width=1, outline=COLORS["ship"])
        self.root.create_text(x*SIZE+25, y*SIZE+25, text=f'{self.x}, {self.y}', anchor="center", font=5)

    def set_color(self, color):
        self.root.itemconfig(self.square, fill=color)

    def set_ship(self, ship):
        if not self.ship:
            self.ship = ship
            self.ship_all_ships.insert(0, ship)

        else:
            self.ship_all_ships.append(ship)
        return [self.x, self.y]

    def set_zone(self, ship):
        self.zone_all_ships.append(ship)
        return [self.x, self.y]

    def set_restricted(self):
        self.set_color(COLORS["restricted"])

    def check_restricted(self):
        if self.ship and (self.zone_all_ships or len(self.ship_all_ships) > 1):
            return True # True means, square is restricted
        return False

    def set_ship_color(self):
        self.set_color(COLORS["ship"])

    def set_zone_color(self):
        if not self.ship:
            self.set_color(COLORS["zone"])

    def set_blank(self, ship):
        if ship in self.ship_all_ships:
            if ship == self.ship: self.ship = None
            self.ship_all_ships.remove(ship)
            if self.ship_all_ships: self.ship = self.ship_all_ships[0]
        else:
            self.zone_all_ships.remove(ship)


    def set_blank_color(self):
        self.set_color(COLORS["blank"])




class Game():
    def __init__(self, player_ships: list['Battleship']):
        self.player_ships = player_ships

        self.shuffle_button = Button(ships_panel, text='Shuffle', command=lambda: self.shuffle_ships(self.player_ships))
        self.shuffle_button.pack(expand=True)

    def shuffle_ships(self, ships: list):
        Battleship.last_selected = None
        self.shuffle_button.configure(state="disabled")
        for ship in self.player_ships:
            validated = False
            x, y = None, None
            while not validated:
                is_horizontal = bool(randint(0, 1))
                width = ship.width
                height = ship.height
                x, y = randint(0, FIELD-width-1), randint(0, FIELD-height-1)

                ship.set_area(width, height, [x*SIZE, y*SIZE])
                if ship.is_horizontal != is_horizontal:
                    if not ship.rotate('_', animation=False, coords=[x*SIZE, y*SIZE]): continue

                validated = not ship.in_restricted_pos

            ship.x, ship.y = x, y
            ship.move('_')
        self.shuffle_button.configure(state="normal")


window = Tk()
game_field = Canvas(width=FIELD*SIZE+1, height=FIELD*SIZE+1, borderwidth=0, highlightthickness=0)
ships_panel = Canvas(width=(FIELD*SIZE+1)*.5, height=FIELD*SIZE+1, borderwidth=0, highlightthickness=0, bg="lightyellow")
ships_panel.pack(expand=True, side="right")
game_field.pack(expand=True)


# creating two-dimensional field
field = []
for i in range(FIELD):
    field.append([])
    for j in range(FIELD):
        field[i].append(Square(game_field, i, j))


# creating ship models
ships = [
    # Battleship(1, 4, 'ship1.png'),
    Battleship(game_field, 1, 4),

    Battleship(game_field, 1, 3, 'ship2.png'),
    Battleship(game_field, 1, 3, 'ship2.png'),
    Battleship(game_field, 1, 3, 'ship4.png'),

    Battleship(game_field, 1, 2, 'ship3.png'),
    Battleship(game_field, 1, 2, 'ship3.png'),

    Battleship(game_field, 1, 1, 'ship5.png'),
    Battleship(game_field, 1, 1, 'ship5.png'),
    Battleship(game_field, 1, 1, 'ship5.png'),
    Battleship(game_field, 1, 1, 'ship5.png')
]


game = Game(ships)
game.shuffle_ships(game.player_ships)

tags = []
for x in range(FIELD):
    for y in range(FIELD):
        res = game_field.gettags(field[x][y].square)
        if res: tags.append(res)


window.mainloop()

# ship0 - 5*2
# ship1 - 6
# ship2 - 5
# ship3 - 4
# ship4 - 4
# ship5 - 3

