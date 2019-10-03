#ぷよぷよ環境構築

import copy
import random

DEBUG = False

class Puyopuyo(object):
    WIDTH = 6
    HEIGHT = 13

    # インスタンス生成時自動呼び出し
    def __init__(self, string=None):
        self.puyos = [[" " for x in range(self.WIDTH)] for y in range(self.HEIGHT)] #空の盤面を作成
        self.pre_puyos = [[" " for x in range(self.WIDTH)] for y in range(self.HEIGHT)] #空の盤面を作成
        self.score = 0
        self.rensa = 0
        self.max_rensa = 0
        self.falling = None
        self.cmd_flag = True

        row = 0
        col = 0

        # if string:
        #     for color in string:
        #         if color == "\n":
        #             col += 1
        #             row = 0
        #             continue
        #         else:
        #             self.puyos[col][row] = color
        #             row += 1


    # 指定ぷよの周辺(上下左右)をチェック
    def scan(self, col, row, chained, color):
        if row < self.WIDTH-1:
            chained = self._check_neighbor(col, row+1, chained, color)
        if col < self.HEIGHT-1:
            chained = self._check_neighbor(col+1, row, chained, color)
        if row > 0:
            chained = self._check_neighbor(col, row-1, chained, color)
        if col > 0:
            chained = self._check_neighbor(col-1, row, chained, color)

        return chained


    # colorとar_colorが同色かを判定
    # 同色ならばchainで繋げる
    def _check_neighbor(self, col, row, chained, color):
        ar_color = self.puyos[col][row]
        if color == ar_color:
            if (col, row) in chained:
                return chained
            chained.append((col, row))
            chained = self.scan(col, row, chained, color)
        return chained


    # ぷよの落下処理
    def fill(self):
        prepuyos = None
        while self.puyos != prepuyos:
            prepuyos = copy.deepcopy(self.puyos)
            for col in range(12, 0, -1):
                for row in range(6):
                    if self.puyos[col][row] == ' ':
                        self.puyos[col][row] = self.puyos[col-1][row]
                        self.puyos[col-1][row] = ' '


    # 盤面からぷよを削除
    def remove_puyo(self, puyos):
        for x in puyos:
            self.puyos[x[0]][x[1]] = ' '


    #
    def update(self):
        # in rensa processing
        if self.falling is None:
            string=''
            puyo_to_remove = set() # 空のセットを生成
            self.pre_puyos = copy.deepcopy(self.puyos)

            if DEBUG:
                for horizontal in self.puyos:
                    string += ''.join(horizontal) + '\n'
                print(string, '++++++++++++++++++++++++++')

            self.fill() #ぷよの落下処理

            # 盤面中に隣り合う同色のぷよが存在するかを判定
            if self.puyos == self.pre_puyos:
                for col in range(self.HEIGHT):
                    for row in range(self.WIDTH):
                        if (col, row) in puyo_to_remove:
                            continue
                        color = self.puyos[col][row]
                        chained = [(col, row)]

                        if color != ' ':
                            chained = self.scan(col, row, chained, color) #ぷよ周辺をチェック

                            if len(chained) >= 4:
                                puyo_to_remove = puyo_to_remove.union(chained)

            #連鎖判定
            if len(puyo_to_remove):
                self.rensa += 1
                self.max_rensa = self.rensa
                self.remove_puyo(puyo_to_remove)

            # スコア換算
            if self.puyos == self.pre_puyos:
                self.score += 10 * self.rensa**2
                self.rensa = 0

                # GAME OVER
                if self.puyos[0][2] != " ":
                    return False
                else:
                    # ネクストぷよを生成
                    self.falling = ({"color":random.choice(("R", "G", "B", "Y")),
                                     "pos":(0, 2)},
                                    {"color":random.choice(("R", "G", "B", "Y")),
                                     "pos":(1, 2)}
                                    )
                    self.cmd_flag = True
        # drop puyo
        else:
            col1, row1 = self.falling[0]["pos"] #col1 = 0, row1 = 2
            col2, row2 = self.falling[1]["pos"] #col2 = 1, row2 = 2

            # on bottom
            if (col1 == (self.HEIGHT-1) or self.puyos[col1+1][row1] != " "
               or col2 == (self.HEIGHT-1) or self.puyos[col2+1][row2] != " "):
                self.puyos[col1][row1] = self.falling[0]["color"]
                self.puyos[col2][row2] = self.falling[1]["color"]
                self.falling = None
            # falling
            else:
                self.falling[0]["pos"] = (col1+1, row1)
                self.falling[1]["pos"] = (col2+1, row2)

        return True


F = """  GYRR
RYYGYG
GYGYRR
RYGYRG
YGYRYG
GYRYRG
YGYRYR
YGYRYR
YRRGRG
RYGYGG
GRYGYR
GRYGYR
GRYGYR"""

def main():
    puyopuyo1 = Puyopuyo(F)
    print("PRESS ENTER KEY")
    while puyopuyo1.falling is None:
        puyopuyo1.update()
        i = raw_input()

if __name__ == '__main__':
    DEBUG = True
    main()
