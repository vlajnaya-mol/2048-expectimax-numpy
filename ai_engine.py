import numpy as np
from numpy2048 import (UP, DOWN, LEFT, RIGHT,
                       get_empty_cells, get_empty_cells_num, move_possible, move_exists, step)

def _score_arr(arr):
    return sum(arr)
    # inc = dec = 1
    # arr_sum = arr[0]
    # for i in range(1, arr.size):
    #     if arr[i - 1] < arr[i]:
    #         dec = 0
    #         inc += 1
    #         arr_sum += arr[i] * inc
    #     else:
    #         dec += 1
    #         inc = 0
    #         arr_sum += arr[i] * dec
    # arr = arr[::-1]
    # inc = dec = 1
    # arr_sum += arr[0]
    # for i in range(1, arr.size):
    #     if arr[i - 1] < arr[i]:
    #         dec = 0
    #         inc += 1
    #         arr_sum += arr[i] * inc
    #     else:
    #         dec += 1
    #         inc = 0
    #         arr_sum += arr[i] * dec
    # return arr_sum


def _get_hash(board):
    return hash(bytes(board))


def _get_depth(m):
    empty_num = get_empty_cells_num(m)
    if empty_num < 3:
        depth = 4
    elif empty_num < 7:
        depth = 3
    else:
        depth = 2
    return depth


def _get_possible_boards(board):
    expectations = []
    empty_cells = get_empty_cells(board)
    for i, j in empty_cells:
        add4 = board.copy()
        add4[i, j] = 2
        expectations.append((.1 / len(empty_cells), add4))

        add2 = board.copy()
        add2[i, j] = 1
        expectations.append((.9 / len(empty_cells), add2))
    return expectations


class AI:
    def __init__(self):
        self.hash_map = dict()
        self.score_map = dict()
        self._set_score_map()

    def _hash_board(self, board, val):
        self.hash_map[_get_hash(board)] = val
        self.hash_map[_get_hash(np.flip(board, 0))] = val
        self.hash_map[_get_hash(np.flip(board, 1))] = val
        self.hash_map[_get_hash(np.flip(board, (0, 1)))] = val

    def _set_score_map(self):
        m_range = range(12)
        for i in m_range:
            for j in m_range:
                for k in m_range:
                    for h in m_range:
                        self.score_map[(i, j, k, h)] = _score_arr(np.array([i, j, k, h]))

    def _score(self, m):
        empty_num = get_empty_cells_num(m)
        max_v = np.amax(m)
        sum_m = (self.score_map[(m[0, 0], m[0, 1], m[0, 2], m[0, 3])]
                 + self.score_map[(m[3, 0], m[3, 1], m[3, 2], m[3, 3])]
                 + self.score_map[(m[0, 0], m[1, 0], m[2, 0], m[3, 0])]
                 + self.score_map[(m[0, 3], m[1, 3], m[2, 3], m[3, 3])]) * 2
        return (empty_num / 10 *
                (sum_m +
                 (self.score_map[(m[1, 0], m[1, 1], m[1, 2], m[1, 3])]
                  + self.score_map[(m[2, 0], m[2, 1], m[2, 2], m[2, 3])]
                  + self.score_map[(m[0, 1], m[1, 1], m[2, 1], m[3, 1])]
                  + self.score_map[(m[0, 2], m[1, 2], m[2, 2], m[3, 2])]))
                + max_v * 4)

    def get_expectimax_move(self, board):
        move_scores = dict()
        depth = _get_depth(board)

        for move in [UP, DOWN, LEFT, RIGHT]:
            if move_possible(board, move):
                next_step = step(board, move)
                move_scores[move] = sum(
                    [prob * self._expectimax(expectation, depth - 1)
                     for prob, expectation in _get_possible_boards(next_step)])
                self._hash_board(next_step, move_scores[move])

        return max(list(move_scores), key=lambda k: move_scores[k])

    def _expectimax(self, board, depth):
        hashed = _get_hash(board)
        if hashed in self.hash_map:
            return self.hash_map[hashed]
        if depth == 0 or not move_exists(board):
            return self._score(board)
        # depth = min(depth, get_depth(board))
        next_steps = [step(board, move) for move in [UP, DOWN, LEFT, RIGHT] if move_possible(board, move)]

        res = max([sum([prob * self._expectimax(expectation, depth - 1)
                        for prob, expectation in _get_possible_boards(next_step)])  # / get_empty_cells_num(next_step)
                   for next_step in next_steps])
        self._hash_board(board, res)
        return res

