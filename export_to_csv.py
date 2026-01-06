#!/usr/bin/env python3
"""
Database to CSV Export Utility
Exports database tables to CSV files for analysis
"""

import csv
import os
from my_awesome_app.database import get_session, SimulationRun, Client, RoundMetric

def export_simulation_runs_to_csv(filename="simulation_runs.csv"):
    """Export simulation_runs table to CSV"""
    session = get_session()
    runs = session.query(SimulationRun).all()

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['id', 'timestamp', 'algorithm', 'num_clients', 'num_malicious', 'attack_type', 'num_rounds', 'dataset']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for run in runs:
            writer.writerow({
                'id': run.id,
                'timestamp': run.timestamp,
                'algorithm': run.algorithm,
                'num_clients': run.num_clients,
                'num_malicious': run.num_malicious,
                'attack_type': run.attack_type,
                'num_rounds': run.num_rounds,
                'dataset': run.dataset
            })
    print(f"Exported {len(runs)} simulation runs to {filename}")

def export_clients_to_csv(filename="clients.csv"):
    """Export clients table to CSV"""
    session = get_session()
    clients = session.query(Client).all()

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['id', 'simulation_run_id', 'client_id', 'is_malicious', 'attack_type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for client in clients:
            writer.writerow({
                'id': client.id,
                'simulation_run_id': client.simulation_run_id,
                'client_id': client.client_id,
                'is_malicious': client.is_malicious,
                'attack_type': client.attack_type
            })
    print(f"Exported {len(clients)} clients to {filename}")

def export_metrics_to_csv(filename="round_metrics.csv"):
    """Export round_metrics table to CSV"""
    session = get_session()
    metrics = session.query(RoundMetric).all()

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['id', 'simulation_run_id', 'client_id', 'round_number', 'train_loss', 'eval_loss', 'eval_accuracy', 'num_examples', 'asr']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for metric in metrics:
            writer.writerow({
                'id': metric.id,
                'simulation_run_id': metric.simulation_run_id,
                'client_id': metric.client_id,
                'round_number': metric.round_number,
                'train_loss': metric.train_loss,
                'eval_loss': metric.eval_loss,
                'eval_accuracy': metric.eval_accuracy,
                'num_examples': metric.num_examples,
                'asr': metric.asr
            })
    print(f"Exported {len(metrics)} metrics to {filename}")

def export_run_summary_to_csv(run_id, output_dir="csv_exports"):
    """Export a complete run summary to CSV (similar to existing format)"""
    os.makedirs(output_dir, exist_ok=True)

    session = get_session()
    run = session.query(SimulationRun).filter_by(id=run_id).first()
    if not run:
        print(f"Run {run_id} not found")
        return

    # Export per-client accuracy over rounds
    clients = session.query(Client).filter_by(simulation_run_id=run_id).all()
    client_ids = sorted([c.client_id for c in clients])

    # Get all rounds
    rounds = sorted(list(set([m.round_number for m in session.query(RoundMetric).filter_by(simulation_run_id=run_id).all()])))

    # Create accuracy matrix
    accuracy_data = []
    for round_num in rounds:
        row = [round_num]
        for client_id in client_ids:
            client_db_id = session.query(Client).filter_by(simulation_run_id=run_id, client_id=client_id).first().id
            metric = session.query(RoundMetric).filter_by(simulation_run_id=run_id, client_id=client_db_id, round_number=round_num).first()
            accuracy = metric.eval_accuracy if metric else 0.0
            row.append(accuracy)
        accuracy_data.append(row)

    # Save accuracy CSV
    acc_filename = os.path.join(output_dir, f"per_client_accuracy_{run.algorithm}_clients{run.num_clients}_atk{run.attack_type}.csv")
    with open(acc_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ["round"] + [f"client_{cid}" for cid in client_ids]
        writer.writerow(header)
        writer.writerows(accuracy_data)
    print(f"Saved per-client accuracy to {acc_filename}")

    # Export ASR data
    asr_data = []
    for round_num in rounds:
        row = [round_num]
        for client_id in client_ids:
            client_db_id = session.query(Client).filter_by(simulation_run_id=run_id, client_id=client_id).first().id
            metric = session.query(RoundMetric).filter_by(simulation_run_id=run_id, client_id=client_db_id, round_number=round_num).first()
            asr = metric.asr if metric else 0.0
            row.append(asr)
        asr_data.append(row)

    asr_filename = os.path.join(output_dir, f"asr_per_client_{run.algorithm}_clients{run.num_clients}_atk{run.attack_type}.csv")
    with open(asr_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ["round"] + [f"client_{cid}" for cid in client_ids]
        writer.writerow(header)
        writer.writerows(asr_data)
    print(f"Saved ASR data to {asr_filename}")

def export_all_to_csv():
    """Export all database tables to CSV files"""
    export_simulation_runs_to_csv()
    export_clients_to_csv()
    export_metrics_to_csv()

    # Export individual run summaries
    session = get_session()
    runs = session.query(SimulationRun).all()
    for run in runs:
        export_run_summary_to_csv(run.id)

if __name__ == "__main__":
    print("Exporting database to CSV files...")
    export_all_to_csv()
    print("Export complete!")