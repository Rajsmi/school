from tkinter import Tk, Canvas, Label, Button, font
from random import randint, choice
from PIL import ImageTk, Image
from math import sqrt

SIZE = 50
FIELD = 10
COLORS = {
    "blank": "white",
    "zone": "lightgrey",
    "ship": "grey",
    "restricted": "lightcoral",
    "hit": "red",
    "miss": "lightblue"
}
SHIPS_DATA = [
    (1, 4, 'ship1.png'),
    (1, 3, 'ship2.png'),
    (1, 3, 'ship2.png'),
    (1, 3, 'ship4.png'),
    (1, 2, 'ship3.png'),
    (1, 2, 'ship3.png'),
    (1, 1, 'ship5.png'),
    (1, 1, 'ship5.png'),
    (1, 1, 'ship5.png'),
    (1, 1, 'ship5.png'),
]
SETTINGS_TEXT = 'Nastav si lodě a pak\nklikni na tlačítko Nová hra.\n\nOtočit loď můžeš dvojím kliknutím na loď.\n(Loď se otáčí kolem své přední části.)'

class Square:
    def __init__(self, root: 'Canvas', x: int, y: int):
        self.x = x
        self.y = y
        self.root = root
        self.ship = None # original ship on the square
        self.ship_all_ships = [] # list of all ships on the square
        self.zone_all_ships = [] # list of ships' zones on the square
        self.marked = False

        self.square = self.root.create_rectangle(x*SIZE, y*SIZE, (x+1)*SIZE, (y+1)*SIZE, fill=COLORS["blank"],
                                              width=1, outline=COLORS["ship"])

    def set_marked(self):
        self.marked = True

    def set_color(self, color):
        self.root.itemconfig(self.square, fill=color)

    def set_hit_color(self):
        self.set_color(COLORS["hit"])

    def set_miss_color(self):
        self.set_color(COLORS["miss"])

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

    def set_restricted_color(self):
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

    def set_blank(self, ship: 'Battleship'):
        if ship in self.ship_all_ships:
            if ship == self.ship: self.ship = None
            self.ship_all_ships.remove(ship)
            if self.ship_all_ships: self.ship = self.ship_all_ships[0]
        else:
            self.zone_all_ships.remove(ship)

    def set_blank_color(self):
        self.set_color(COLORS["blank"])



