from enum import Enum
from Menu import *
from BoardGame import *
import pgzrun

# CONST
WIDTH = 1000
HEIGHT = 850
TITLE = 'PIKA PIKA'
ICON = 'game.ico'


class State(Enum):
    MAINMENU = 1
    OPTIONSMENU = 2
    INFOMENU = 3
    GAMESIZEMENU = 4
    VOLMENU = 5
    PLAYING = 0
    QUIT = -1


MENU_S = {State.MAINMENU: {'menu': MainMenu, 'pos': (WIDTH/2-200, HEIGHT/3, 400, 70), 'font': 50},
          State.OPTIONSMENU: {'menu': OptionsMenu, 'pos': (WIDTH/2-150, HEIGHT/2, 300, 50), 'font': 35},
          State.INFOMENU: {'menu': InfoMenu, 'pos': (WIDTH/2-150, 5*HEIGHT/6, 300, 50), 'font': 35},
          State.GAMESIZEMENU: {'menu': GamesizeMenu, 'pos': (WIDTH/2-150, HEIGHT/2, 300, 50), 'font': 35},
          State.VOLMENU: {'menu': VolMenu, 'pos': (WIDTH/2-150, HEIGHT/2, 300, 50), 'font': 35},
          State.PLAYING: {'menu': PlayMenu, 'pos': (HEIGHT+15, 3*HEIGHT/4, 120, 30), 'font': 18}}

MUSIC_S = {'BG': 'yummyflavor', 'GP': 'playwithme'}


class Game(object):
    def __init__(self) -> None:
        self.music = music
        self.clock = clock
        self.keyboard = keyboard
        self.state = None
        self.old_state = None
        self.boardgame = None
        self.config = ConfigParser()
        self.play('BG')
        self.set_volume()
        self.change_state(State.MAINMENU)

    def new_menu(self) -> None:
        self.menu = MENU_S[self.state]['menu'](
            MENU_S[self.state]['font'], *MENU_S[self.state]['pos'])

    def creat_new_game(self) -> None:
        self.config.read('config.ini')
        mode = self.config.get('OPTION', 'MODE')
        table_size = (self.config.getint(mode, 'X'),
                      self.config.getint(mode, 'Y'))
        npkm = self.config.getint(mode, 'npkm')
        time = self.config.getint(mode, 'time')
        print(
            f'Creat game mode: {mode}  table size: {table_size}  number pokemon: {npkm}  time: {time}.')
        self.boardgame = BoardGame(self.clock, table_size, npkm, time, 5, HEIGHT/2 - 25*table_size[0] - 5, HEIGHT/2 - 25 *
                                   table_size[1] - 5, 50*table_size[0] + 10, 50*table_size[1] + 10)
        self.music.play(MUSIC_S['GP'])

    def play(self, key) -> None:
        self.music.play(MUSIC_S[key])

    def set_volume(self) -> None:
        self.config.read('config.ini')
        self.music.set_volume(self.config.getint('OPTION', 'volume')/100)

    def focus_check(self, pos) -> None:
        self.menu.focus_check(pos)

    def change_volume(self, pos) -> None:
        if self.state is State.VOLMENU and self.menu.mouse_down:
            self.menu.change_volume(pos)

    def change_state(self, state) -> None:
        self.old_state = self.state
        self.state = state
        print(f'Current state is {self.state}.')
        if self.state is State.PLAYING:
            self.creat_new_game()
        else:
            self.boardgame = None
        if self.old_state is State.PLAYING:
            self.play('BG')
        self.new_menu()

    def draw(self, surface) -> None:
        surface.fill(BG_COLOR)
        self.menu.draw(surface)

        if self.state is State.PLAYING:
            surface.draw.line(
                (HEIGHT, 0), (HEIGHT, HEIGHT), color=LINE_COLOR)
            self.boardgame.draw(surface)

    def update(self) -> None:
        if self.state is State.QUIT:
            exit()
        if self.state is State.PLAYING:
            if self.menu.shuffle:
                self.boardgame.shufflegrid()
                self.menu.shuffle = False
            if self.menu.change:
                self.boardgame.changegrid()
                self.menu.change = False

    def on_mouse_move(self, pos) -> None:
        self.focus_check(pos)
        self.change_volume(pos)

    def on_mouse_down(self, pos) -> None:
        if self.state is State.VOLMENU:
            self.menu.mouse_down = True
        if self.state is State.PLAYING and self.boardgame.collidepoint(pos):
            self.boardgame.clicked(
                ((pos[1]-self.boardgame.y-5)//50, (pos[0]-self.boardgame.x-5)//50))
        elif self.state is State.PLAYING and self.boardgame.over:
            self.change_state(State.MAINMENU)
        else:
            try:
                self.change_state(State(self.menu.button_selected()))
            except:
                print('You can click again!')

    def on_mouse_up(self) -> None:
        if self.state is State.VOLMENU:
            self.menu.mouse_down = False
        if self.state is State.OPTIONSMENU:
            self.set_volume()

    def on_key_down(self, key) -> None:
        if self.state is State.PLAYING:
            if self.keyboard['LCTRL']:
                self.boardgame.auto(key.name)
            if self.boardgame.over:
                self.change_state(State.MAINMENU)


PIKA_PUZZLE = Game()
# PYGAMEZERO


def draw() -> None:
    PIKA_PUZZLE.draw(screen)


def update() -> None:
    PIKA_PUZZLE.update()


def on_mouse_move(pos) -> None:
    PIKA_PUZZLE.on_mouse_move(pos)


def on_mouse_down(button, pos) -> None:
    if button.name == 'LEFT':
        PIKA_PUZZLE.on_mouse_down(pos)


def on_mouse_up() -> None:
    PIKA_PUZZLE.on_mouse_up()


def on_key_down(key) -> None:
    PIKA_PUZZLE.on_key_down(key)


pgzrun.go()
