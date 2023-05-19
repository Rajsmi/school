from PIL import ImageTk, Image

class Battleship:
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


