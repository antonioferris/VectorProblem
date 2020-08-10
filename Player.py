from constants import N, HIGH, LOW
import numpy as np


class Player:
    def turn(self, history):
        pass

class BasicPlayer1:
    def turn(self, history):
        if not history:
            return (np.array([HIGH, HIGH, HIGH, 0, 0, 0, 0]), 'Get Feedback')
        elif len(history) == 1:
            return (np.array([0, 0, 0, HIGH, HIGH, HIGH, HIGH]), 'Get Feedback')
        vec = np.zeros((N,))
        for v, score in history:
            if score > 0:
                vec += v
            else:
                vec -= v
        return (vec, 'Submit')

class BasicPlayer2:
    def turn(self, history):
        if not history:
            return (np.array([HIGH, HIGH, HIGH, 0, 0, 0, 0]), 'Get Feedback')
        elif len(history) == 1:
            return (np.array([0, 0, 0, HIGH, HIGH, 0, 0]), 'Get Feedback')
        elif len(history) == 2:
            return (np.array([0, 0, 0, 0, 0, HIGH, HIGH]), 'Get Feedback')
        vec = np.zeros((N,))
        for v, score in history:
            if score > 0:
                vec += v
            else:
                vec -= v
        return (vec, 'Submit')

class PlayerUtil:
    # sample a point in R^10 that could be the base state given
    # a history with complete vectors (no zeros)
    def sample_point(self, history):
        p = len(history)
        M = np.zeros((p, N))
        b = np.zeros((p,))
        for i in range(p):
            v, sc = history[i]
            M[i] = v
            b[i] = sc

        # choose indexes to fix
        # N - p variables can vary in a system of equations with N params and p eqs
        fixed_idxs = np.array([0, 1, 5, 6])
        var_idxs = np.array(list(set(range(N)) - set(fixed_idxs)))
        # print('idxs')
        # print(fixed_idxs, var_idxs)
        PT = np.zeros((N,))
        # set the fixed variables
        PT[fixed_idxs] = np.random.uniform(LOW, HIGH, (N - p,))
        # move these 'fixed' variables to the other side of the equation
        b -= np.sum(M * PT, axis=1)

        # now, create an equation with the non fixed variables
        A = M[:, var_idxs]
        x = np.linalg.solve(A, b)

        # now, add the solved for vars back into our point
        PT[var_idxs] = x

        return PT

    def sample_points(self, history, n, boxed=True):
        missed = 0
        pts = []
        ct = 0
        for i in range(100 * n):
            pt = self.sample_point(history)
            if not boxed or (np.all(-10 <= pt) and np.all(pt <= 10)):
                pts.append(pt)
                ct += 1
            else:
                missed += 1
            if ct >= n:
                break
        if boxed and ct < n:
            print('low hit rate detected')
        return np.array(pts)

class AdvancedPlayer1(PlayerUtil):
    def turn(self, history):
        v1 = np.array([1, 1, 1, 1, 1, 1, 1]) * HIGH
        v2 = np.array([1, -1, 1, -1, 1, 1, 1]) * LOW
        v3 = np.array([1, 1, 1, 1, -1, -1, -1]) * HIGH
        if not history:
            self.submitting = False
            return (v1, 'Get Feedback')
        elif len(history) == 1:
            return (v2, 'Get Feedback')
        elif len(history) == 2:
            return (v3, 'Get Feedback')

        elif self.submitting == False:
            pts = self.sample_points(history, 2000, boxed=True)
            mean = np.mean(pts, axis=0)
            self.submission = np.sign(mean) * HIGH
            self.submitting = True
        return (self.submission, 'Submit')