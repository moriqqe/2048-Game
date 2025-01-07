from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import BorderImage
from kivy.core.window import Window
from kivy.utils import get_color_from_hex


class Board(Widget):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.resize()
    
    def resize(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            BorderImage(pos=self.pos, size= self.size, source='board.png')
    
    on_pos = resize
    on_size = resize

class GameApp(App):
    def on_start(self):
        board = self.root.ids.board
        board.resize()

if __name__ == '__main__':
    Window.clearcolor = get_color_from_hex('faf8ef')
    GameApp().run()