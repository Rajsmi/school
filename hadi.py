from tkinter import Tk, Canvas
from random import randint
COUNT = 30
SIZE = 600//COUNT
FPS = 5
DRBEKS = 1

class Ctverec:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vzhled = platno.create_rectangle(x*SIZE,y*SIZE, (x+1)*SIZE, (y+1)*SIZE, fill="white")
        self.cislo = 0

class Had:
    def __init__(self, x:int, y:int, smer:int, barva:str, delka:int,
                 clovek:bool, nahoru=None, doprava = None, dolu = None, doleva = None):
        self.x = x
        self.y = y
        self.smer = smer
        self.barva = barva
        self.delka = delka
        self.clovek = clovek
        self.nahoru = nahoru
        self.doprava = doprava
        self.dolu = dolu
        self.doleva = doleva
        sit[x][y].cislo = delka
        platno.itemconfig(sit[x][y].vzhled, fill = barva)
    def logika(self):
        smer = 1
        x = self.x
        y = self.y

        if sit[(x-1)%COUNT][y].cislo == 0:
            smer = 4
        if sit[(x + 1)%COUNT][y].cislo == 0:
            smer = 2
        if sit[x][(y - 1)%COUNT].cislo == 0:
            smer = 1
        if sit[x][(y + 1)%COUNT].cislo == 0:
            smer = 3

        return smer


def cyklus():
    #hni hady
    for had in hadi:
        if not had.clovek:
            had.smer = had.logika()

        if had.smer == 1:
            had.y -= 1
        if had.smer == 2:
            had.x += 1
        if had.smer == 3:
            had.y += 1
        if had.smer == 4:
            had.x -= 1
        had.x %= COUNT
        had.y %= COUNT
        if sit[had.x][had.y].cislo>0:
            hadi.remove(had)
            continue
        if sit[had.x][had.y].cislo == -1:
            had.delka += 1
            drobek()
        sit[had.x][had.y].cislo = had.delka + 1
        platno.itemconfig(sit[had.x][had.y].vzhled, fill=had.barva)

    #sniz cisla
    for i in range(COUNT):
        for j in range(COUNT):
            if sit[i][j].cislo > 0:
                sit[i][j].cislo -= 1
                if sit[i][j].cislo == 0:
                    platno.itemconfig(sit[i][j].vzhled, fill="white")
    okno.after(1000//FPS, cyklus)

def klavesa(e):
    k = e.keysym
    for had in hadi:
        if k == had.nahoru:
            had.smer = 1
        if k == had.doprava:
            had.smer = 2
        if k == had.dolu:
            had.smer = 3
        if k == had.doleva:
            had.smer = 4
def drobek():
    x = randint(0, COUNT - 1)
    y = randint(0, COUNT - 1)
    while sit[x][y].cislo!=0:
        x = randint(0, COUNT - 1)
        y = randint(0, COUNT - 1)
    sit[x][y].cislo = -1
    platno.itemconfig(sit[x][y].vzhled, fill = "#CC0")

okno = Tk()
platno = Canvas(width=600, height=600, bg="white")
platno.pack()

sit = []
for i in range(COUNT):
    sit.append([])
    for j in range(COUNT):
        sit[i].append(Ctverec(i,j))

hadi = [
    Had(x=5, y=15, smer=2, barva="red", delka = 4,
        clovek = True, nahoru = "w",doprava = "d", dolu = "s", doleva = "a"),
    Had(x=15, y=15, smer=1, barva="blue", delka = 10,
        clovek = True, nahoru = "Up",doprava = "Right", dolu = "Down", doleva = "Left")
]
for i in range(DRBEKS):
    drobek()

okno.after(500, cyklus)
okno.bind("<Key>", klavesa)
okno.mainloop()