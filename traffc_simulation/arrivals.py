# arrivals.py
import numpy as np
import simpy
from vehicle import Vehicle

class ArrivalProcess:
    """
    Generates vehicles following a Poisson process (exponential inter-arrivals).
    arrival_rate: lambda (vehicles per second)
    num_cars: stop after a fixed number of vehicles (optional)
    vehicle_mix: dict mapping type->probability
    """
    def __init__(self, env: simpy.Environment, road, arrival_rate=0.5, num_cars=None, vehicle_mix=None):
        self.env = env
        self.road = road
        self.arrival_rate = arrival_rate
        self.num_cars = num_cars
        self.vehicle_mix = vehicle_mix or {'car': 0.95, 'bus': 0.03, 'bike': 0.02}
        self.process = env.process(self.run())

    def run(self):
        car_count = 0
        while True:
            if self.num_cars and car_count >= self.num_cars:
                break  # stop when limit reached
            # generate exponential inter-arrival times
            inter = np.random.exponential(1.0 / self.arrival_rate)
            yield self.env.timeout(inter)
            # sample vehicle type and add to queue
            vtype = self._sample_type()
            v = Vehicle(arrival_time=self.env.now, vehicle_type=vtype)
            self.road.enqueue(v)
            car_count += 1

    # ✅ MISSING FUNCTION added here
    def _sample_type(self):
        types = list(self.vehicle_mix.keys())
        probs = list(self.vehicle_mix.values())
        return np.random.choice(types, p=probs)
