class Simulation:
    def __init__(self, noc, dist, cutoff, tlen):
        self._noc = noc
        self._dist = dist
        self._cutoff = cutoff
        self._tlen = tlen

    def simulate(self):
        self.trials = []
        self.maintenances = []
        self.failures = []
        for _ in range(self._noc):
            # Initialize
            tot = []
            while sum(tot) < self._tlen:
                trial = self._dist.rvs()
                tot.append(min(trial, self._cutoff))
            # Last failure/maintenance is truncated
            tot.pop(-1)
            # Get number of failures/maintenances
            maintenance = tot.count(self._cutoff)
            failure = len(tot) - maintenance
            self.trials.append(tot)
            self.maintenances.append(maintenance)
            self.failures.append(failure)

        '''
        self.durations = [min(x, y)
                          for x, y
                          in zip(list(self.trials), [self._cutoff]*self._tlen)]
        self.mtbf = sum(self.durations)/sum(self.trials < self._cutoff)

        # Failure indices and times
        f = np.argwhere(self.trials < self._cutoff).ravel()
        ftimes = np.cumsum(self.durations)[f]
        # Time between failures
        self.tbf = [ftimes[0]]+list(np.diff(ftimes))
        '''
