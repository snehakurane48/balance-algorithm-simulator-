#!/usr/bin/env python3
"""
Demo: How the Database Backend Works
Shows the workflow of storing and retrieving simulation data
"""

from my_awesome_app.database import get_session, SimulationRun, Client, RoundMetric
import datetime

def demo_database_workflow():
    """Demonstrate the complete database workflow"""

    print("🔄 DATABASE BACKEND WORKFLOW DEMO")
    print("=" * 50)

    # Step 1: Create a session
    session = get_session()
    print("✅ Connected to database")

    # Step 2: Simulate creating a simulation run (like what happens in balance_algo.py)
    print("\n📝 Step 1: Creating Simulation Run Record")
    sim_run = SimulationRun(
        timestamp=datetime.datetime.now(),
        algorithm="balance",
        num_clients=6,
        num_malicious=1,
        attack_type="sign_flip",
        num_rounds=10,
        dataset="aptos"
    )
    session.add(sim_run)
    session.commit()
    print(f"   Created run ID: {sim_run.id}")

    # Step 3: Add clients
    print("\n👥 Step 2: Adding Client Records")
    clients_data = [
        (0, False, "none"),
        (1, False, "none"),
        (2, False, "none"),
        (3, False, "none"),
        (4, False, "none"),
        (5, True, "sign_flip")  # Malicious client
    ]

    for client_id, is_mal, attack in clients_data:
        client = Client(
            simulation_run_id=sim_run.id,
            client_id=client_id,
            is_malicious=is_mal,
            attack_type=attack
        )
        session.add(client)
    session.commit()
    print(f"   Added {len(clients_data)} clients (1 malicious)")

    # Step 4: Add some sample metrics for a few rounds
    print("\n📊 Step 3: Adding Round Metrics")
    sample_metrics = [
        # Round 1
        (1, 0, 0.85, 0.0), (1, 1, 0.82, 0.0), (1, 2, 0.88, 0.0),
        (1, 3, 0.79, 0.0), (1, 4, 0.91, 0.0), (1, 5, 0.45, 0.85),  # Malicious low accuracy, high ASR
        # Round 5
        (5, 0, 0.92, 0.0), (5, 1, 0.89, 0.0), (5, 2, 0.94, 0.0),
        (5, 3, 0.86, 0.0), (5, 4, 0.96, 0.0), (5, 5, 0.52, 0.78),
    ]

    for round_num, client_id, accuracy, asr in sample_metrics:
        metric = RoundMetric(
            simulation_run_id=sim_run.id,
            client_id=client_id,
            round_number=round_num,
            eval_accuracy=accuracy,
            asr=asr,
            num_examples=100
        )
        session.add(metric)
    session.commit()
    print(f"   Added metrics for {len(sample_metrics)} client-rounds")

    # Step 5: Query and display results
    print("\n🔍 Step 4: Querying Stored Data")

    # Show run details
    run = session.query(SimulationRun).filter_by(id=sim_run.id).first()
    print(f"Run Details: {run.algorithm.upper()} | {run.num_clients} clients | {run.num_malicious} malicious | {run.attack_type}")

    # Show clients
    clients = session.query(Client).filter_by(simulation_run_id=sim_run.id).all()
    print("\nClients:")
    for client in clients:
        status = "MALICIOUS" if client.is_malicious else "SAFE"
        print(f"  Client {client.client_id}: {status} ({client.attack_type})")

    # Show metrics summary
    metrics = session.query(RoundMetric).filter_by(simulation_run_id=sim_run.id).all()
    print("\nMetrics Summary:")
    benign_metrics = [m for m in metrics if not session.query(Client).filter_by(id=m.client_id, is_malicious=True).first()]
    malicious_metrics = [m for m in metrics if session.query(Client).filter_by(id=m.client_id, is_malicious=True).first()]

    if benign_metrics:
        avg_benign_acc = sum(m.eval_accuracy for m in benign_metrics) / len(benign_metrics)
        print(f"Average Benign Accuracy: {avg_benign_acc:.3f}")
    if malicious_metrics:
        avg_mal_asr = sum(m.asr for m in malicious_metrics) / len(malicious_metrics)
        print(f"Average Malicious ASR: {avg_mal_asr:.3f}")

    print("\n✅ Database workflow complete!")
    print("💾 Data is now stored in simulation_results.db")

    # Cleanup demo data
    session.query(RoundMetric).filter_by(simulation_run_id=sim_run.id).delete()
    session.query(Client).filter_by(simulation_run_id=sim_run.id).delete()
    session.query(SimulationRun).filter_by(id=sim_run.id).delete()
    session.commit()
    print("🧹 Cleaned up demo data")

if __name__ == "__main__":
    demo_database_workflow()