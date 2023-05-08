from tkinter import Tk, Canvas, Label
from PIL import ImageTk, Image

FIELD = 15 # 15
SIZE = 50 # 50

class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ship = None
        self.in_zone_ships = []

        self.square = canvas.create_rectangle(x*SIZE, y*SIZE, (x+1)*SIZE, (y+1)*SIZE, fill="white",
                                              width=1, dash=(1, 3))
        canvas.create_text(x*SIZE+25, y*SIZE+25, text=f'{self.x}, {self.y}', anchor="center", font=10)

    def set_ship(self, ship):
        if self.ship: return None
        canvas.itemconfig(self.square, fill="black")
        self.ship = ship
        return [self.x, self.y]

    def set_zone(self, ship):
        if not self.ship:
            canvas.itemconfig(self.square, fill="grey")
        self.in_zone_ships.append(ship)
        return [self.x, self.y]

    def set_restricted(self):
        canvas.itemconfig(self.square, fill="red")
        print('restricted')

    def check_restricted(self):
        print(self.ship, self.in_zone_ships)
        if self.ship and self.in_zone_ships:
            print('TRUE')
            return True


    def set_blank(self, ship):
        if self.ship:
            self.ship = None
        else:
            self.in_zone_ships.remove(ship)

        if not self.in_zone_ships:
            canvas.itemconfig(self.square, fill="white")



class Battleship():
    last_selected = None
    def __init__(self, x, y, width, length, image_path):
        self.image = Image.open(image_path).resize((int(SIZE * width), int(SIZE * length)))
        self.image_object = canvas.create_image(x * SIZE, y * SIZE, image=None, anchor="nw")
        self.set_image(self.image)

        self.x = x # unit format
        self.y = y # unit format
        self.rel_grab_coords = () # pixels format
        self.abs_grab_coords = (x, y)
        # self.moves_coords = [(x, y)]
        self.width = width - 1
        self.height = length - 1
        self.is_horizontal = False
        self.ship_coords = [] # coords of squares directly under ship
        self.zone_coords = [] # coords directly in area next to ship

        self.set_area(self.width, self.height)

        canvas.tag_bind(self.image_object, "<B1-Motion>", self.grab)
        canvas.tag_bind(self.image_object, "<ButtonRelease-1>", self.move)
        canvas.tag_bind(self.image_object, "<Button-3>", self.rotate)

    def set_image(self, image):
        self.image = image
        self.tk_image = ImageTk.PhotoImage(self.image)
        canvas.itemconfig(self.image_object, image=self.tk_image)

    def set_area(self, width, height):
        # coords of image
        tl = [int(coord / SIZE) for coord in canvas.coords(self.image_object)]
        tr = [tl[0] + width, tl[1]]
        bl = [tl[0], tl[1] + height]
        br = [tl[0] + width, tl[1] + height]

        for box in self.ship_coords + self.zone_coords:
            field[box[0]][box[1]].set_blank(self)
        self.ship_coords = []
        self.zone_coords = []

        # colors, sets rectangles directly under ship
        for xbox in range(tl[0], tr[0] + 1):
            for ybox in range(tl[1], bl[1] + 1):
                res = field[xbox][ybox].set_ship(self)
                if res: self.ship_coords.append(res)

        # colors, sets rectangles directly next to ship
        for xbox in range(tl[0] - 1, tr[0] + 2):
            if xbox < 0 or xbox > FIELD - 1: continue
            for ybox in range(tl[1] - 1, bl[1] + 2):
                if ybox < 0 or ybox > FIELD - 1: continue
                if [xbox, ybox] in self.ship_coords: continue
                res = field[xbox][ybox].set_zone(self)
                if res: self.zone_coords.append(res)

        for box in self.zone_coords:
            if field[box[0]][box[1]].check_restricted():
                for coord in self.zone_coords:
                    field[coord[0]][coord[1]].set_restricted()
                break

    def count_area(self, x, y, current_x, current_y):
        """Count cursor accessible area depending on given parameters and ship width/height

        :param x: origin cursor x position
        :param y: origin cursor y position
        :param current_x: current cursor x position
        :param current_y: current cursor y position
        :return: tuple(x pos, y pos) | same or borderline coordinates
        """
        # checks if cursor/grabbing is within the field
        field_x = [0, 0]
        field_y = [0, 0]

        for coord in self.ship_coords:
            if coord[0] < x // SIZE: field_x[0] += 1
            if coord[0] > x // SIZE: field_x[1] -= 1
            if coord[1] < y // SIZE: field_y[0] += 1
            if coord[1] > y // SIZE: field_y[1] -= 1

        nx = max(0 + field_x[0], min(current_x // SIZE, FIELD - 1 + field_x[1]))
        ny = max(0 + field_y[0], min(current_y // SIZE, FIELD - 1 + field_y[1]))
        nx, ny = nx * SIZE, ny * SIZE
        return nx, ny

    def rotate(self, e):
        x = e.x//SIZE
        y = e.y//SIZE
        angle = -90 if self.is_horizontal else 90
        self.is_horizontal = not self.is_horizontal
        self.width, self.height = self.height, self.width

        # TODO: Přidat nemožnost rotace v případě rotace u okraje

        rimg = self.image.rotate(angle, expand=True) # center=(x, y)
        self.set_image(rimg)




        self.set_area(self.width, self.height)  # height and width are changed because of different position

    def grab(self, e):
        # if it is first move of new click&move
        if not self.rel_grab_coords:
            nx, ny = self.count_area(e.x, e.y, e.x, e.y)
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

        # change position of image
        canvas.coords(self.image_object, upx*SIZE, upy*SIZE)
        self.set_area(self.width, self.height)


    def move(self, e):
        self.rel_grab_coords = ()
        # canvas.coords(self.image_object, self.x*SIZE, self.y*SIZE)

        # TODO: Uložit finální self.x a self.y




window = Tk()
canvas = Canvas(width=FIELD*SIZE+1, height=FIELD*SIZE+1, borderwidth=0, highlightthickness=0)
canvas.pack(expand=True)

# creating two-dimensional field
field = []
for i in range(FIELD):
    field.append([])
    for j in range(FIELD):
        field[i].append(Square(i, j))


# creating ships models
ship0 = Battleship(1, 10, 2, 5, f'ship0.png')
ship1 = Battleship(0, 0, 1, 6, f'ship1.png')
ship2 = Battleship(5, 0, 1, 5, f'ship2.png')
ship3 = Battleship(7, 0, 1, 4, f'ship3.png')
ship4 = Battleship(14, 2, 1, 4, f'ship4.png')
ship5 = Battleship(10, 10, 1, 3, f'ship5.png')


window.mainloop()

# ship0 - 5*2
# ship1 - 6
# ship2 - 5
# ship3 - 4
# ship4 - 4
# ship5 - 3

