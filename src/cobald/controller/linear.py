import trio

from cobald.interfaces import Pool, Controller

from cobald.daemon import service

from math import ceil


@service(flavour=trio)
class LinearController(Controller):
    """
    Controller that linearly increases or decreases demand

    :param target: the pool to manage
    :param low_utilisation: pool utilisation below which resources are decreased
    :param high_allocation: pool allocation above which resources are increased
    :param rate: maximum change of demand in resources per second
    :param interval: interval between adjustments in seconds
    """

    def __init__(
        self, target: Pool, low_utilisation=0.5, high_allocation=0.5, rate=1, interval=1
    ):
        super().__init__(target=target)
        assert rate > 0
        self.rate = rate
        self.interval = interval
        assert low_utilisation <= high_allocation
        self.low_utilisation = low_utilisation
        self.high_allocation = high_allocation

    async def run(self):
        while True:
            self.regulate(self.interval)
            await trio.sleep(self.interval)

    def regulate(self, interval):
        if self.target.utilisation < self.low_utilisation:
            self.target.demand -= interval * self.rate
        elif self.target.allocation > self.high_allocation:
            self.target.demand += interval * self.rate

    def regulate_stepwise(self, interval):
        low = self.low_utilisation
        high = self.high_allocation
        print('Demand: {}, Supply: {}, Allocation: {}, Utilisation: {}'.format(
            self.target.demand,
            self.target.supply,
            self.target.allocation,
            self.target.utilisation))
        '''
        if self.target.demand == self.target.supply:
            if self.target.allocation < low:
                new_demand = ceil(self.target.supply * self.target.utilisation)
                print('Demand is now {}, adjust demand to {}'.format(self.target.demand, new_demand))
                self.target.demand = new_demand
            elif self.target.allocation > high:
                self.target.demand += self.rate
            else:
                pass
        '''
        if self.target.allocation < low:
            target_utilisation = 0.8 # 80% utilisation after adjusting the demand
            print('Adjust demand based on utilisation {}'.format(self.target.utilisation))
            new_demand = int(ceil(self.target.supply * self.target.utilisation / target_utilisation))
            print('Demand is now {}, adjust demand to {}'.format(self.target.demand, new_demand))
            self.target.demand = new_demand
        elif (self.target.demand == self.target.supply) and (self.target.allocation > high):
            print('Increase demand by {}'.format(self.rate))
            self.target.demand += self.rate
        else:
            print('Do nothing')
            pass
