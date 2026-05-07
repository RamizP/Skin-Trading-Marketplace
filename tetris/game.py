

from abc import ABC, abstractmethod
import copy
import random

class Playground:

    def __init__(self, length, height):
        self.playground: list[list[int]] = []
        self.playground_to_draw: list[list[int]] = []
        self.length: int = length
        self.height: int = height

    def create(self):
        for i in range(self.height):
            self.playground.append([])
            for e in range(self.length):
                self.playground[i].append(0)
        self.playground_to_draw = copy.deepcopy(self.playground)
        return self.playground

    def color_digit(self, digit, color):
        COLORS = {
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "orange": "\033[38;5;208m",
            "purple": "\033[38;5;129m",
            "cyan": "\033[36m",
            "reset": "\033[0m"
        }
        color_code = COLORS.get(color, COLORS["reset"])
        return f"{color_code}{digit}{COLORS['reset']}"

    def render_block(self, block):
        posX = block.posX
        posY = block.posY

        playground_r = copy.deepcopy(self.playground)
        self.playground_to_draw_copy = copy.deepcopy(self.playground_to_draw)
        # print(block.block)
        for i in block.block:
            for e in i:
                if playground_r[posY][posX] != 1:
                    if e == 1:
                        self.playground_to_draw_copy[posY][posX] = self.color_digit(e, block.color)
                    playground_r[posY][posX] = e
                posX+=1
            posX = block.posX
            posY+=1
        for row in self.playground_to_draw_copy:
            print(" ".join(str(cell) for cell in row))
        print()

    def put_block(self, block):
        posX = block.posX
        posY = block.posY

        for i in block.block:
            for e in i:
                if self.playground[posY][posX] != 1:
                    if e == 1:
                        self.playground_to_draw[posY][posX] = self.color_digit(e, block.color)
                    self.playground[posY][posX] = e
                posX+=1
            posX = block.posX
            posY+=1
        self.check_rows()

    def check_rows(self):
        width = len(self.playground[0])
        k=0
        for i in range(len(self.playground)-1, -1, -1):
            if 0 not in self.playground[i+k]:
                # Remove filled row
                self.playground.pop(i+k)
                self.playground.insert(0, [0] * width)
                self.playground_to_draw.pop(i+k)
                self.playground_to_draw.insert(0, [0] * width)
                k+=1

    def display(self):
        for row in self.playground_to_draw:
            print(" ".join(str(cell) for cell in row))
        print()

class Player:

    def __init__(self, name, id):
        self.id = id
        self.name = name
        self.points = 0

    def add_points(self, amout):
        self.points+=amout


class Block(ABC):

    def __init__(self, posX, posY, block):
        self.posX = posX
        self.posY = posY
        self.block = block


#TODO: fix left right
    def move(self, direction, playground):
        match direction:
            case "l":
                can = True
                if self.posX == 0:
                        can = False
                if can:
                    for i in range(len(self.block)):
                        # if playground.playground[self.posY+i][self.posX-1] == 1 and self.block[i][0] == 1:
                        if 1 in self.block[i]:
                            index = self.block[i].index(1)-1
                            if playground.playground[self.posY+i][self.posX+index] == 1:
                                can = False
                                break
                if can:
                    self.posX -= 1

            case "r":
                can = True
                if self.posX+len(self.block[0]) == 10:
                        can = False

                if can:
                    for i in range(len(self.block)):
                        if 1 in self.block[i]:
                            # if playground.playground[self.posY+i][self.posX+len(self.block[0])] == 1 and self.block[i][-1] == 1:
                            #Find last matching element index
                            index=len(self.block[i])
                            for el in self.block[i][::-1]:
                                index-=1
                                if el==1:
                                    index+=1
                                    break

                            if playground.playground[self.posY+i][self.posX+index] == 1:
                                can = False
                                break
                if can:
                    self.posX += 1

            case "d":
                if self.posY+len(self.block) == 20:
                    return False
                for i in range(len(self.block[-1])):
                    block_y = -1
                    playground_y = self.posY+len(self.block)
                    while self.block[block_y][i] == 0:
                        if self.block[block_y][i] == 0:
                            block_y -= 1
                            playground_y -=1
                    if playground.playground[playground_y][self.posX+i] == 1 and self.block[block_y][i] == 1:
                        return False

                self.posY += 1
                return True


    def spin(self, playground):
        new_block = self.create_new_block()
        can = True
        for i in self.block:
            ind = 0
            for e in i:
                new_block[ind].insert(0, e)
                ind+=1

        for y in range(0, len(new_block)):
            for x in range(0, len(new_block[0])):
                if playground.length<=self.posX+x or self.posX+x<0 or playground.height<=self.posY+y or self.posY+y<0 or playground.playground[self.posY+y][self.posX+x]==1:
                    return False
        if can:
            self.block = new_block
            return new_block

    def display(self):
        for row in self.block:
            print(" ".join(str(cell) for cell in row))
        print()

    def create_new_block(self):
        new_block = []
        for i in range(len(self.block[0])):
            new_block.append([])
        return new_block


