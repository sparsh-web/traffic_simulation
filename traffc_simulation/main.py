# main.py - Fully adaptive for Green, Red, and Yellow

import simpy
import numpy as np
import pandas as pd
from road import Road
from arrivals import ArrivalProcess
from traffic_light import TrafficLight
from metrics import MetricsCollector
from visualization import plot_queue_timeseries, plot_metrics_bar
from vehicle import Vehicle


# 🧠 Adaptive formula for all 3 lights
def compute_adaptive_timings(queue_length, arrival_rate, service_rate, base_green=10, base_red=10, base_yellow=3):
    α, β, γ = 1.5, 5, 2  # tuning constants
    ρ = arrival_rate / service_rate if service_rate > 0 else 1

    # compute each signal duration
    red_time = base_red + β * ρ
    green_time = base_green + α * ((queue_length + (arrival_rate * red_time)) / service_rate)
    yellow_time = base_yellow + γ * ρ

    return round(green_time, 2), round(red_time, 2), round(yellow_time, 2)


def run_simulation(mode, sim_time, arrival_rate, service_rate, lanes, green, yellow, red, num_cars, init_queue):
    np.random.seed(42)
    env = simpy.Environment()

    road = Road(env, name='MainRoad', lanes=lanes, service_rate=service_rate)
    for _ in range(init_queue):
        road.enqueue(Vehicle(arrival_time=0))

    light = TrafficLight(env, road=road, green=green, yellow=yellow, red=red, adaptive=(mode == 'adaptive'))
    arrivals = ArrivalProcess(env, road=road, arrival_rate=arrival_rate, num_cars=num_cars)

    metrics = MetricsCollector([road])

    def snapshotter():
        while True:
            metrics.take_snapshot(env.now)
            yield env.timeout(5)
    env.process(snapshotter())

    env.run(until=sim_time)
    return metrics


def compare_fixed_and_adaptive(sim_time, arrival_rate, service_rate, lanes, green, yellow, red, num_cars, init_queue):
    print(f"\n=== Running FIXED signal simulation (G={green}s, R={red}s, Y={yellow}s) ===")
    metrics_fixed = run_simulation('fixed', sim_time, arrival_rate, service_rate, lanes, green, yellow, red, num_cars, init_queue)
    df_fixed = metrics_fixed.snapshots_df()
    stats_fixed = metrics_fixed.final_stats()
    cong_fixed = metrics_fixed.congestion_probability()

    # Compute adaptive timings
    adaptive_green, adaptive_red, adaptive_yellow = compute_adaptive_timings(init_queue, arrival_rate, service_rate)
    print(f"\nAdaptive timings calculated automatically:")
    print(f"Green = {adaptive_green}s, Red = {adaptive_red}s, Yellow = {adaptive_yellow}s")

    print("\n=== Running ADAPTIVE signal simulation ===")
    metrics_adaptive = run_simulation('adaptive', sim_time, arrival_rate, service_rate, lanes,
                                      adaptive_green, adaptive_yellow, adaptive_red, num_cars, init_queue)
    df_adapt = metrics_adaptive.snapshots_df()
    stats_adapt = metrics_adaptive.final_stats()
    cong_adapt = metrics_adaptive.congestion_probability()

    print("\n--- FIXED SIGNAL STATS ---")
    print(stats_fixed)
    print("Congestion probability (fixed):", cong_fixed)

    print("\n--- ADAPTIVE SIGNAL STATS ---")
    print(stats_adapt)
    print("Congestion probability (adaptive):", cong_adapt)

    print("\nGenerating graphs...")
    plot_queue_timeseries(pd.concat([df_fixed.assign(mode='Fixed'), df_adapt.assign(mode='Adaptive')]))
    plot_metrics_bar(stats_fixed.assign(mode='Fixed'), cong_fixed)
    plot_metrics_bar(stats_adapt.assign(mode='Adaptive'), cong_adapt)


if __name__ == '__main__':
    print("🚦 Intelligent Traffic Flow Simulation (Fully Adaptive) 🚗")
    print("----------------------------------------------------------\n")

    try:
        num_cars = int(input("Enter number of cars to simulate (e.g. 100): "))
        init_queue = int(input("Enter initial queue length (e.g. 10): "))
        arrival_rate = float(input("Enter average arrival rate λ (vehicles/sec, e.g. 0.5): "))
        service_rate = float(input("Enter service rate μ (vehicles/sec during green, e.g. 1.2): "))
        sim_time = int(input("Enter total simulation time (seconds, e.g. 600): "))
        green = int(input("Enter FIXED mode Green signal time (sec, e.g. 20): "))
        yellow = int(input("Enter FIXED mode Yellow signal time (sec, e.g. 3): "))
        red = int(input("Enter FIXED mode Red signal time (sec, e.g. 20): "))
    except ValueError:
        print("❌ Invalid input detected. Please enter numeric values only.")
        exit(1)

    compare_fixed_and_adaptive(
        sim_time=sim_time,
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        lanes=1,
        green=green,
        yellow=yellow,
        red=red,
        num_cars=num_cars,
        init_queue=init_queue
    )
