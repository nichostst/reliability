import numpy as np


class Simulation:
    def __init__(self, dist, cutoff, size=10000):
        assert size >= 100, 'Size should be at least 100'
        self._dist = dist
        self._cutoff = cutoff
        self._size = size

    def simulate(self):
        self.trials = self._dist.rvs(size=self._size)
        self.durations = [min(x, y)
                          for x, y
                          in zip(list(self.trials), [self._cutoff]*self._size)]
        self.mtbf = sum(self.durations)/sum(self.trials < self._cutoff)

        # Failure indices and times
        f = np.argwhere(self.trials < self._cutoff).ravel()
        ftimes = np.cumsum(self.durations)[f]
        # Time between failures
        self.tbf = [ftimes[0]]+list(np.diff(ftimes))
