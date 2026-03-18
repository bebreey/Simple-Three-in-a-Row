import os
import time

AI_USE_CPP = False

if not AI_USE_CPP:  # 是否用C++版的AI脚本
    from ai import AI1Step
else:
    import example


class Gomoku:

    def __init__(self, mode='PVE', board_size=3):
        self.board_size = board_size
        self.g_map = [[0 for y in range(self.board_size)] for x in range(self.board_size)]  # 当前的棋盘
        self.cur_step = 0  # 步数
        self.max_search_steps = 3  # 最远搜索2回合之后
        self.mode = mode  # 'PVP' 或 'PVE'
        self.max_pieces = 3
        self.player1_pieces = []  # [(x, y), ...]
        self.player2_pieces = []
        self.selected_piece = None  # 当前选中的棋子 (x, y)

    def move_1step(self, input_by_window=False, pos_x=None, pos_y=None):
        """
        玩家落子或移动
        """
        player = 1 if self.cur_step % 2 == 0 else 2
        pieces = self.player1_pieces if player == 1 else self.player2_pieces

        if len(pieces) < self.max_pieces:
            # 放置阶段
            if self.g_map[pos_x][pos_y] == 0:
                self.g_map[pos_x][pos_y] = player
                pieces.append((pos_x, pos_y))
                self.cur_step += 1
                return True
        else:
            # 移动阶段
            if self.selected_piece:
                # 尝试移动到新位置
                old_x, old_y = self.selected_piece
                if self.g_map[pos_x][pos_y] == 0:
                    # 检查是否相邻 (可选规则，这里先实现可以移动到任意空位，或者相邻)
                    # 为了游戏性，通常是移动到相邻空位
                    if abs(pos_x - old_x) <= 1 and abs(pos_y - old_y) <= 1:
                        self.g_map[old_x][old_y] = 0
                        self.g_map[pos_x][pos_y] = player
                        pieces.remove((old_x, old_y))
                        pieces.append((pos_x, pos_y))
                        self.selected_piece = None
                        self.cur_step += 1
                        return True
                # 如果点击的是另一个自己的棋子，切换选中
                if self.g_map[pos_x][pos_y] == player:
                    self.selected_piece = (pos_x, pos_y)
                    return False
                # 如果点击的是空位但不合法或对方棋子，取消选中
                self.selected_piece = None
                return False
            else:
                # 选择棋子
                if self.g_map[pos_x][pos_y] == player:
                    self.selected_piece = (pos_x, pos_y)
                    return False
        return False

    def game_result(self, show=False):
        """判断游戏的结局。0为游戏进行中，1为玩家1获胜，2为玩家2获胜，3为平局"""
        target = 3 # 3个棋子，3连即胜
        
        # 1. 判断是否横向连续
        for x in range(self.board_size - target + 1):
            for y in range(self.board_size):
                if self.g_map[x][y] != 0 and all(self.g_map[x+i][y] == self.g_map[x][y] for i in range(target)):
                    if show:
                        return self.g_map[x][y], [(x+i, y) for i in range(target)]
                    else:
                        return self.g_map[x][y]

        # 2. 判断是否纵向连续
        for x in range(self.board_size):
            for y in range(self.board_size - target + 1):
                if self.g_map[x][y] != 0 and all(self.g_map[x][y+i] == self.g_map[x][y] for i in range(target)):
                    if show:
                        return self.g_map[x][y], [(x, y+i) for i in range(target)]
                    else:
                        return self.g_map[x][y]

        # 3. 判断是否有左上-右下的连续
        for x in range(self.board_size - target + 1):
            for y in range(self.board_size - target + 1):
                if self.g_map[x][y] != 0 and all(self.g_map[x+i][y+i] == self.g_map[x][y] for i in range(target)):
                    if show:
                        return self.g_map[x][y], [(x+i, y+i) for i in range(target)]
                    else:
                        return self.g_map[x][y]

        # 4. 判断是否有右上-左下的连续
        for x in range(self.board_size - target + 1):
            for y in range(target - 1, self.board_size):
                if self.g_map[x][y] != 0 and all(self.g_map[x+i][y-i] == self.g_map[x][y] for i in range(target)):
                    if show:
                        return self.g_map[x][y], [(x+i, y-i) for i in range(target)]
                    else:
                        return self.g_map[x][y]

        return 0, [(-1, -1)] if show else 0

    def ai_play_1step(self):
        """简单的 AI 逻辑：随机移动或放置"""
        import random
        player = 2
        pieces = self.player2_pieces
        
        if len(pieces) < self.max_pieces:
            # 放置阶段
            empty_spots = [(x, y) for x in range(self.board_size) for y in range(self.board_size) if self.g_map[x][y] == 0]
            if empty_spots:
                pos_x, pos_y = random.choice(empty_spots)
                self.g_map[pos_x][pos_y] = player
                pieces.append((pos_x, pos_y))
                self.cur_step += 1
        else:
            # 移动阶段
            # 随机选择一个棋子并移动到相邻空位
            random.shuffle(pieces)
            for old_x, old_y in pieces:
                adj_spots = []
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0: continue
                        nx, ny = old_x + dx, old_y + dy
                        if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.g_map[nx][ny] == 0:
                            adj_spots.append((nx, ny))
                if adj_spots:
                    nx, ny = random.choice(adj_spots)
                    self.g_map[old_x][old_y] = 0
                    self.g_map[nx][ny] = player
                    pieces.remove((old_x, old_y))
                    pieces.append((nx, ny))
                    self.cur_step += 1
                    break

    def show(self, res):
        """显示游戏内容"""
        for y in range(15):
            for x in range(15):
                if self.g_map[x][y] == 0:
                    print('  ', end='')
                elif self.g_map[x][y] == 1:
                    print('〇', end='')
                elif self.g_map[x][y] == 2:
                    print('×', end='')

                if x != 14:
                    print('-', end='')
            print('\n', end='')
            for x in range(15):
                print('|  ', end='')
            print('\n', end='')

        if res == 1:
            print('玩家获胜!')
        elif res == 2:
            print('电脑获胜!')
        elif res == 3:
            print('平局!')

    def play(self):
        while True:
            self.move_1step()  # 玩家下一步
            res = self.game_result()  # 判断游戏结果
            if res != 0:  # 如果游戏结果为“已经结束”，则显示游戏内容，并退出主循环
                self.show(res)
                return
            self.ai_move_1step()  # 电脑下一步
            res = self.game_result()
            if res != 0:
                self.show(res)
                return
            self.show(0)  # 在游戏还没有结束的情况下，显示游戏内容，并继续下一轮循环

    def map2string(self):
        mapstring = list()
        for x in range(15):
            mapstring.extend(list(map(lambda x0: x0 + 48, self.g_map[x])))
        return bytearray(mapstring).decode('utf8')
