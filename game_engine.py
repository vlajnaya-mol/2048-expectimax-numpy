import numpy as np
from random import choice
from ai_engine import AI
from numpy2048 import UP, DOWN, LEFT, RIGHT, get_empty_cells, move_exists


class Engine:
    # board = np.array(
    #     [[0, 2, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])

    def __init__(self, size):
        self.AI = AI()
        self.board_len = size
        self.is_working = False
        self.states = self.board = self.score = None
        self.restart()

    def add_cell(self, board):
        i, j = choice(get_empty_cells(board))
        board[i, j] = choice([1, 1, 1, 1, 1, 1, 1, 1, 1, 2])

        self.is_working = move_exists(board)

        return (i, j), (i, j), board[i, j], board[i, j]

    def slide_up(self, board):
        slides = []
        for j in range(self.board_len):
            i = 0
            while i < self.board_len:
                if not board[i, j]:
                    k = i
                    while i < self.board_len and not board[i, j]:
                        i += 1
                    if i < self.board_len:
                        slides.append(([i, j], [k, j], board[i, j]))
                        board[k, j] = board[i, j]
                        board[i, j] = 0
                        i = k
                else:
                    k = i
                    i += 1
                    while i < self.board_len and not board[i, j]:
                        i += 1

                    if not slides or slides[-1][1] != [k, j]:
                        slides.append(([k, j], [k, j], board[k, j]))
                    if i < self.board_len:
                        if board[i, j] == board[k, j]:
                            slides.append(([i, j], [k, j], board[k, j], board[k, j] + 1))
                            self.score += board[k, j] * 2
                            board[k, j] += 1
                            board[i, j] = 0
                        else:
                            slides.append(([i, j], [k + 1, j], board[i, j]))
                            a = board[i, j]
                            board[i, j] = 0
                            board[k + 1, j] = a
                        i = k + 1
        return slides

    def slide_down(self, board):
        slides = []
        for j in range(self.board_len):
            i = self.board_len - 1
            while i >= 0:
                if not board[i, j]:
                    k = i
                    while i >= 0 and not board[i, j]:
                        i -= 1
                    if i >= 0:
                        slides.append(([i, j], [k, j], board[i, j]))
                        board[k, j] = board[i, j]
                        board[i, j] = 0
                        i = k
                else:
                    k = i
                    i -= 1
                    while i >= 0 and not board[i, j]:
                        i -= 1
                    if not slides or slides[-1][1] != [k, j]:
                        slides.append(([k, j], [k, j], board[k, j]))
                    if i >= 0:
                        if board[i, j] == board[k, j]:
                            slides.append(([i, j], [k, j], board[k, j], board[k, j] + 1))
                            self.score += board[k, j] * 2
                            board[k, j] += 1
                            board[i, j] = 0
                        else:
                            slides.append(([i, j], [k - 1, j], board[i, j]))
                            a = board[i, j]
                            board[i, j] = 0
                            board[k - 1, j] = a
                        i = k - 1
        return slides

    def slide_left(self, board):
        slides = []
        for i in range(self.board_len):
            j = 0
            while j < self.board_len:
                if not board[i, j]:
                    k = j
                    while j < self.board_len and not board[i, j]:
                        j += 1
                    if j < self.board_len:
                        slides.append(([i, j], [i, k], board[i, j]))
                        board[i, k] = board[i, j]
                        board[i, j] = 0
                        j = k
                else:
                    k = j
                    j += 1
                    while j < self.board_len and not board[i, j]:
                        j += 1
                    if not slides or slides[-1][1] != [i, k]:
                        slides.append(([i, k], [i, k], board[i, k]))
                    if j < self.board_len:
                        if board[i, j] == board[i, k]:
                            slides.append(([i, j], [i, k], board[i, k], board[i, k] + 1))
                            self.score += board[i, k] * 2
                            board[i, k] += 1
                            board[i, j] = 0
                        else:
                            slides.append(([i, j], [i, k + 1], board[i, j]))
                            a = board[i, j]
                            board[i, j] = 0
                            board[i, k + 1] = a
                        j = k + 1
        return slides

    def slide_right(self, board):
        slides = []
        for i in range(self.board_len):
            j = self.board_len - 1
            while j >= 0:
                if not board[i, j]:
                    k = j
                    while j >= 0 and not board[i, j]:
                        j -= 1
                    if j >= 0:
                        slides.append(([i, j], [i, k], board[i, j]))
                        board[i, k] = board[i, j]
                        board[i, j] = 0
                        j = k
                else:
                    k = j
                    j -= 1
                    while j >= 0 and not board[i, j]:
                        j -= 1
                    if not slides or slides[-1][1] != [i, k]:
                        slides.append(([i, k], [i, k], board[i, k]))
                    if j >= 0:
                        if board[i, j] == board[i, k]:
                            slides.append(([i, j], [i, k], board[i, k], board[i, k] + 1))
                            self.score += board[i, k] * 2
                            board[i, k] += 1
                            board[i, j] = 0
                        else:
                            slides.append(([i, j], [i, k - 1], board[i, j]))
                            a = board[i, j]
                            board[i, j] = 0
                            board[i, k - 1] = a
                        j = k - 1
        return slides

    def cell_moved(self, slides):
        return any(slide[0] != slide[1] for slide in slides)

    def move(self, direction):
        slides = []
        self.states.append(self.board.copy())
        if direction is UP:
            slides = self.slide_up(self.board)
        elif direction is RIGHT:
            slides = self.slide_right(self.board)
        elif direction is DOWN:
            slides = self.slide_down(self.board)
        elif direction is LEFT:
            slides = self.slide_left(self.board)
        if self.cell_moved(slides):
            slides.append(self.add_cell(self.board))
        return slides

    def let_ai_move(self):
        if self.board_len != 4:
            raise NotImplementedError()
        return self.move(self.AI.get_expectimax_move(self.board))

    def undo(self):
        if not self.states:
            return False
        self.board = self.states.pop()
        self.is_working = True

    def restart(self):
        self.board = np.zeros((self.board_len, self.board_len), dtype=np.int)
        self.states = []
        self.score = 0
        self.is_working = True
        self.add_cell(self.board)
