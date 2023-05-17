from tkinter import Tk, Canvas, Label, Button
from PIL import ImageTk, Image
from random import randint

FIELD = 10 # 15
SIZE = 50 # 50

COLORS = {
    "blank": "white",
    "zone": "lightgrey",
    "ship": "grey",
    "restricted": "lightcoral"
}

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


class Battleship():
    last_selected = None
    def __init__(self, width, length, image_path=None, x=0, y=0):

        self.x = x # unit format
        self.y = y # unit format
        self.image_path = image_path
        self.rel_grab_coords = () # pixels format
        self.abs_grab_coords = (x, y)
        self.width = width - 1
        self.height = length - 1
        self.is_horizontal = False
        self.in_restricted_pos = False
        self.is_disabled = False
        self.ship_coords = [] # coords of squares directly under ship
        self.zone_coords = [] # coords directly in area next to ship

        self.image = None
        self.image_object = None
        self.rectangle_object = None
        self.watched_object_type = None

        if not Battleship.validate_area(self.x, self.y, self.width, self.height):
            raise ValueError(f'Zadána špatná hodnota pozice nebo šířka/výška lodi.')

        # initializing image
        if image_path:
            self.image = Image.open(image_path).resize((int(SIZE * width), int(SIZE * length)))
            self.image_object = game_field.create_image(self.x * SIZE, self.y * SIZE, image=None, anchor="nw")
            self.watched_object()
            self.set_object(self.image)
        else:
            self.rectangle_object = game_field.create_rectangle(self.x*SIZE, self.y*SIZE, (self.x+self.width+1)*SIZE,
                                                            (self.y+self.height+1)*SIZE, fill="grey", width=0)
            self.watched_object()

        # initializing coordinates of image/ship
        self.set_area(self.width, self.height)


        if not self.is_disabled:
            watched_object = self.watched_object()
            game_field.tag_bind(watched_object, "<Button-1>", self.select)
            game_field.tag_bind(watched_object, "<B1-Motion>", self.grab)
            game_field.tag_bind(watched_object, "<ButtonRelease-1>", self.move)
            game_field.tag_bind(watched_object, "<Double 1>", self.rotate)


    @classmethod
    def validate_area(cls, x, y, width, height):
        x = x + width # width -1
        y = y + height # height -1
        if x > FIELD - 1 or y > FIELD - 1:
            return False
        return True

    def watched_object(self):
        if self.image_object or self.image_path:
            self.watched_object_type = 'image'
            return self.image_object
        elif self.rectangle_object:
            self.watched_object_type = 'rectangle'
            return self.rectangle_object

    def set_object(self, object, edit=None):
        if self.watched_object_type == 'image':
            if edit == 'rotate':
                object = object.rotate(-270 if self.is_horizontal else 270, expand=True)
            self.image = object
            self.tk_image = ImageTk.PhotoImage(self.image)
            game_field.itemconfig(self.image_object, image=self.tk_image)
        elif self.watched_object_type == 'rectangle':
            if edit == 'rotate':
                self.object_pos(self.watched_object(), self.x*SIZE, self.y*SIZE, (self.x+self.width+1)*SIZE, (self.y+self.height+1)*SIZE)



    def object_pos(self, object, x=None, y=None, xr=None, yr=None):
        coords = None
        if self.watched_object_type == 'image':
            coords = game_field.coords(object, x, y)
        elif self.watched_object_type == 'rectangle':
            if all([x!=None, y!=None, xr!=None, yr!=None]):
                coords = game_field.coords(object, x, y, xr, yr)
            else:
                coords = game_field.coords(object)
        return coords

    def count_area(self, x, y, current_x=None, current_y=None):
        """Count cursor accessible area depending on given parameters and ship width/height

        :param x: origin cursor x position
        :param y: origin cursor y position
        :param current_x: current cursor x position
        :param current_y: current cursor y position
        :return: tuple(x pos, y pos) | same or borderline coordinates
        """
        if current_x is None: current_x = x
        if current_y is None: current_y = y

        # checks if cursor/grabbing is within the field
        field_x = [0, 0]
        field_y = [0, 0]

        x //= SIZE
        y //= SIZE
        current_x //= SIZE
        current_y //= SIZE


        for coord in self.ship_coords:
            if coord[0] < x and coord[1] == y: field_x[0] += 1
            if coord[0] > x and coord[1] == y: field_x[1] -= 1
            if coord[1] < y and coord[0] == x: field_y[0] += 1
            if coord[1] > y and coord[0] == x: field_y[1] -= 1

        nx = max(0 + field_x[0], min(current_x, FIELD - 1 + field_x[1]))
        ny = max(0 + field_y[0], min(current_y, FIELD - 1 + field_y[1]))
        nx, ny = nx * SIZE, ny * SIZE

        return nx, ny

    def set_area(self, width, height, coords:list[int, int]=None):
        if coords is None: coords = self.object_pos(self.watched_object())

        # coords of image
        tl = [int(coord / SIZE) for coord in coords] # top left
        tr = [tl[0] + width, tl[1]] # top right
        bl = [tl[0], tl[1] + height] # bottom left
        br = [tl[0] + width, tl[1] + height] # bottom right

        if Battleship.last_selected:
            last_selected = Battleship.last_selected
            for box in last_selected.ship_coords + last_selected.zone_coords:
                res = field[box[0]][box[1]]
                res.set_blank_color()

        for box in self.ship_coords + self.zone_coords:
            res = field[box[0]][box[1]]
            res.set_blank(self)
            res.set_blank_color()

        self.ship_coords = []
        self.zone_coords = []

        # colors, sets rectangles directly under ship
        for xbox in range(tl[0], tr[0] + 1):
            for ybox in range(tl[1], bl[1] + 1):
                res = field[xbox][ybox]
                self.ship_coords.append(res.set_ship(self))
                if Battleship.last_selected: res.set_ship_color()

        # colors, sets rectangles directly next to ship
        for xbox in range(tl[0] - 1, tr[0] + 2):
            if xbox < 0 or xbox > FIELD - 1: continue # if box is out of field on x axis
            for ybox in range(tl[1] - 1, bl[1] + 2):
                if ybox < 0 or ybox > FIELD - 1: continue # if box is out of field on y axis
                if [xbox, ybox] in self.ship_coords: continue
                res = field[xbox][ybox]
                self.zone_coords.append(res.set_zone(self))
                if Battleship.last_selected: res.set_zone_color()

        # colors, sets zone rectangles in different color, if ship is in restricted position
        for box in self.zone_coords + self.ship_coords:
            if field[box[0]][box[1]].check_restricted():
                for coord in self.zone_coords:
                    field[coord[0]][coord[1]].set_restricted()
                self.in_restricted_pos = True
                break
            self.in_restricted_pos = False


    def select(self, e):
        if not Battleship.last_selected: Battleship.last_selected = self
        self.set_area(self.width, self.height)
        Battleship.last_selected = self

    def rotate(self, e, animation=True, coords:list[int, int]=None):
        if self.rel_grab_coords: return
        if coords is None:
            coords = [x*SIZE for x in self.abs_grab_coords]

        # rotate the ship 90 degrees clockwise or counterclockwise
        if coords[0]//SIZE + self.height + 1 <= FIELD and coords[1]//SIZE + self.width + 1 <= FIELD:
            self.is_horizontal = not self.is_horizontal
            self.width, self.height = self.height, self.width
            self.set_object(self.image, edit="rotate")
            self.set_area(self.width, self.height, coords)

            if self.in_restricted_pos:
                self.is_horizontal = not self.is_horizontal
                self.width, self.height = self.height, self.width
                self.set_object(self.image, edit="rotate")
                self.set_area(self.width, self.height, coords)
            else:
                return True

        if animation:
            for coord in self.zone_coords:
                field[coord[0]][coord[1]].set_restricted()
            game_field.after(250, self.set_area, self.width, self.height, coords)
        else:
            return False

    def grab(self, e):
        # if it is first move of new click&move
        if not self.rel_grab_coords:
            nx, ny = self.count_area(e.x, e.y)
            self.rel_grab_coords = (nx, ny)
            return


        # setting up original (old) relative coords
        x, y = self.rel_grab_coords

        # setting up original (old) absolute coords
        upx, upy = self.abs_grab_coords

        nx, ny = self.count_area(x, y, e.x, e.y)


        # delta x/y - counts shift in pixels
        dx = nx - x
        dy = ny - y

        # if the image was shifted
        if dx != 0 or dy != 0:
            upx = ((upx*SIZE) + dx)//SIZE
            upy = ((upy*SIZE) + dy)//SIZE

            # update last relative coordinates (counted from cursor)
            self.rel_grab_coords = (nx, ny)

            # update last absolute coordinates (counted from "head" of image)
            self.abs_grab_coords = (upx, upy)

        self.object_pos(self.watched_object(), upx*SIZE, upy*SIZE, (upx+self.width+1)*SIZE, (upy+self.height+1)*SIZE)
        self.set_area(self.width, self.height)
        if not self.in_restricted_pos: self.x, self.y = self.abs_grab_coords



    def move(self, e):
        self.rel_grab_coords = ()

        for box in self.zone_coords + self.ship_coords:
            if field[box[0]][box[1]].check_restricted():
                self.in_restricted_pos = True
                break

        if self.in_restricted_pos:
            self.in_restricted_pos = False
            self.abs_grab_coords = (self.x, self.y)
            self.object_pos(self.watched_object(), self.x*SIZE, self.y*SIZE, (self.x+self.width+1)*SIZE, (self.y+self.height+1)*SIZE)
            self.set_area(self.width, self.height)
        else:
            self.abs_grab_coords = (self.x, self.y)
            self.object_pos(self.watched_object(), self.x * SIZE, self.y * SIZE, (self.x+self.width+1)*SIZE, (self.y+self.height+1)*SIZE)
            self.set_area(self.width, self.height)


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
    Battleship(1, 4),

    Battleship(1, 3, 'ship2.png'),
    Battleship(1, 3, 'ship2.png'),
    Battleship(1, 3, 'ship4.png'),

    Battleship(1, 2, 'ship3.png'),
    Battleship(1, 2, 'ship3.png'),

    Battleship(1, 1, 'ship5.png'),
    Battleship(1, 1, 'ship5.png'),
    Battleship(1, 1, 'ship5.png'),
    Battleship(1, 1, 'ship5.png')
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

