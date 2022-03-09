from pygame import Rect
from configparser import ConfigParser

BG_COLOR = '#3a749f'
BUTTON_COLOR_0 = '#052c49'
BUTTON_COLOR_1 = '#04082b'


class Button(Rect):
    def __init__(self, text, nextid, fontsize, x, y, width, height) -> None:
        super().__init__(x, y, width, height)
        self.text = text
        self.nextid = nextid
        self.fontsize = fontsize
        self.focus = False

    def draw(self, surface) -> None:
        # rubo.ttf
        # dpcomic.ttf
        surface.draw.filled_rect(self,
                                 color=BUTTON_COLOR_1 if self.focus else BUTTON_COLOR_0)
        surface.draw.text(self.text,
                          center=self.center,
                          color='white',
                          fontname='rubo.ttf',
                          fontsize=self.fontsize)


class Menu:
    def __init__(self, fontsize, x, y, width, height) -> None:
        self.fontsize = fontsize
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = None
        self.buttons = list()

    def add_button(self, text, nextid) -> None:
        self.buttons.append(
            Button(text, nextid, self.fontsize, self.x, self.y, self.width, self.height))
        self.y += self.height + 25

    def draw(self, surface) -> None:
        for button in self.buttons:
            button.draw(surface)
        if self.title:
            self.draw_title(surface)

    def draw_title(self, surface) -> None:
        surface.draw.text(self.title,
                          center=(500, 250),
                          color='white',
                          fontname='dpcomic.ttf',
                          fontsize=120)

    def focus_check(self, pos) -> None:
        for button in self.buttons:
            button.focus = button.collidepoint(pos)

    def button_selected(self) -> int | None:
        for button in self.buttons:
            if button.focus:
                return button.nextid


class MainMenu(Menu):
    def __init__(self, fontsize, x, y, width, height) -> None:
        super().__init__(fontsize, x, y, width, height)
        self.add_button('Play', 0)
        self.add_button('Options', 2)
        self.add_button('Info', 3)
        self.add_button('Quit', -1)
        self.title = 'PIKA PIKA'

    def draw_title(self, surface) -> None:
        surface.draw.text(self.title,
                          center=(500, 150),
                          color='white',
                          fontname='dpcomic.ttf',
                          fontsize=150)


class OptionsMenu(Menu):
    def __init__(self, fontsize, x, y, width, height) -> None:
        super().__init__(fontsize, x, y, width, height)
        self.add_button('Game Size', 4)
        self.add_button('Volume', 5)
        self.add_button('Back', 1)
        self.title = 'OPTION'
        self.config = ConfigParser()


class InfoMenu(Menu):
    def __init__(self, fontsize, x, y, width, height) -> None:
        super().__init__(fontsize, x, y, width, height)
        self.add_button('Back', 1)
        self.title = 'INFO'

    def draw(self, surface) -> None:
        super().draw(surface)
        surface.draw.text('This is some information about the game and the creator of the game',
                          center=(500, 400),
                          color='white',
                          fontname='dpcomic.ttf',
                          fontsize=30)


class PlayMenu(Menu):
    def __init__(self, fontsize, x, y, width, height) -> None:
        super().__init__(fontsize, x, y, width, height)
        self.add_button('Shuffle', None)
        self.add_button('Change', None)
        self.add_button('Back', 1)
        self.shuffle = False
        self.change = False

    def button_selected(self) -> int | None:
        for button in self.buttons:
            if button.focus:
                if button.text == 'Shuffle':
                    self.shuffle = True
                if button.text == 'Change':
                    self.change = True
                return button.nextid


class GamesizeMenu(Menu):
    def __init__(self, fontsize, x, y, width, height) -> None:
        super().__init__(fontsize, x, y, width, height)
        self.add_button('Small', 1)
        self.add_button('Medium', 1)
        self.add_button('Large', 1)
        self.title = 'GAME SIZE'
        self.config = ConfigParser()

    def button_selected(self) -> int | None:
        for button in self.buttons:
            if button.focus:
                self.config.read('config.ini')
                self.config.set('OPTION', 'MODE', button.text)
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
                return button.nextid


class VolBar(Rect):
    def __init__(self, vol, fontsize, x, y, width, height) -> None:
        super().__init__(x, y, width, height)
        self.vol = vol
        self.fontsize = fontsize

    def draw(self, surface) -> None:
        surface.draw.filled_rect(self, color=BUTTON_COLOR_0)
        surface.draw.filled_rect(Rect(
            self.topleft, (self.width*int(self.vol)/100, self.height)),
            color=BUTTON_COLOR_1)
        surface.draw.text(self.vol,
                          center=self.center,
                          color='white',
                          fontname='rubo.ttf',
                          fontsize=self.fontsize)


class VolMenu(Menu):
    def __init__(self, fontsize, x, y, width, height) -> None:
        super().__init__(fontsize, x, y, width, height)
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.title = 'VOLUME'
        self.vol = self.config.getint('OPTION', 'volume')
        self.mouse_down = False
        self.add_volbar(str(self.vol))
        self.add_button('Save', 2)

    def add_volbar(self, vol) -> None:
        self.buttons.append(
            VolBar(vol, self.fontsize, self.x, self.y, self.width, self.height))
        self.y += self.height + 25

    def change_volume(self, pos) -> None:
        self.vol = round(float((pos[0]-self.x) / self.width * 100))
        self.vol = 0 if self.vol < 0 else 100 if self.vol > 100 else self.vol
        self.config.set('OPTION', 'volume', str(self.vol))
        self.buttons[0].vol = str(self.vol)

    def button_selected(self) -> int | None:
        for button in self.buttons:
            if button.focus:
                if button.text:
                    with open('config.ini', 'w') as configfile:
                        self.config.write(configfile)
                return button.nextid
