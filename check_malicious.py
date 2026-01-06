#!/usr/bin/env python3
"""
Check which clients are malicious after simulation runs
"""

from my_awesome_app.database import get_session, SimulationRun, Client, RoundMetric

def check_malicious_clients(run_id=None):
    """Check which clients are malicious in a simulation run"""
    session = get_session()

    if run_id is None:
        # Get latest run
        latest = session.query(SimulationRun).order_by(SimulationRun.timestamp.desc()).first()
        run_id = latest.id

    print(f"🔍 MALICIOUS CLIENT DETECTION - Run {run_id}")
    print("=" * 50)

    # Get run info
    run = session.query(SimulationRun).filter_by(id=run_id).first()
    print(f"Algorithm: {run.algorithm.upper()}")
    print(f"Total Clients: {run.num_clients}")
    print(f"Malicious Clients: {run.num_malicious}")
    print(f"Attack Type: {run.attack_type}")
    print()

    # Get all clients and their metrics
    clients = session.query(Client).filter_by(simulation_run_id=run_id).all()

    print("CLIENT ANALYSIS:")
    print("-" * 70)
    print("Client ID | Status     | Attack Type | Avg Accuracy | Avg ASR")
    print("-" * 70)

    for client in clients:
        # Get metrics for this client
        metrics = session.query(RoundMetric).filter_by(
            simulation_run_id=run_id,
            client_id=client.id
        ).all()

        if metrics:
            avg_accuracy = sum(m.eval_accuracy for m in metrics) / len(metrics)
            avg_asr = sum(m.asr for m in metrics) / len(metrics)
        else:
            avg_accuracy = 0.0
            avg_asr = 0.0

        status = "MALICIOUS" if client.is_malicious else "SAFE"
        attack = client.attack_type if client.attack_type != "none" else "-"

        print(f"{client.client_id:>9} | {status:<10} | {attack:<11} | {avg_accuracy:>12.3f} | {avg_asr:>7.3f}")

    print()
    print("📊 SUMMARY:")
    malicious = [c for c in clients if c.is_malicious]
    if malicious:
        print(f"🚨 Malicious clients detected: {', '.join(str(c.client_id) for c in malicious)}")
        print(f"   Attack method: {malicious[0].attack_type}")
    else:
        print("✅ No malicious clients detected")

def check_latest_run():
    """Check the most recent simulation run"""
    check_malicious_clients()

if __name__ == "__main__":
    check_latest_run()