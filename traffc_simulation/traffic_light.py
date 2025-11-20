# traffic_light.py
import simpy

class TrafficLight:
    """
    Manages a traffic light cycle. If adaptive=True, green time may be extended
    based on road.queue_length() and adaptive_threshold.
    """
    def __init__(self, env: simpy.Environment, road=None, green=30, yellow=3, red=None, adaptive=False):
        self.env = env
        self.road = road
        self.green = green
        self.yellow = yellow
        self.adaptive = adaptive
        # if red not given, set red equal to green by default (single approach)
        self.red = red if red is not None else green
        self.state = 'RED'
        self.process = env.process(self.run())

    def run(self):
        while True:
            # RED phase
            self.state = 'RED'
            if self.road:
                self.road.light_state = 'RED'
            yield self.env.timeout(self.red)

            # GREEN phase (possibly adaptive)
            self.state = 'GREEN'
            if self.road:
                self.road.light_state = 'GREEN'
            green_time = self.green
            if self.adaptive and self.road is not None:
                qlen = self.road.queue_length()
                threshold = getattr(self.road, 'adaptive_threshold', 5)
                if qlen > threshold:
                    # extend green in proportion to excess queue (capped)
                    green_time += min(30, qlen - threshold)
            yield self.env.timeout(green_time)

            # YELLOW phase
            self.state = 'YELLOW'
            if self.road:
                self.road.light_state = 'YELLOW'
            yield self.env.timeout(self.yellow)
