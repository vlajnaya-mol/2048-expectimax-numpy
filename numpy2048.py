import numpy as np

RIGHT = 0
DOWN = 1
LEFT = 2
UP = 3


def get_empty_cells(board):
    return np.argwhere(board == 0)


def get_empty_cells_num(board):
    return np.count_nonzero(board == 0)


def move_exists(board):
    if not np.all(board):
        return True
    return np.any(board[:, 1:] == board[:, :-1]) or np.any(board[1:, :] == board[:-1, :])


def move_possible(board, move):
    board = np.rot90(board, move)
    return np.any((board[:, 1:] == 0) & (board[:, :-1] != 0) | (board[:, 1:] == board[:, :-1]) & (board[:, 1:] != 0))


def _slide(mat):
    mask = mat > 0
    res = np.zeros_like(mat)
    res[np.sort(mask, axis=1)] = mat[mask]
    return res


def step(mat, move, add=1):
    mat = _slide(np.rot90(mat, move))

    mask = mat[:, :-1] == mat[:, 1:]
    mat[:, 1:][mask] += add
    mask[:, 1] ^= mask[:, -1]  # CAUTION! WORKS PROPERLY ONLY FOR 4 x 4 BOARD!
    mat[:, :-1][mask] = 0

    return np.rot90(_slide(mat), 4 - move)


if __name__ == '__main__':
    mat = np.array([[2, 0, 2, 0],
                    [0, 4, 4, 4],
                    [4, 4, 4, 0],
                    [0, 4, 0, 0]])
    print(step(mat, RIGHT))
