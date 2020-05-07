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
            t = 0
            while t < self._tlen:
                trial = self._dist.rvs()
                if trial > self._cutoff:
                    t += self._cutoff
                    tot.append([self._cutoff, 0])
                else:
                    t += trial
                    tot.append([trial, 1])
            # Last failure/maintenance does not exist yet
            tot.pop(-1)
            # Get number of failures/maintenances
            maintenance = len([x for x in tot if x[1] == 0])
            failure = len(tot) - maintenance
            self.trials.append(tot)
            self.maintenances.append(maintenance)
            self.failures.append(failure)
