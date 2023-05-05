from PIL import ImageTk, Image
from tkinter import Tk, Canvas
BOX_SIZE = 100

class Box:
    def __init__(self, i, j, whiteBackground, whitePiece, blackPiece):
        self.background = canvas.create_rectangle(i*BOX_SIZE, j*BOX_SIZE, (i+1)*BOX_SIZE, (j+1)*BOX_SIZE, fill="white" if whiteBackground else "gray")
        if whitePiece:
            self.image = canvas.create_image((i+0.5)*BOX_SIZE, (j+0.5)*BOX_SIZE, image = whiteImg)
        if blackPiece:
            self.image = canvas.create_image((i+0.5)*BOX_SIZE, (j+0.5)*BOX_SIZE, image = blackImg)

window = Tk()
canvas = Canvas(width=800, height=800)
canvas.pack()
whiteImg = ImageTk.PhotoImage(Image.open("bila.png").resize((BOX_SIZE, BOX_SIZE)))
blackImg = ImageTk.PhotoImage(Image.open("cerna.png").resize((BOX_SIZE, BOX_SIZE)))
window.config(cursor='none')

field = []
for i in range(8):
    field.append([])
    for j in range(8):
        field[i].append(Box(i, j, (i+j)%2, j>4 and not (i+j)%2, j<3 and not (i+j)%2))

shown = False
cursorImg = ImageTk.PhotoImage(Image.open("kurzor.png").rotate(180).resize((30,30)))
activeCursor = ImageTk.PhotoImage(Image.open("klik.png").rotate(180).resize((30,30)))
cursor = canvas.create_image(-100, -100, image = cursorImg, anchor="se")
def motion(e):
    x = e.x
    y = e.y
    canvas.coords(cursor, x, y)

def active(e):
    canvas.itemconfig(cursor, image=activeCursor)

def disabled(e):
    canvas.itemconfig(cursor, image=cursorImg)


window.bind("<Button>", active)
window.bind("<ButtonRelease>", disabled)
window.bind("<Motion>", motion)

window.mainloop()