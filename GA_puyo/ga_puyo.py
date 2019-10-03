#!/usr/bin/env python
# -*- coding: utf-8 -*-
#遺伝的アルゴリズム

import pygame, random
import sys #sysモジュール: コマンドライン引数受け取りのため
import math
import copy

import ga_puyo_ as puyo

args = sys.argv # コマンドライン引数受け取り
ai = True
# if len(args) >= 2 else False # コマンドライン引数（=seed値）でAIモード

IND = 6 # 個体数()
GENE = 300 # 遺伝子数()

class Game(object):
    SCREEN_SIZE = (640, 480)

    def __init__(self): #インスタンス生成時自動呼び出し
        pygame.init() #pygameモジュール初期化
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)

        self.gem = {"R":pygame.image.load("resource/r.png").convert_alpha(),
                    "G":pygame.image.load("resource/g.png").convert_alpha(),
                    "B":pygame.image.load("resource/b.png").convert_alpha(),
                    "Y":pygame.image.load("resource/y.png").convert_alpha()}

        #self.player1 = puyo.Puyopuyo(puyo.F)
        self.player1 = puyo.Puyopuyo("")
        self.player1.controller = {"left":pygame.K_LEFT,
                         "down":pygame.K_DOWN,
                         "right":pygame.K_RIGHT,
                         "roll":pygame.K_a,
                         "esc":pygame.K_ESCAPE,
                         "back":pygame.K_BACKSPACE}

        self.control_time = 1 if ai else 400
        self.update_time = 2 if ai else 1200
        self.generation = 0 # 世代
        self.ind = [[0 for i in range(GENE)] for j in range(IND)] # 遺伝子情報
        self.ind_num = 0 # 個体番号
        self.gene_num = 0 # 遺伝子番号
        self.i_score = [0] * IND # 得点
        self.i_chain = [0] * IND # 最大連鎖数
        for i in range(IND):
            for j in range(GENE):
                self.ind[i][j] = random.randrange(24) #実際は22状態 計算簡略のため

        self.player1.OFFSET = (100, 100)
        self.screen.fill((100, 100, 100),
                         (self.player1.OFFSET[0], self.player1.OFFSET[1], self.player1.WIDTH*24, self.player1.HEIGHT*24))
        self.draw(self.player1)
        pygame.display.update()

        self.clock = pygame.time.Clock()

    def draw(self, p):
        #要素をチェックしカラーならば描画
        x_offset, y_offset = p.OFFSET # (x_offset, y_offset) = (100, 100)
        for y, row in enumerate(p.puyos):
            for x, color in enumerate(row):
                if color != " ":
                    self.screen.blit(self.gem[color], (x_offset + x*24, y_offset + y*24))
        if p.falling: # 落下中(?)ならば
            for i in range(2):
                y, x = p.falling[i]["pos"]
                if y >= 0 and x >= 0:
                    self.screen.blit(self.gem[p.falling[i]["color"]], (x_offset + x*24, y_offset + y*24))

    def command(self):#1-24の数字を対応した操作で返す(左,右,回転)
        cmd = self.ind[self.ind_num][self.gene_num]
        if cmd % 6 < 3:
            left = cmd % 6 + 1
            right = 0
        else:
            left = 0
            right = cmd % 6 - 1
        roll = int(cmd / 6)
        self.gene_num += 1
        if self.gene_num == GENE:
            self.gene_num = 0

        return left,right,roll

    def play(self):
        counter = 0 #counter: 1コマあたりの動き
        while True:
            # print(counter)
            counter += 1

            # exit game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            # control puyo
            if self.player1.falling and not (counter % self.control_time):
                keys = pygame.key.get_pressed() #全てのキーの入力状態を取得
                col1, row1 = self.player1.falling[0]["pos"] #col1 = 0, row1 = 2
                col2, row2 = self.player1.falling[1]["pos"] #col2 = 1, row2 = 2
                a1 = col1 - col2
                a2 = row1 - row2

                # ゲーム終了
                if keys[self.player1.controller["esc"]]:
                    pygame.quit()

                if ai and self.player1.cmd_flag:
                    self.player1.cmd_flag = False
                    left,right,roll = self.command()

                #プレイヤー操作用
                # else:
                #     left = 0
                #     right = 0
                #     roll = 0
                #     if keys[self.player1.controller["left"]]:
                #         left = 1
                #     if keys[self.player1.controller["right"]]:
                #         right = 1
                #     if keys[self.player1.controller["roll"]]:
                #         roll = 1

                while roll > 0:
                    col1, row1 = self.player1.falling[0]["pos"]
                    col2, row2 = self.player1.falling[1]["pos"]
                    a1 = col1 - col2
                    a2 = row1 - row2
                    if (row1+a1 in (-1, self.player1.WIDTH)) or col1-a2 == self.player1.HEIGHT or self.player1.puyos[col1-a2][row1+a1] != " ":
                        pass
                    else:
                        self.player1.falling[1]["pos"] = (col1-a2, row1+a1)
                    roll -= 1
                while left > 0:
                    col1, row1 = self.player1.falling[0]["pos"]
                    col2, row2 = self.player1.falling[1]["pos"]
                    a1 = col1 - col2
                    a2 = row1 - row2
                    if (row1 > 0 and self.player1.puyos[col1][row1-1] == " ") and (row2 > 0 and self.player1.puyos[col2][row2-1] == " "):
                        self.player1.falling[0]["pos"] = (col1, row1-1)
                        self.player1.falling[1]["pos"] = (col2, row2-1)
                    left -= 1
                while right > 0:
                    col1, row1 = self.player1.falling[0]["pos"]
                    col2, row2 = self.player1.falling[1]["pos"]
                    a1 = col1 - col2
                    a2 = row1 - row2
                    if (row1 < self.player1.WIDTH-1 and self.player1.puyos[col1][row1+1] == " ") and (row2 < self.player1.WIDTH-1 and self.player1.puyos[col2][row2+1] == " "):
                        self.player1.falling[0]["pos"] = (col1, row1+1)
                        self.player1.falling[1]["pos"] = (col2, row2+1)
                    right -= 1
                if keys[self.player1.controller["down"]] or ai:
                    while (col1 < self.player1.HEIGHT-1 and self.player1.puyos[col1+1][row1] == " ") and (col2 < self.player1.HEIGHT-1 and self.player1.puyos[col2+1][row2] == " "):
                        self.player1.falling[0]["pos"] = (col1+1, row1)
                        self.player1.falling[1]["pos"] = (col2+1, row2)
                        col1, row1 = self.player1.falling[0]["pos"]
                        col2, row2 = self.player1.falling[1]["pos"]

            # update puyos' position
            update = True

            if not (counter % self.update_time):
                update = self.player1.update()

            if self.i_chain[self.ind_num] < self.player1.max_rensa:
                self.i_chain[self.ind_num] = self.player1.max_rensa
                self.i_score[self.ind_num] += self.player1.score
            if ai and ((not update) or self.gene_num == GENE-1):
                update = True
                self.i_score[self.ind_num] = self.gene_num

                #世代 ぷよの個数 連鎖数
                print(self.generation, self.i_score[self.ind_num], self.i_chain[self.ind_num])
                if self.ind_num == IND-1:
                    random.seed(None)
                    # その世代の各情報を調べる
                    max_score = 0 # 最大連鎖の中での最大得点
                    max_chain = max(self.i_chain) # 最大連鎖
                    e = 0
                    for i in range(IND):
                        if self.i_chain[i] == max_chain and self.i_score[i] > max_score:
                            e = i
                            max_score = self.i_score[i]
                    elite = copy.deepcopy(self.ind[e])
                    print('best is', e)
                    print('max_rensa is', max_chain)
                    # print(elite)

                    # 次の世代に遺伝子を渡す
                    for i in range(IND):
                        if i < IND - 1: # (IND-1)個は二点交叉
                            r1 = random.randrange(0, GENE-1) # [- - - - r1 - … - - - - - - - ]
                            r2 = random.randrange(r1,GENE)   # [- - - - r1 - … - - r2 - - - -]
                            for j in range(GENE):
                                r = random.randrange(2)
                                if r == 0:
                                    if r1 < j and j < r2:    # [- - - - r1 <elite> r2 - - - -]
                                        self.ind[i][j] = self.ind[i+1][j]
                                    else:
                                        self.ind[i][j] = elite[j]
                                else:
                                    if r1 < j and j < r2:    # [<elite> r1 - … - - r2 <elite>]
                                        self.ind[i][j] = elite[j]
                                    else:
                                        self.ind[i][j] = self.ind[i+1][j]
                            r = random.randrange(2) # 0～1
                            if r == 0: # 稀に変異を起こす
                                r = random.randrange(9) + 1 # 1～9
                                for j in range(r):
                                    self.ind[i][random.randrange(max_score)] = random.randrange(24)
                        else: # 最良個体を１つだけ引き継ぐ
                            self.ind[i] = copy.deepcopy(elite)
                        self.i_score[i] = 0
                        self.i_chain[i] = 0

                    self.generation += 1
                    self.ind_num = 0
                    if self.generation % 10 == 0: # データを保存
                        if self.generation == 10:
                            file = open('result2.txt', 'w')
                        else:
                            file = open('result2.txt', 'a')
                        savedata = 'generation:' + str(self.generation) + '\n_chain:' + str(max_chain) + '\n_score:' + str(max_score) + '\n'
                        file.write(savedata)
                        file.close()
                else:
                    self.ind_num += 1
                self.gene_num = 0

                if ai:
                    # random.seed(int(args[1]))
                    random.seed(3) #引数を指定することで毎回同じ乱数を生成できる
                self.player1 = puyo.Puyopuyo("") # 初期化
                self.player1.controller = {"left":pygame.K_LEFT,
                                 "down":pygame.K_DOWN,
                                 "right":pygame.K_RIGHT,
                                 "roll":pygame.K_a,
                                 "esc":pygame.K_ESCAPE,
                                 "back":pygame.K_BACKSPACE}
                self.player1.OFFSET = (100, 100)

            # update screen
            self.screen.fill((100, 100, 100),
                             (self.player1.OFFSET[0],
                              self.player1.OFFSET[1],
                              self.player1.WIDTH*24,
                              self.player1.HEIGHT*24)
                             )

            keys_d = pygame.key.get_pressed()
            if not ai:
                fps = 10
                self.draw(self.player1)
                pygame.display.update()
            if ai and keys_d[self.player1.controller["back"]]:
                fps = 8
                self.draw(self.player1)
                pygame.display.update()
            else:
                fps = 10000
            self.clock.tick(fps)

            if counter == 2400:
                counter = 0

if __name__ == "__main__":
    Game().play()