class Battleship:
    last_selected = None
    def __init__(self, root: 'Canvas', field: list, width: int, length: int, image_path: str=None, x=0, y=0, playable=True, disabled=False):

        self.root = root
        self.field = field
        self.x = x # unit format
        self.y = y # unit format
        self.image_path = image_path
        self.rel_grab_coords = () # pixels format
        self.abs_grab_coords = (x, y)
        self.width = width - 1
        self.height = length - 1
        self.is_horizontal = False
        self.in_restricted_pos = False
        self.is_disabled = disabled
        self.sunken = False
        self.ship_coords = [] # coords of squares directly under ship
        self.zone_coords = [] # coords directly in area next to ship
        self.hit_coords = [] # coords of ship that got hit

        self.playable = playable
        self.image = None
        self.image_object = None
        self.rectangle_object = None
        self.watched_object_type = None

        if not Battleship.validate_area(self.x, self.y, self.width, self.height):
            raise ValueError(f'Zadána špatná hodnota pozice nebo šířka/výška lodi.')

        # initializing image
        if self.playable:
            if image_path:
                self.image = Image.open(image_path).resize((int(SIZE * width), int(SIZE * length)))
                self.image_object = self.root.create_image(self.x * SIZE, self.y * SIZE, image=None, anchor="nw")
                self.watched_object()
                self.set_object(self.image)
            else:
                self.rectangle_object = self.root.create_rectangle(self.x*SIZE, self.y*SIZE, (self.x+self.width+1)*SIZE,
                                                                (self.y+self.height+1)*SIZE, fill="grey", width=0)
                self.watched_object()

        # initializing coordinates of image/ship
        self.set_area(self.width, self.height)


        if not self.is_disabled and self.playable:
            watched_object = self.watched_object()
            self.root.tag_bind(watched_object, "<Button-1>", self.select)
            self.root.tag_bind(watched_object, "<B1-Motion>", self.grab)
            self.root.tag_bind(watched_object, "<ButtonRelease-1>", self.move)
            self.root.tag_bind(watched_object, "<Double 1>", self.rotate)


    @classmethod
    def validate_area(cls, x, y, width, height):
        x = x + width # width -1
        y = y + height # height -1
        if x > FIELD - 1 or y > FIELD - 1:
            return False
        return True

    def set_disabled(self):
        watched_object = self.watched_object()
        self.root.tag_unbind(watched_object, "<Button-1>")
        self.root.tag_unbind(watched_object, "<B1-Motion>")
        self.root.tag_unbind(watched_object, "<ButtonRelease-1>")
        self.root.tag_unbind(watched_object, "<Double 1>")

        self.set_area(self.width, self.height)

        self.is_disabled = True


    def watched_object(self):
        if not self.playable: return None

        if self.image_object or self.image_path:
            self.watched_object_type = 'image'
            return self.image_object
        elif self.rectangle_object:
            self.watched_object_type = 'rectangle'
            return self.rectangle_object

    def set_hit(self, coords:list[int, int]):
        self.hit_coords.append(coords)
        self.sunken = len(self.ship_coords) == len(self.hit_coords)

    def set_object(self, object, edit=None):
        if self.watched_object_type == 'image':
            if edit == 'rotate':
                object = object.rotate(-270 if self.is_horizontal else 270, expand=True)
            self.image = object
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.root.itemconfig(self.image_object, image=self.tk_image)
        elif self.watched_object_type == 'rectangle':
            if edit == 'rotate':
                self.object_pos(self.watched_object(), self.x*SIZE, self.y*SIZE, (self.x+self.width+1)*SIZE, (self.y+self.height+1)*SIZE)

    def object_pos(self, object, x=None, y=None, xr=None, yr=None):
        coords = None
        if not self.playable:
            coords = [self.x*SIZE, self.y*SIZE, (self.x+self.width+1)*SIZE, (self.y+self.height+1)*SIZE]
            return coords

        if self.watched_object_type == 'image':
            coords = self.root.coords(object, x, y)
        elif self.watched_object_type == 'rectangle':
            if all([x!=None, y!=None, xr!=None, yr!=None]):
                coords = self.root.coords(object, x, y, xr, yr)
            else:
                coords = self.root.coords(object)

        return coords

    def count_area(self, x: int, y: int, current_x=None, current_y=None):
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

    def set_area(self, width: int, height: int, coords:list[int, int]=None):
        if coords is None: coords = self.object_pos(self.watched_object())

        # coords of image
        tl = [int(coord / SIZE) for coord in coords] # top left
        tr = [tl[0] + width, tl[1]] # top right
        bl = [tl[0], tl[1] + height] # bottom left
        br = [tl[0] + width, tl[1] + height] # bottom right

        if Battleship.last_selected:
            last_selected = Battleship.last_selected
            for box in last_selected.ship_coords + last_selected.zone_coords:
                res = self.field[box[0]][box[1]]
                res.set_blank_color()

        for box in self.ship_coords + self.zone_coords:
            res = self.field[box[0]][box[1]]
            res.set_blank(self)
            res.set_blank_color()

        self.ship_coords = []
        self.zone_coords = []

        # colors, sets rectangles directly under ship
        for xbox in range(tl[0], tr[0] + 1):
            for ybox in range(tl[1], bl[1] + 1):
                res = self.field[xbox][ybox]
                self.ship_coords.append(res.set_ship(self))
                if Battleship.last_selected: res.set_ship_color()

        # colors, sets rectangles directly next to ship
        for xbox in range(tl[0] - 1, tr[0] + 2):
            if xbox < 0 or xbox > FIELD - 1: continue # if box is out of field on x axis
            for ybox in range(tl[1] - 1, bl[1] + 2):
                if ybox < 0 or ybox > FIELD - 1: continue # if box is out of field on y axis
                if [xbox, ybox] in self.ship_coords: continue
                res = self.field[xbox][ybox]
                self.zone_coords.append(res.set_zone(self))
                if Battleship.last_selected: res.set_zone_color()

        # colors, sets zone rectangles in different color, if ship is in restricted position
        for box in self.zone_coords + self.ship_coords:
            if self.field[box[0]][box[1]].check_restricted():
                for coord in self.zone_coords:
                    self.field[coord[0]][coord[1]].set_restricted_color()
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
                self.field[coord[0]][coord[1]].set_restricted_color()
            self.root.after(250, self.set_area, self.width, self.height, coords)
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
            if self.field[box[0]][box[1]].check_restricted():
                self.in_restricted_pos = True
                break

        if self.in_restricted_pos:
            self.in_restricted_pos = False

        if self.playable:
            self.abs_grab_coords = (self.x, self.y)
            self.object_pos(self.watched_object(), self.x * SIZE, self.y * SIZE, (self.x+self.width+1)*SIZE, (self.y+self.height+1)*SIZE)
        self.set_area(self.width, self.height)




