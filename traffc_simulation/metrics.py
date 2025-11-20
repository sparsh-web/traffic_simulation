# metrics.py
import pandas as pd
import numpy as np

class MetricsCollector:
    """
    Collect snapshots and compute final metrics:
    - average queue length over time
    - average waiting time per passed vehicle
    - congestion probability (fraction of time queue > threshold)
    """
    def __init__(self, roads):
        self.roads = roads
        self.snapshots = []  # list of DataFrame-like dicts

    def take_snapshot(self, now):
        recs = []
        for r in self.roads:
            recs.append({
                'time': now,
                'road': r.name,
                'queue_length': r.queue_length(),
                'passed_count': len(r.passed)
            })
        self.snapshots.append(pd.DataFrame(recs))

    def snapshots_df(self):
        if not self.snapshots:
            return pd.DataFrame(columns=['time','road','queue_length','passed_count'])
        return pd.concat(self.snapshots, ignore_index=True)

    def final_stats(self):
        rows = []
        for r in self.roads:
            total_passed = len(r.passed)
            waits = [v.wait_time() for v in r.passed if v.wait_time() is not None]
            avg_wait = float(np.mean(waits)) if waits else float('nan')
            # average queue length over snapshots for this road
            df = self.snapshots_df()
            sub = df[df['road'] == r.name]
            avg_q = float(sub['queue_length'].mean()) if not sub.empty else 0.0
            rows.append({
                'road': r.name,
                'total_passed': total_passed,
                'avg_wait_time': avg_wait,
                'avg_queue_length': avg_q
            })
        return pd.DataFrame(rows)

    def congestion_probability(self, threshold=10):
        df = self.snapshots_df()
        if df.empty:
            return {}
        probs = {}
        for rname in df['road'].unique():
            sub = df[df['road'] == rname]
            probs[rname] = float((sub['queue_length'] > threshold).mean())
        return probs
