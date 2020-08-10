import numpy as np
from Player import *
from constants import *

def init_game_state():
    game_state = np.random.uniform(LOW, HIGH, (N,))
    return game_state

# test the strategy defined by player on n random games
def test_strategy(player, n):
    scores = 0
    for _ in range(n):
        scores += run_game(player)
    return scores / n

def score(vec, game_state):
    return np.dot(vec, game_state)

def run_game(player):
    game_state = init_game_state()
    history = []
    total_score = 0
    for _ in range(TURNS):
        vec, act = player.turn(history)
        sc = score(vec, game_state)
        if act == 'Submit':
            total_score += sc
        else:
            history.append((vec, sc))
    return total_score

def test_players():
    to_test = [BasicPlayer1(), BasicPlayer2(), AdvancedPlayer1(), AdvancedPlayer2()]
    n = 100

    for player in to_test:
        avg = test_strategy(player, n)
        print(player.__class__.__name__, 'scored an average score of', avg, 'over', n, 'tests')

def test_sample_point():
    game_state = init_game_state()
    v1 = np.array([1, 1, 1, 1, 1, 1, 1]) * HIGH
    v2 = np.array([1, -1, 1, -1, 1, 1, 1]) * LOW
    v3 = np.array([1, 1, 1, 1, -1, -1, -1]) * HIGH
    history = [(v1, score(v1, game_state)), (v2, score(v2, game_state)), (v3, score(v3, game_state))]
    # print(history)
    # pt = sample_point(history)
    # print('PT', pt)
    pts = PlayerUtil.sample_points(history, 500)
    print(pts.shape)
    print(np.mean(pts, axis=0))
    print(game_state)

def main():
    test_players()
    # test_sample_point()


if __name__ == '__main__':
    main()