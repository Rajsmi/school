from tkinter import Tk, Canvas, Label
from PIL import ImageTk, Image

FIELD = 15
SIZE = 50

class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ship = None

        self.square = canvas.create_rectangle(x*SIZE, y*SIZE, (x+1)*SIZE, (y+1)*SIZE, fill="white",
                                              width=1, dash=(1, 3))
        canvas.create_text(x*SIZE+25, y*SIZE+25, text=f'{self.x}, {self.y}', anchor="center", font=10)

    def set_ship(self, ship):
        canvas.itemconfig(self.square, fill="black")
        self.ship = ship
        return [self.x, self.y]

    def zone_color(self):
        canvas.itemconfig(self.square, fill="grey")

    def empty_color(self):
        canvas.itemconfig(self.square, fill="white")



class Battleship():
    last_selected = None
    def __init__(self, x, y, width, length, image_path):
        self.image = Image.open(image_path).resize((int(SIZE * width), int(SIZE * length)))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.image_object = canvas.create_image(x * SIZE, y * SIZE, image=self.tk_image, anchor="nw")

        self.x = x # unit format
        self.y = y # unit format
        self.last_coords = () # pixels format
        self.width = width - 1
        self.height = length - 1
        self.coords = []

        # coords of image
        tl = [int(coord / SIZE) for coord in canvas.coords(self.image_object)]
        tr = [tl[0] + self.width, tl[1]]
        bl = [tl[0], tl[1] + self.height]
        br = [tl[0] + self.width, tl[1] + self.height]

        # colors rectangles directly under ship
        for xbox in range(tl[0], tr[0]+1):
            for ybox in range(tl[1], bl[1]+1):
                res = field[xbox][ybox].set_ship(self)
                self.coords.append(res)

        # colors rectangles directly next to ship
        for xbox in range(tl[0]-1, tr[0]+2):
            if xbox < 0 or xbox > FIELD-1: continue
            for ybox in range(tl[1]-1, bl[1] + 2):
                if ybox < 0 or ybox > FIELD-1: continue
                if [xbox, ybox] in self.coords: continue
                field[xbox][ybox].zone_color()

        canvas.tag_bind(self.image_object, "<B1-Motion>", self.grab)
        canvas.tag_bind(self.image_object, "<ButtonRelease-1>", self.move)
        canvas.tag_bind(self.image_object, "<Button-1>", self.rotate)


    def grab(self, e):
        # checks if cursor/grabing is within the field
        nx = max(0, min(e.x//SIZE, FIELD - 1))
        ny = max(0, min(e.y//SIZE, FIELD - 1))
        nx, ny = nx*SIZE, ny*SIZE

        # if it is first move of new click&move
        if not self.last_coords:
            self.last_coords = (nx, ny)
            return

        x = self.last_coords[0]
        y = self.last_coords[1]

        # delta x/y - counts shift in pixels
        dx = nx - x
        dy = ny - y

        # if the image was shifted
        if dx != 0 or dy != 0:
            self.x = ((self.x*SIZE) + dx)//SIZE
            self.y = ((self.y*SIZE) + dy)//SIZE
            self.last_coords = (nx, ny) # updates last coordinates

        # change position of image
        canvas.coords(self.image_object, self.x*SIZE, self.y*SIZE)

    def move(self, e):
        self.last_coords = ()

    def rotate(self, e):
        rimg = self.image.rotate(5)
        tk_rimg = ImageTk.PhotoImage(rimg)
        canvas.itemconfig(self.image_object, image=tk_rimg)

window = Tk()
canvas = Canvas(width=FIELD*SIZE+1, height=FIELD*SIZE+1, borderwidth=0, highlightthickness=0)
canvas.pack(expand=True)


field = []
for i in range(FIELD):
    field.append([])
    for j in range(FIELD):
        field[i].append(Square(i, j))


ship0 = Battleship(1, 10, 2, 5, f'ship0.png')
ship1 = Battleship(0, 0, 1, 6, f'ship1.png')
ship2 = Battleship(5, 0, 1, 5, f'ship2.png')
ship3 = Battleship(7, 0, 1, 4, f'ship3.png')
ship4 = Battleship(14, 2, 1, 4, f'ship4.png')
ship5 = Battleship(12, 10, 1, 3, f'ship5.png')


window.mainloop()

# ship0 - 5*2
# ship1 - 6
# ship2 - 5
# ship3 - 4
# ship4 - 4
# ship5 - 3

