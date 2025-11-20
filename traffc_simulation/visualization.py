# visualization.py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_queue_timeseries(df_snapshots):
    """
    df_snapshots: DataFrame with columns ['time','road','queue_length']
    """
    if df_snapshots.empty:
        print("No snapshot data to plot.")
        return
    fig, ax = plt.subplots(figsize=(9,4))
    for road in df_snapshots['road'].unique():
        sub = df_snapshots[df_snapshots['road'] == road]
        ax.plot(sub['time'], sub['queue_length'], label=road)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Queue length (vehicles)')
    ax.set_title('Queue length over time')
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_metrics_bar(final_stats_df, congestion_probs):
    """
    final_stats_df: DataFrame with columns ['road','avg_wait_time','avg_queue_length']
    congestion_probs: dict road->prob
    """
    if final_stats_df.empty:
        print("No final stats to plot.")
        return
    roads = final_stats_df['road'].tolist()
    avg_waits = final_stats_df['avg_wait_time'].fillna(0).tolist()
    avg_q = final_stats_df['avg_queue_length'].tolist()
    cong = [congestion_probs.get(r, 0.0) for r in roads]

    x = np.arange(len(roads))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9,4))
    ax.bar(x - width, avg_waits, width, label='Avg wait (s)')
    ax.bar(x, avg_q, width, label='Avg queue')
    ax.bar(x + width, cong, width, label='Cong prob')
    ax.set_xticks(x)
    ax.set_xticklabels(roads)
    ax.set_ylabel('Value')
    ax.set_title('Performance metrics (final)')
    ax.legend()
    plt.tight_layout()
    plt.show()