class Game():
    def __init__(self, ships_data: list[tuple]):
        self.ships_data = ships_data
        self.player_turn = True
        self.game_ended = False

        self.ships_panel = Canvas(width=(FIELD * SIZE + 1) * .7, borderwidth=0, highlightthickness=0)
        self.player_panel = Canvas(width=FIELD * SIZE + 1, height=FIELD * SIZE + 1, borderwidth=0, highlightthickness=0)
        self.opponent_panel = Canvas(width=FIELD * SIZE + 1, height=FIELD * SIZE + 1, borderwidth=0, highlightthickness=0, relief="raised")
        self.description = self.opponent_panel.create_text((FIELD*SIZE/2, FIELD*SIZE/2), text=SETTINGS_TEXT, justify="center")
        self.start_button = Button(self.ships_panel, height=5, width=12, bg="lightgreen", text='Nová hra', command=self.start_game)
        self.shuffle_button = Button(self.ships_panel, height=3, width=12, bg="lightblue", text='Automatické\nrozmístění', command=lambda: self.shuffle_ships(self.player_ships))
        self.round_triangle = self.ships_panel.create_polygon(0, 0)
        self.player_text = Label(text="Hráč", font=("CROSSOVER", 25), anchor="center")
        self.opponent_text = Label(text="Compjůtr", font=("CROSSOVER", 25), anchor="center")

        self.player_text.grid(column=0, row=0)
        self.player_panel.grid(column=0, row=1, sticky="ew")
        self.ships_panel.grid(column=1, row=1, sticky="ew", padx=10)
        self.opponent_panel.grid(column=2, row=1, sticky="ew")
        self.start_button.grid(column=0,row=0, sticky="ew", pady=5)
        self.shuffle_button.grid(column=0,row=1, sticky="ew", pady=5)

        self.player_field = []
        self.player_ships = []
        self.player_ships_count = 0

        self.opponent_field = []
        self.opponent_ships = []
        self.target_ship = []
        self.opponent_ships_count = 0

        self.create_player_field()

    def shuffle_ships(self, ships: list['Battleship']):
        Battleship.last_selected = None
        self.shuffle_button.configure(state="disabled")
        for ship in ships:
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

    def create_player_field(self):
        self.player_field = [[Square(self.player_panel, i, j) for j in range(FIELD)] for i in range(FIELD)]
        self.player_ships = [Battleship(self.player_panel, self.player_field, ship[0], ship[1], ship[2]) for ship in
                             self.ships_data]
        self.player_ships_count = len(self.player_ships)
        self.shuffle_ships(self.player_ships)


    def create_opponent_field(self):
        self.opponent_field = [[Square(self.opponent_panel, i, j) for j in range(FIELD)] for i in range(FIELD)]
        self.opponent_ships = [Battleship(self.opponent_panel, self.opponent_field, ship[0], ship[1], ship[2], playable=False) for ship in self.ships_data]
        self.opponent_panel.bind("<Button-1>", self.player_move)
        self.shuffle_ships(self.opponent_ships)
        self.opponent_ships_count = len(self.opponent_ships)
        self.opponent_text.grid(column=2, row=0)



    def change_round_triangle(self, side=50):
        self.ships_panel.delete(self.round_triangle)
        color = "blue" if self.player_turn else "red"
        operator = 1 if self.player_turn else -1
        triangle_side = side
        pythagoras = sqrt(triangle_side ** 2 - (triangle_side / 2) ** 2) * operator
        panel_width = self.ships_panel.winfo_width()
        panel_height = self.ships_panel.winfo_height()
        self.round_triangle = self.ships_panel.create_polygon([panel_width / 2 - pythagoras / 2, panel_height / 2 - triangle_side / 2,
                                         panel_width / 2 - pythagoras / 2, panel_height / 2 + triangle_side / 2,
                                         panel_width / 2 + pythagoras / 2, panel_height / 2], fill=color)

    def start_game(self):
        if self.game_ended:
            self.game_ended = False
            self.player_turn = not self.player_turn
            self.shuffle_button.grid()
            self.create_player_field()
            [[self.opponent_panel.delete(self.opponent_field[i][j].square) for j in range(FIELD)] for i in range(FIELD)]

            for widget in self.widgets_for_deletion:
                self.root_for_deletion.delete(widget)

            self.player_text.configure(font=("CROSSOVER", 25))
            self.opponent_text.configure(font=("CROSSOVER", 25))

            self.description = self.opponent_panel.create_text((FIELD * SIZE / 2, FIELD * SIZE / 2), text=SETTINGS_TEXT, justify="center")
        else:
            self.opponent_panel.delete(self.description)
            self.create_opponent_field()
            Battleship.last_selected = None
            for ship in self.player_ships:
                ship.set_disabled()
            if not self.player_turn: self.opponent_move()
            self.start_button.grid_remove()
            self.shuffle_button.grid_remove()
            self.change_round_triangle()
            self.change_header_text()

    def activate_field_outline(self):
        res_rec = self.opponent_panel.create_rectangle(0, 0, FIELD * SIZE, FIELD * SIZE, width=20, outline="red")
        self.opponent_panel.after(300, lambda: self.opponent_panel.delete(res_rec))


    def player_move(self, e):
        x, y = e.x // SIZE, e.y // SIZE
        square = self.opponent_field[x][y]

        if not self.player_turn or square.marked:
            self.activate_field_outline()
            return

        square.set_marked()

        if square.ship:
            square.set_hit_color()
            square.ship.set_hit([x, y])

            if square.ship.sunken:
                for coord in square.ship.zone_coords:
                    self.opponent_field[coord[0]][coord[1]].set_marked()
                    self.opponent_field[coord[0]][coord[1]].set_miss_color()
                self.opponent_ships_count -= 1

        else:
            self.player_turn = False
            square.set_miss_color()

        self.end_turn()

    def opponent_move(self):
        x, y = 0, 0
        if self.target_ship:
            if len(self.target_ship) == 1:
                while True:
                    coords = [self.target_ship[0].x, self.target_ship[0].y]
                    direction = choice([-1, 1])
                    coord_index = randint(0, 1)
                    while coords[coord_index] + direction not in range(FIELD):
                        direction = choice([-1, 1])
                        coord_index = randint(0, 1)
                    coords[coord_index] += direction
                    if not self.player_field[coords[0]][coords[1]].marked:
                        break
                x, y = coords

            if len(self.target_ship) > 1:
                dx = self.target_ship[1].x - self.target_ship[0].x
                dy = self.target_ship[1].y - self.target_ship[0].y
                self.target_ship.sort(key=lambda x: x.x if dx != 0 else x.y)

                coords = []

                if dx != 0:
                    x_options = [self.target_ship[0].x - 1, self.target_ship[-1].x + 1]
                    for x in x_options:
                        if x in range(FIELD):
                            selected_square = self.player_field[x][self.target_ship[0].y]
                            if not selected_square.marked:
                                coords = [selected_square.x, selected_square.y]
                                break
                elif dy != 0:
                    y_options = [self.target_ship[0].y - 1, self.target_ship[-1].y + 1]
                    for y in y_options:
                        if y in range(FIELD):
                            selected_square = self.player_field[self.target_ship[0].x][y]
                            if not selected_square.marked:
                                coords = [selected_square.x, selected_square.y]
                                break

                x, y = coords

        else:
            x, y = randint(0, FIELD-1), randint(0, FIELD-1)
            while self.player_field[x][y].marked:
                x, y = randint(0, FIELD-1), randint(0, FIELD-1)

        square = self.player_field[x][y]
        square.set_marked()

        if square.ship:
            square.set_restricted_color()
            square.ship.set_hit([x, y])

            if square.ship.sunken:
                for coord in square.ship.zone_coords:
                    self.player_field[coord[0]][coord[1]].set_marked()
                    self.player_field[coord[0]][coord[1]].set_zone_color()
                self.target_ship = []
                self.player_ships_count -= 1
            else:
                self.target_ship.append(square)
        else:
            square.set_zone_color()
            self.player_turn = True

        self.end_turn()

    def change_header_text(self):
        if self.player_turn:
            self.player_text.configure(font=("CROSSOVER", 25))
            self.opponent_text.configure(font=("CROSSOVER", 10))
        else:
            self.player_text.configure(font=("CROSSOVER", 10))
            self.opponent_text.configure(font=("CROSSOVER", 25))

    def end_turn(self):
        if self.player_ships_count == 0 or self.opponent_ships_count == 0:
            return self.end_game()

        self.change_round_triangle()
        if not self.player_turn:
            self.player_panel.after(randint(4, 20)*100, self.opponent_move)

        self.change_header_text()

    def show_opponent_field(self):
        for i in range(FIELD):
            for j in range(FIELD):
                square = self.opponent_field[i][j]
                if square.marked and square.ship:
                    square.set_hit_color()
                elif square.marked and not square.ship:
                    square.set_zone_color()
                elif not square.marked and square.ship:
                    square.set_restricted_color()
                else:
                    square.set_ship_color()

    def show_player_field(self):
        for i in range(FIELD):
            for j in range(FIELD):
                square = self.player_field[i][j]
                if square.marked and square.ship:
                    square.set_restricted_color()
                elif not square.marked and square.ship:
                    square.set_ship_color()
                else:
                    square.set_zone_color()

    def end_game(self):
        self.opponent_panel.unbind("<Button-1>")
        self.ships_panel.delete(self.round_triangle)
        root_for_deletion = None
        widgets_for_deletion = []

        if self.player_ships_count == 0: # player loses
            rec = self.player_panel.create_rectangle(0, (FIELD*SIZE)//2-(FIELD*SIZE)//6, FIELD*SIZE, (FIELD*SIZE)//2+(FIELD*SIZE)//6, fill="red3", width=0)
            text = self.player_panel.create_text((FIELD*SIZE)//2, (FIELD*SIZE)//2, text="PROHRÁL JSI", anchor="center", font=("CROSSOVER", 50), fill="white")
            root_for_deletion = self.player_panel
            widgets_for_deletion = [rec, text]

        elif self.opponent_ships_count == 0: # opponent loses
            rec = self.opponent_panel.create_rectangle(0, (FIELD*SIZE)//2-(FIELD*SIZE)//6, FIELD*SIZE, (FIELD*SIZE)//2+(FIELD*SIZE)//6, fill="green4", width=0)
            text = self.opponent_panel.create_text((FIELD*SIZE)//2, (FIELD*SIZE)//2, text="VYHRÁL JSI", anchor="center", font=("CROSSOVER", 50), fill="white")
            root_for_deletion = self.opponent_panel
            widgets_for_deletion = [rec, text]

        self.root_for_deletion = root_for_deletion
        self.widgets_for_deletion = widgets_for_deletion

        self.player_panel.after(1000, self.show_opponent_field)
        self.opponent_panel.after(1000, self.show_player_field)

        self.game_ended = True
        self.ships_panel.after(1500, self.start_button.grid)



window = Tk()
def_font = font.nametofont("TkDefaultFont")
def_font.config(size=12, family='Helvetica', weight='bold')


game = Game(SHIPS_DATA)
# A takhle to dopadá, když si všechno naflákám do tříd..


window.mainloop()



