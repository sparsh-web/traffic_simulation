# vehicle.py
import itertools

_id_counter = itertools.count(1)

class Vehicle:
    def __init__(self, arrival_time, vehicle_type='car'):
        self.id = next(_id_counter)
        self.arrival_time = arrival_time
        self.start_service_time = None
        self.departure_time = None
        self.type = vehicle_type

    def wait_time(self):
        if self.start_service_time is None:
            return None
        return self.start_service_time - self.arrival_time

    def service_time(self):
        if self.departure_time is None or self.start_service_time is None:
            return None
        return self.departure_time - self.start_service_time
