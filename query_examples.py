#!/usr/bin/env python3
"""
Database Query Examples
Demonstrates how to query the simulation database
"""

from my_awesome_app.database import get_session, SimulationRun, Client, RoundMetric
import pandas as pd

def show_recent_runs():
    """Show recent simulation runs"""
    session = get_session()
    runs = session.query(SimulationRun).order_by(SimulationRun.timestamp.desc()).limit(5).all()

    print("Recent Simulation Runs:")
    print("-" * 80)
    for run in runs:
        print(f"ID: {run.id}")
        print(f"  Algorithm: {run.algorithm.upper()}")
        print(f"  Clients: {run.num_clients} (Malicious: {run.num_malicious})")
        print(f"  Attack: {run.attack_type}")
        print(f"  Rounds: {run.num_rounds}")
        print(f"  Time: {run.timestamp}")
        print()

def analyze_algorithm_performance():
    """Compare different algorithms"""
    session = get_session()

    # Get average accuracy by algorithm
    results = session.query(
        SimulationRun.algorithm,
        RoundMetric.eval_accuracy
    ).join(RoundMetric).filter(
        Client.is_malicious == False  # Only benign clients
    ).join(Client).all()

    df = pd.DataFrame(results, columns=['algorithm', 'accuracy'])
    avg_by_algo = df.groupby('algorithm')['accuracy'].mean()

    print("Average Benign Client Accuracy by Algorithm:")
    print("-" * 50)
    for algo, acc in avg_by_algo.items():
        print(f"{algo.upper()}: {acc:.3f}")

def show_malicious_client_details(run_id=None):
    """Show details of malicious clients in a run"""
    session = get_session()

    if run_id is None:
        # Get latest run
        latest = session.query(SimulationRun).order_by(SimulationRun.timestamp.desc()).first()
        run_id = latest.id

    malicious_clients = session.query(Client).filter_by(
        simulation_run_id=run_id,
        is_malicious=True
    ).all()

    print(f"Malicious Clients in Run {run_id}:")
    print("-" * 40)
    for client in malicious_clients:
        print(f"Client {client.client_id}: {client.attack_type}")

def get_run_metrics(run_id):
    """Get all metrics for a specific run"""
    session = get_session()

    metrics = session.query(RoundMetric).filter_by(simulation_run_id=run_id).all()

    # Convert to DataFrame for analysis
    data = []
    for m in metrics:
        data.append({
            'round': m.round_number,
            'client_id': m.client_id,
            'accuracy': m.eval_accuracy,
            'asr': m.asr
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    show_recent_runs()
    print()
    analyze_algorithm_performance()
    print()
    show_malicious_client_details()