class IBlock(Block):
    def __init__(self, posX, posY):
        self.block: list[list[int]] = [
            [1,1,1,1]
        ]
        self.color = "cyan"
        super().__init__(posX, posY, self.block)


class LBlock(Block):
    def __init__(self, posX, posY):
        self.block: list[list[int]] = [
            [1,1,1],
            [1,0,0]
        ]
        self.color = "orange"
        super().__init__(posX, posY, self.block)


class JBlock(Block):
    def __init__(self, posX, posY):
        self.block: list[list[int]] = [
            [1,0,0],
            [1,1,1]
        ]
        self.color = "blue"
        super().__init__(posX, posY, self.block)


class SBlock(Block):
    def __init__(self, posX, posY):
        self.block: list[list[int]] = [
            [0,1,1],
            [1,1,0]
        ]
        self.color = "green"
        super().__init__(posX, posY, self.block)


class ZBlock(Block):
    def __init__(self, posX, posY):
        self.block: list[list[int]] = [
            [1,1,0],
            [0,1,1]
        ]
        self.color = "red"
        super().__init__(posX, posY, self.block)


class OBlock(Block):
    def __init__(self, posX, posY):
        self.block: list[list[int]] = [
            [1,1],
            [1,1]
        ]
        self.color = "yellow"
        super().__init__(posX, posY, self.block)


class TBlock(Block):
    def __init__(self, posX, posY):
        self.block: list[list[int]] = [
            [0,1,0],
            [1,1,1]
        ]
        self.color = "purple"
        super().__init__(posX, posY, self.block)

def random_block():
    return random.choice([
        IBlock(4, 0), LBlock(4, 0), JBlock(4, 0), SBlock(4, 0), ZBlock(4, 0), OBlock(4, 0), TBlock(4, 0)
    ])

def get_random_color():
    COLORS = ["red", "green", "yellow", "blue", "magenta", "cyan"]
    return random.choice(COLORS)

blocks = []
bl = random_block()
n = Playground(10, 20)
n.create()
color = get_random_color()

import time



import msvcrt

def getch_non_blocking():
    if msvcrt.kbhit():          # key available?
        return msvcrt.getch().decode("utf-8").lower()
    return None
import time

last_fall = time.time()

while True:
    key = getch_non_blocking()

    # INPUT
    if key == 'a':
        bl.move("l", n)
    elif key == 'd':
        bl.move("r", n)
    elif key == 's':
        bl.move("d", n)
    elif key == 'w':
        bl.spin(n)
    elif key == 'q':
        break

    # UPDATE (gravity)
    if time.time() - last_fall > 0.5:
        moved = bl.move("d", n)
        if moved is False:
            n.put_block(bl)
            bl = random_block()
        last_fall = time.time()

    # RENDER
    print("\033[H\033[J", end="")  # clear screen
    n.render_block(bl)

    time.sleep(0.05)