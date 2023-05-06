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
        image = Image.open(image_path).resize((int(SIZE * width), int(SIZE * length)))
        self.image = ImageTk.PhotoImage(image)
        self.image_object = canvas.create_image(x * SIZE, y * SIZE, image=self.image, anchor="nw")

        self.x = x
        self.y = y
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

        print(self.coords)

        for xbox in range(tl[0]-1, tr[0]+2):
            if xbox < 0 or xbox > FIELD-1: continue
            for ybox in range(tl[1]-1, bl[1] + 2):
                if ybox < 0 or ybox > FIELD-1: continue
                if [xbox, ybox] in self.coords: continue
                field[xbox][ybox].zone_color()

    def move(self, nx, ny):
        nx = nx * SIZE
        ny = ny * SIZE
        print(nx, ny)
        canvas.coords(self.image_object, nx, ny)

window = Tk()
canvas = Canvas(width=FIELD*SIZE+1, height=FIELD*SIZE+1, borderwidth=0, highlightthickness=0)
canvas.pack(expand=True)


field = []
for i in range(FIELD):
    field.append([])
    for j in range(FIELD):
        field[i].append(Square(i, j))


ship0 = Battleship(1, 10, 2, 5, f'ship0.png')
ship1 = Battleship(3, 0, 1, 6, f'ship1.png')
ship2 = Battleship(5, 0, 1, 5, f'ship2.png')
ship3 = Battleship(7, 0, 1, 4, f'ship3.png')
ship4 = Battleship(14, 2, 1, 4, f'ship4.png')
ship5 = Battleship(12, 10, 1, 3, f'ship5.png')

def drag(e):
    x = e.x // SIZE
    y = e.y // SIZE

    x = max(0, min(x, FIELD - 1))
    y = max(0, min(y, FIELD - 1))


    ship = field[x][y].ship
    if ship:
        ship.move(x, y)

window.bind("<B1-Motion>", drag)

window.mainloop()

# ship0 - 5*2
# ship1 - 6
# ship2 - 5
# ship3 - 4
# ship4 - 4
# ship5 - 3

