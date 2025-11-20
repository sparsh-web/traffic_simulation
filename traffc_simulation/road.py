# road.py
import simpy
import numpy as np
from vehicle import Vehicle

class Road:
    """
    Models a single approach to the intersection with one or more service lanes.
    Vehicles queue during RED and are served during GREEN.
    service_rate is vehicles per second per lane when green.
    """
    def __init__(self, env: simpy.Environment, name='R1', lanes=1, service_rate=1.0):
        self.env = env
        self.name = name
        self.lanes = lanes
        self.service_rate = service_rate  # vehicles/sec per lane during green
        self.queue = []         # list[Vehicle]
        self.passed = []        # list[Vehicle] that have departed
        self.light_state = 'RED'
        # simple adaptive threshold (can be changed externally)
        self.adaptive_threshold = 5
        # start the serving process
        self.process = env.process(self._serve())

    def enqueue(self, vehicle: Vehicle):
        self.queue.append(vehicle)

    def queue_length(self):
        return len(self.queue)

    def _vehicles_can_depart_per_second(self):
        return max(0.000001, self.lanes * self.service_rate)

    def _serve(self):
        while True:
            if self.light_state == 'GREEN' and self.queue:
                # inter-departure mean time given service rate
                rate = self._vehicles_can_depart_per_second()
                mean_inter = 1.0 / rate
                # pop one vehicle and serve
                vehicle = self.queue.pop(0)
                vehicle.start_service_time = self.env.now
                # model service time as exponential around mean_inter (MM/1 or MM/c behaviour)
                service_duration = np.random.exponential(mean_inter)
                yield self.env.timeout(service_duration)
                vehicle.departure_time = self.env.now
                self.passed.append(vehicle)
            else:
                # small wait to avoid busy loop
                yield self.env.timeout(0.5)
