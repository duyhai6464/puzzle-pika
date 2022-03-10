from configparser import ConfigParser
from pygame import Rect
import numpy as np

LINE_COLOR = '#6edcdc'


class BoardGame(Rect):
    def __init__(self, clock, table_size, npkm, time, heart, x, y, width, height) -> None:
        super().__init__(x, y, width, height)
        self.clock = clock
        self.table_size = table_size
        self.npkm = npkm
        self.maxtime = time
        self.maxheart = heart
        self.score = 0
        self.level = 1
        self.over = False
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.generate()
        self.clock.schedule_interval(self.timer, 0.97)

    def generate(self) -> None:
        self.grid = np.append(np.random.randint(low=self.npkm, size=int(
            self.table_size[0]*self.table_size[1]/2 - self.npkm)), np.arange(self.npkm))
        self.grid = self.grid.repeat(2)
        np.random.shuffle(self.grid)
        self.grid = self.grid.reshape((self.table_size[1], -1))
        print(f'Board game:\n{self.grid}')
        self.dict = np.arange(1, 56)
        np.random.shuffle(self.dict)
        self.mark = list()
        self.time = self.maxtime
        self.heart = self.maxheart
        self.randmode()
        self.getrank()

    def clicked(self, rc) -> None:
        if not self.over and len(self.mark) < 2 and self.grid[rc] >= 0:
            print(f'Clicked: {rc}')
            if rc in self.mark:
                self.mark.remove(rc)
            else:
                self.mark.append(rc)
                if len(self.mark) == 2:
                    self.clock.schedule_unique(self.checkconnect, 0.15)

    def checkconnect(self) -> None:
        if len(self.mark) == 2:
            if self.canconnect(self.mark[0], self.mark[1]):
                print('Correct!')
                for rc in self.mark:
                    self.grid[rc] = -1
                self.score += 1
                self.updategrid()
                self.checkgameover()
            self.mark.clear()

    def canconnect(self, p1, p2) -> bool:
        if self.grid[p1[0], p1[1]] != self.grid[p2[0], p2[1]]:
            return False
        return True if p2 in self.findpath(p1) else False

    def findpath(self, p) -> list[tuple]:
        res = list()
        Q = list()
        d = np.array([[0, 0, -1, 1], [-1, 1, 0, 0]])
        Adj = np.full((self.table_size[1]+2, self.table_size[0]+2), 4)
        Adj[p[0]+1, p[1]+1] = 0
        Q.append((p[0]+1, p[1]+1))
        while len(Q):
            posX, posY = Q.pop(0)
            for i in range(4):
                px, py = posX + d[0, i], posY+d[1, i]
                while self.available(px, py) >= 0 and Adj[px, py] > Adj[posX, posY] + 1:
                    Adj[px, py] = Adj[posX, posY] + 1
                    if self.available(px, py) > 0:
                        Q.append((px, py))
                    else:
                        if self.grid[px-1, py-1] == self.grid[p]:
                            res.append((px-1, py-1))
                        break
                    px += d[0, i]
                    py += d[1, i]
        # print(f'The possibilities for point {p} are {res}')
        return res

    def available(self, Xpos, Ypos) -> int:
        if 1 <= Xpos <= self.table_size[1] and 1 <= Ypos <= self.table_size[0]:
            return 0 if self.grid[Xpos-1, Ypos-1] >= 0 else 1
        if 0 <= Xpos <= self.table_size[1] + 1 and 0 <= Ypos <= self.table_size[0] + 1:
            return 1
        return -1

    def shufflegrid(self) -> None:
        if not self.heart:
            print('You don\'t have enough heart!')
            return
        self.heart -= 1
        print(f'shuffle successfully! Your hearts are down to {self.heart}.')
        mask = np.fromfunction(
            lambda i, j: self.grid[i, j] >= 0, (self.table_size[1], self.table_size[0]), dtype=int)
        temp = self.grid[mask]
        np.random.shuffle(temp)
        self.grid[mask] = temp

    def changegrid(self) -> None:
        print('Change images successfully!')
        np.random.shuffle(self.dict)

    def allempty(self) -> bool:
        return np.sum(self.grid) == -self.table_size[0]*self.table_size[1]

    def allimpossible(self) -> tuple:
        for Ro in np.random.choice(self.table_size[1], self.table_size[1], replace=False):
            for Co in np.random.choice(self.table_size[0], self.table_size[0], replace=False):
                if self.grid[Ro, Co] >= 0:
                    pathfromrc = self.findpath((Ro, Co))
                    if len(pathfromrc) > 0:
                        Ri, Ci = pathfromrc[np.random.choice(len(pathfromrc))]
                        # print(Ro, Co, Ri, Ci)
                        return False, Ro, Co, Ri, Ci
        return True, -1, -1, -1, -1

    def timer(self) -> None:
        if self.time > 0:
            self.time -= 1
        else:
            self.gameover()
            self.time = 9999

    def checkgameover(self) -> None:
        if self.allempty():
            self.levelup()
        if self.allimpossible()[0]:
            if self.heart == 0:
                self.gameover()
            print('There are no available moves! :((')
            self.shufflegrid()

    def gameover(self) -> None:
        print('Game over')
        self.over = True
        self.ranks.append(self.score)
        self.ranks = sorted(self.ranks, reverse=True)[:5]
        self.config.set(self.mode, 'score', str(self.ranks)[1:-1])
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def levelup(self) -> None:
        self.level += 1
        self.score += self.time*100//self.maxtime
        self.heart = min(self.maxheart, self.heart+1)
        self.generate()
        print(f'level up to {self.level}')

    def auto(self, k) -> None:
        if k == 'A':
            print('Auto click activated!')
            self.clock.schedule_interval(self.autoclick, 0.25)
        if k == 'Z':
            print('Auto click disabled!')
            self.clock.unschedule(self.autoclick)
        if k == 'S':
            print(f'Suggest move: {self.allimpossible()[1:]}')

    def autoclick(self) -> None:
        impossible, ro, co, ri, ci = self.allimpossible()
        if not impossible:
            self.clicked((ro, co))
            self.clicked((ri, ci))

    def randmode(self) -> None:
        self.modegame = np.random.random_integers(10)

    def updategrid(self) -> None:
        if self.modegame == 1:
            for i in range(self.table_size[1]):
                self.grid[i, :] = sorted(
                    self.grid[i, :], key=lambda v: v == -1)
        if self.modegame == 2:
            for i in range(self.table_size[1]):
                self.grid[i, :] = sorted(
                    self.grid[i, :], key=lambda v: v != -1)
        if self.modegame == 3:
            for i in range(self.table_size[0]):
                self.grid[:, i] = sorted(
                    self.grid[:, i], key=lambda v: v == -1)
        if self.modegame == 4:
            for i in range(self.table_size[0]):
                self.grid[:, i] = sorted(
                    self.grid[:, i], key=lambda v: v != -1)
        if self.modegame == 5:
            for i in range(self.table_size[1]):
                if i < self.table_size[1]//2:
                    self.grid[i, :] = sorted(
                        self.grid[i, :], key=lambda v: v == -1)
                else:
                    self.grid[i, :] = sorted(
                        self.grid[i, :], key=lambda v: v != -1)
        if self.modegame == 6:
            for i in range(self.table_size[1]):
                if i < self.table_size[1]//2:
                    self.grid[i, :] = sorted(
                        self.grid[i, :], key=lambda v: v != -1)
                else:
                    self.grid[i, :] = sorted(
                        self.grid[i, :], key=lambda v: v == -1)
        if self.modegame == 7:
            for i in range(self.table_size[1]):
                self.grid[i, :self.table_size[0]//2] = sorted(
                    self.grid[i, :self.table_size[0]//2], key=lambda v: v == -1)
                self.grid[i, self.table_size[0]//2:] = sorted(
                    self.grid[i, self.table_size[0]//2:], key=lambda v: v != -1)
        if self.modegame == 8:
            for i in range(self.table_size[1]):
                self.grid[i, :self.table_size[0]//2] = sorted(
                    self.grid[i, :self.table_size[0]//2], key=lambda v: v != -1)
                self.grid[i, self.table_size[0]//2:] = sorted(
                    self.grid[i, self.table_size[0]//2:], key=lambda v: v == -1)

    def getrank(self) -> None:
        self.mode = self.config.get('OPTION', 'mode')
        self.ranks = list(
            map(int, self.config.get(self.mode, 'score').split(', ')))
        print(f'Old ranks {self.mode}:\n{self.ranks}')

    def draw(self, surface) -> None:
        surface.draw.rect(self, color=LINE_COLOR)
        for Ro in range(self.table_size[1]):
            for Co in range(self.table_size[0]):
                if (Ro, Co) in self.mark:
                    surface.draw.rect(Rect((Co*50+5+self.x, Ro*50+5+self.y), (50, 50)),
                                      color=LINE_COLOR)
                if self.grid[Ro, Co] >= 0:
                    surface.blit(f'f{self.dict[self.grid[Ro, Co]]}.png',
                                 (Co*50+10+self.x, Ro*50+10+self.y))
        if self.over:
            surface.draw.text('GAME OVER',
                              center=self.center,
                              color='white',
                              fontname='rubo.ttf',
                              fontsize=75)
        top, left = 870, 75
        surface.draw.text(f'GAME SIZE:\n{self.mode}',
                          topleft=(top, left),
                          color='white',
                          fontname='dpcomic.ttf',
                          fontsize=25)
        surface.draw.text(f'LEVEL:\n{self.level}',
                          topleft=(top, left+90),
                          color='white',
                          fontname='dpcomic.ttf',
                          fontsize=25)
        surface.draw.text(f'SCORE:\n{self.score}',
                          topleft=(top, left+180),
                          color='white',
                          fontname='dpcomic.ttf',
                          fontsize=25)
        surface.draw.text(f'TIME:\n{self.time}',
                          topleft=(top, left+270),
                          color='white',
                          fontname='dpcomic.ttf',
                          fontsize=25)
        surface.draw.text(f'RANK:\n1. {self.ranks[0]}\n2. {self.ranks[1]}\n3. {self.ranks[2]}\n4. {self.ranks[3]}\n5. {self.ranks[4]}',
                          topleft=(top, left+360),
                          color='white',
                          fontname='dpcomic.ttf',
                          fontsize=25)
        surface.draw.text(f'{"O"*self.heart}',
                          topleft=(top, left+520),
                          color='red',
                          fontname='dpcomic.ttf',
                          fontsize=40)
