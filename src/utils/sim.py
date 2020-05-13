def simulate_fleetwide(dist, cutoff):
    '''
    Simulate failures assuming fleetwide maintenance for one maintenance
    cycle
    '''
    timenow = 0
    durations = []
    sim = dist.rvs()
    while sim < cutoff-timenow:
        durations.append([sim, 1])
        timenow += sim
        sim = dist.rvs()
    durations.append([cutoff-timenow, 0])

    return durations


def get_durations_fleetwide(tlen, cutoff, dist):
    '''
    Simulate for (possibly) multiple maintenance cycles
    '''
    durations = []
    for _ in range(int(tlen/cutoff)):
        durations.extend(simulate_fleetwide(dist, cutoff))

    remainder = tlen % cutoff
    if remainder > 0:
        rem = simulate_fleetwide(dist, remainder)
        rem = [x for x in rem if x[1] == 1]
        durations.extend(rem)

    return durations


def simulate_bycomponent(dist, cutoff, noc, tlen):
    trials = []
    maintenances = []
    failures = []
    for _ in range(noc):
        # Initialize
        tot = []
        t = 0
        while t < tlen:
            trial = dist.rvs()
            if trial > cutoff:
                t += cutoff
                tot.append([cutoff, 0])
            else:
                t += trial
                tot.append([trial, 1])
        # Last failure/maintenance does not exist yet
        tot.pop(-1)
        # Get number of failures/maintenances
        maintenance = len([x for x in tot if x[1] == 0])
        failure = len(tot) - maintenance
        trials.append(tot)
        maintenances.append(maintenance)
        failures.append(failure)
    return [trials, maintenances, failures]
