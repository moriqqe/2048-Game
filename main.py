from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import BorderImage, Color
from kivy.core.window import Window, Keyboard
from kivy.utils import get_color_from_hex
from kivy.properties import ListProperty, NumericProperty
import random
from kivy.animation import Animation
from kivy.vector import Vector

spacing = 15

# dictionary of movement vectors for each key press
key_vectors = {Keyboard.keycodes['up']: (0, 1), Keyboard.keycodes['right']: (1, 0), Keyboard.keycodes['down']: (0, -1), Keyboard.keycodes['left']: (-1, 0)}

# colors for different tile numbers
colors = ['EEE4DA', 'EDE0C8', 'F2B179', 'F59563', 'F67C5F', 'F65E3B', 'EDCF72', 'EDCC61', 'EDC850', 'EDC53F', 'EDC22E']
tile_colors = {2**i: color for i, color in enumerate(colors, start=1)}

# generate all cells with optional flipping along axes
def all_cells(flip_x=False, flip_y=False):
    for x in (reversed(range(4)) if flip_x else range(4)):
        for y in (reversed(range(4)) if flip_y else range(4)):
            yield (x, y)

class Tile(Widget):
    font_size = NumericProperty(24)
    number = NumericProperty(2)
    color = ListProperty(get_color_from_hex(tile_colors[2]))
    number_color = ListProperty(get_color_from_hex('776E65'))

    def __init__(self, number=2, **kwargs):
        super(Tile, self).__init__(**kwargs)
        self.font_size = 0.5 * self.width  # set font size relative to width
        self.number = number  # set the number for the tile
        self.update_colors()

    def update_colors(self):
        """update tile colors based on its number."""
        self.color = get_color_from_hex(tile_colors[self.number])  # update background color
        if self.number > 4:
            self.number_color = get_color_from_hex('F9F6F2')  # lighter color for higher numbers

    def resize(self, pos, size):
        """resize the tile position and font size according to the board size."""
        self.pos = pos
        self.size = size
        self.font_size = 0.5 * self.width  # adjust font size when resized

class Board(Widget):
    board = None
    moving = False

    def valid_cell(self, x, y):
        """check if the cell is within the valid board range (0 to 3)."""
        return 0 <= x <= 3 and 0 <= y <= 3

    def can_move(self, x, y):
        """check if a tile can move into the cell (empty space)."""
        return self.valid_cell(x, y) and self.board[x][y] is None

    def is_deadlocked(self):
        """check if the game is deadlocked, meaning no more moves can be made."""
        for x, y in all_cells():
            if self.board[x][y] is None:
                return False  # empty cell, game can still proceed
            number = self.board[x][y].number
            if self.can_merge(x + 1, y, number) or self.can_merge(x, y + 1, number):
                return False  # tiles can still merge, game can proceed
        return True  # no more moves, game is deadlocked

    def new_tile(self, *args):
        """add a new tile in a random empty spot on the board."""
        empty_cells = [(x, y) for x, y in all_cells() if self.board[x][y] is None]
        x, y = random.choice(empty_cells)
        tile = Tile(pos=self.cell_pos(x, y), size=self.cell_size)
        self.board[x][y] = tile
        self.add_widget(tile)
        if len(empty_cells) == 1 and self.is_deadlocked():
            print('game over (deadlock)')  # no more moves possible
        self.moving = False

    def reset(self):
        """reset the game board and start with two tiles."""
        self.board = [[None for _ in range(4)] for _ in range(4)]  # empty 4x4 board
        self.new_tile()  # add first tile
        self.new_tile()  # add second tile

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.resize()

    def cell_pos(self, x, y):
        """calculate the position of a cell on the screen."""
        return (self.x + spacing + x * (self.cell_size[0] + spacing), self.y + spacing + y * (self.cell_size[1] + spacing))

    def can_merge(self, x, y, number):
        """check if two tiles with the same number can merge."""
        return self.valid_cell(x, y) and self.board[x][y] and self.board[x][y].number == number

    def move(self, dir_x, dir_y):
        """move the tiles in the given direction (horizontal or vertical)."""
        if self.moving:
            return  # prevent movement while animation is in progress

        # iterate over all cells in the direction of movement
        for x, y in all_cells(dir_x > 0, dir_y > 0):
            tile = self.board[x][y]
            if not tile:
                continue  # skip empty cells
            start_x, start_y = x, y

            # move the tile as far as it can go in the given direction
            while self.can_move(x + dir_x, y + dir_y):
                self.board[x][y] = None
                x += dir_x
                y += dir_y
                self.board[x][y] = tile

            # merge tiles if they have the same number
            if self.can_merge(x + dir_x, y + dir_y, tile.number):
                self.board[x][y] = None
                x += dir_x
                y += dir_y
                self.remove_widget(self.board[x][y])
                self.board[x][y] = tile
                tile.number *= 2  # double the number
                if tile.number == 2048:
                    print('you win the game.')  # check for victory
                tile.update_colors()

            if x == start_x and y == start_y:
                continue  # no move made, skip animation

            # animate the movement of the tile
            anim = Animation(pos=self.cell_pos(x, y), duration=0.25, transition='linear')
            if not self.moving:
                anim.on_complete = self.new_tile
                self.moving = True
            anim.start(tile)

    def resize(self, *args):
        """resize the board and all tiles when window size changes."""
        self.cell_size = (.25 * (self.width - 5 * spacing),) * 2  # each cell size
        self.canvas.before.clear()  # clear previous drawings
        with self.canvas.before:
            BorderImage(pos=self.pos, size=self.size, source='board.png')  # background image
            Color(*get_color_from_hex('ccc0b4'))  # color for grid lines
            # draw each cell border
            for x, y in all_cells():
                BorderImage(pos=self.cell_pos(x, y), size=self.cell_size, source='cell.png')
        if not self.board:
            return

        # resize each tile
        for x, y in all_cells():
            tile = self.board[x][y]
            if tile:
                tile.resize(pos=self.cell_pos(x, y), size=self.cell_size)

    on_pos = resize
    on_size = resize

    def on_key_down(self, window, key, *args):
        """handle keyboard input."""
        if key in key_vectors:
            self.move(*key_vectors[key])  # move tiles in the direction specified by the key

    def on_touch_up(self, touch):
        """handle touch input (swipe gestures)."""
        v = Vector(touch.pos) - Vector(touch.opos)
        if v.length < 20:  # ignore small movements
            return
        if abs(v.x) > abs(v.y):  # horizontal swipe
            v.y = 0
        else:  # vertical swipe
            v.x = 0

        self.move(*v.normalize())  # normalize the swipe and move tiles

class GameApp(App):
    def on_start(self):
        """initialize the game when the app starts."""
        board = self.root.ids.board
        board.reset()  # reset the board
        Window.bind(on_key_down=board.on_key_down)  # bind keyboard input

if __name__ == '__main__':
    Window.clearcolor = get_color_from_hex('faf8ef')  # set background color
    GameApp().run()
