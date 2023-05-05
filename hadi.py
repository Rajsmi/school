from tkinter import Tk, Canvas
from random import randint
COUNT = 30
SIZE = 600//COUNT
FPS = 20
DRBEKS = 30


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
        # 1 nahoru  2 doprava   3 dolů  4 doleva
        smer = None
        x = self.x
        y = self.y

        # najde všechny drobky ve hře
        drobky = []
        for l in range(COUNT):
            for m in range(COUNT):
                if sit[m][l].cislo == -1: drobky.append([sit[m][l].x, sit[m][l].y])

        # vyhodnotí nejbližší drobek ve hře
        def nejblizsi():
            relativ = []
            for drobek in drobky:
                drobx = drobek[0]
                droby = drobek[1]

                pohyb_x = int
                pohyb_y = int

                dx_in = drobx - self.x
                dx_out = (COUNT - dx_in) * -1

                if abs(dx_in) > abs(dx_out) or abs(dx_out) == abs(dx_in):
                    pohyb_x = dx_out
                else:
                    pohyb_x = dx_in

                dy_in = droby - self.y
                dy_out = (COUNT - dy_in) * -1

                if abs(dy_in) > abs(dy_out) or abs(dy_out) == abs(dy_in):
                    pohyb_y = dy_out
                else:
                    pohyb_y = dy_in

                # připne do pole relativ [[drobek.x, drobek.y], počet pohybů k dropku, relativní pohyb x, r. p. y]
                relativ.append([[drobx, droby], abs(pohyb_x) + abs(pohyb_y), pohyb_x, pohyb_y])

            n_drob = [n for n in relativ if n[1] == min([n[1] for n in relativ])][0]

            return n_drob

        drb = nejblizsi()

        rules = [
            sit[(x - 1) % COUNT][y].cislo in [0, -1],  # volno vlevo
            sit[(x + 1) % COUNT][y].cislo in [0, -1],  # volno vpravo
            sit[x][(y - 1) % COUNT].cislo in [0, -1],  # volno nahoře
            sit[x][(y + 1) % COUNT].cislo in [0, -1],  # volno dole
        ]

        if rules[0] and drb[2] < 0:
            if smer != 2:
                smer = 4
        if rules[1] and drb[2] > 0:
            if smer != 4:
                smer = 2
        if rules[2] and drb[3] < 0:
            if smer != 3:
                smer = 1
        if rules[3] and drb[3] > 0:
            if smer != 1:
                smer = 3

        if smer: return smer

        if rules[0]:
            smer = 4
        if rules[1]:
            smer = 2
        if rules[2]:
            smer = 1
        if rules[3]:
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
    Had(x=5, y=15, smer=2, barva="red", delka = 1,
        clovek = False, nahoru = "w",doprava = "d", dolu = "s", doleva = "a"),
    Had(x=15, y=15, smer=1, barva="blue", delka = 1,
        clovek = False, nahoru = "Up",doprava = "Right", dolu = "Down", doleva = "Left")
]
for i in range(DRBEKS):
    drobek()

okno.after(500, cyklus)
okno.bind("<Key>", klavesa)
okno.mainloop()