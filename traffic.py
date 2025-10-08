# 🚦 Traffic Flow Simulation at Signals
# Author: (Your Name)
# Description: Simulates car flow through traffic signals using probability and adaptive timing.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------
#  Function: Simulate Traffic Flow
# ------------------------------
def simulate(arrival_rates, green_time, red_time, total_time):
    num_roads = len(arrival_rates)
    total_seconds = total_time * 60
    cycle_time = green_time + red_time
    num_cycles = total_seconds // cycle_time

    queue_lengths = [0] * num_roads
    all_queues = [[] for _ in range(num_roads)]
    total_passed = [0] * num_roads

    print("\n🚦 Starting Traffic Simulation...\n")

    for cycle in range(1, int(num_cycles) + 1):
        print(f"----- Cycle {cycle} -----")
        for i in range(num_roads):
            # Cars arrive randomly using Poisson distribution
            arrived = np.random.poisson(arrival_rates[i])
            # Cars that can pass = proportional to green time
            passed = min(queue_lengths[i] + arrived, int(green_time * (arrival_rates[i] / 60)))
            queue_lengths[i] = max(0, queue_lengths[i] + arrived - passed)
            total_passed[i] += passed

            all_queues[i].append(queue_lengths[i])

            print(f"Road {i+1} → Arrived: {arrived} | Passed: {passed} | Waiting: {queue_lengths[i]}")
        print("--------------------------")

    # Collect stats
    avg_queue = [np.mean(q) for q in all_queues]
    max_queue = [np.max(q) for q in all_queues]

    print("\n✅ Simulation Complete!")
    for i in range(num_roads):
        print(f"Road {i+1}: Avg Queue = {avg_queue[i]:.2f}, Max Queue = {max_queue[i]}, Cars Passed = {total_passed[i]}")

    return all_queues, avg_queue, total_passed

# ------------------------------
#  Function: Suggest Adaptive Signal Timings
# ------------------------------
def suggest_adaptive_signals(avg_queue, total_green_time):
    total_q = sum(avg_queue)
    suggested = []

    print("\n🧠 Suggested Adaptive Signal Timings:")
    for i, q in enumerate(avg_queue):
        if total_q == 0:
            time = total_green_time / len(avg_queue)
        else:
            time = (q / total_q) * total_green_time
        suggested.append(round(time, 1))
        print(f"Road {i+1}: {suggested[-1]} seconds (based on avg queue {q:.2f})")
    return suggested

# ------------------------------
#  Function: Plot Results
# ------------------------------
def plot_results(all_queues, suggested_green):
    plt.figure(figsize=(8,5))
    for i, q in enumerate(all_queues):
        plt.plot(q, label=f"Road {i+1}")
    plt.title("Queue Length Over Cycles")
    plt.xlabel("Cycle Number")
    plt.ylabel("Queue Length")
    plt.legend()
    plt.show()

    plt.figure(figsize=(6,4))
    roads = [f"Road {i+1}" for i in range(len(suggested_green))]
    plt.bar(roads, suggested_green)
    plt.title("Suggested Adaptive Green Time per Road")
    plt.ylabel("Seconds")
    plt.show()

# ------------------------------
#  MAIN PROGRAM
# ------------------------------
print("🚗 Traffic Flow Simulation at Signals 🚦")
print("1. Manual Input")
print("2. Use Dataset")

choice = input("Choose an option (1 or 2): ")

if choice == '1':
    num_roads = int(input("Enter number of roads: "))
    arrival_rates = []
    for i in range(num_roads):
        rate = float(input(f"Enter car arrival rate for Road {i+1} (cars/min): "))
        arrival_rates.append(rate)
    green_time = int(input("Enter green light duration (seconds): "))
    red_time = int(input("Enter red light duration (seconds): "))
    total_time = int(input("Enter total simulation time (minutes): "))

elif choice == '2':
    file_path = input("Enter dataset file path (e.g., traffic.csv): ")
    data = pd.read_csv(file_path)
    print("\nColumns available:", list(data.columns))
    column = input("Enter column name for traffic volume (e.g., 'traffic_volume'): ")

    num_roads = int(input("Enter number of roads to simulate: "))
    arrival_rates = (data[column][:num_roads] / 60).tolist()
    green_time = int(input("Enter green light duration (seconds): "))
    red_time = int(input("Enter red light duration (seconds): "))
    total_time = len(data) // num_roads

else:
    print("Invalid choice! Exiting...")
    exit()

# Run simulation
all_queues, avg_queue, total_passed = simulate(arrival_rates, green_time, red_time, total_time)

# Suggest adaptive timings
suggested = suggest_adaptive_signals(avg_queue, green_time * len(arrival_rates))

# Plot graphs
plot_results(all_queues, suggested)

print("\n📊 Simulation Finished Successfully!")
print("You can now analyze results or re-run with adaptive timings.")
