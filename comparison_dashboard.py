#!/usr/bin/env python3
"""
Comparative Dashboard: Compare all aggregation methods vs BALANCE
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from my_awesome_app.database import get_session, SimulationRun, Client, RoundMetric
import subprocess
import time

def run_comparison_simulations():
    """Run simulations with different aggregation methods"""
    print("🚀 Running comparative simulations...")

    methods = ['balance', 'fedavg', 'trim', 'median', 'krum']
    num_clients = 6
    num_malicious = 1
    attack_type = 'sign_flip'
    rounds = 10

    for method in methods:
        print(f"Running {method.upper()}...")
        cmd = [
            'python', 'my_awesome_app/balance_algo.py',
            '--num_clients', str(num_clients),
            '--rounds', str(rounds),
            '--malicious', str(num_malicious),
            '--attack', attack_type,
            '--agg', method
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error running {method}: {result.stderr}")
        else:
            print(f"✅ {method.upper()} completed")

        time.sleep(1)  # Brief pause between runs

def get_comparison_data():
    """Get data for all recent runs with different methods"""
    session = get_session()

    # Get the most recent runs (assuming they were just run)
    runs = session.query(SimulationRun).order_by(SimulationRun.timestamp.desc()).limit(5).all()

    data = {}
    for run in runs:
        # Get metrics for this run
        metrics = session.query(RoundMetric).filter_by(simulation_run_id=run.id).all()

        # Group by round
        rounds_data = {}
        for metric in metrics:
            round_num = metric.round_number
            if round_num not in rounds_data:
                rounds_data[round_num] = {'accuracies': [], 'asrs': []}

            rounds_data[round_num]['accuracies'].append(metric.eval_accuracy)
            rounds_data[round_num]['asrs'].append(metric.asr)

        # Calculate averages per round
        avg_accuracy_per_round = []
        avg_asr_per_round = []
        rounds_list = sorted(rounds_data.keys())

        for round_num in rounds_list:
            accuracies = rounds_data[round_num]['accuracies']
            asrs = rounds_data[round_num]['asrs']

            avg_accuracy_per_round.append(np.mean(accuracies))
            avg_asr_per_round.append(np.mean(asrs))

        data[run.algorithm] = {
            'rounds': rounds_list,
            'avg_accuracy': avg_accuracy_per_round,
            'avg_asr': avg_asr_per_round
        }

    return data

def create_comparison_dashboard():
    """Create comparative dashboard plots"""
    data = get_comparison_data()

    if not data:
        print("❌ No data found. Run simulations first!")
        return

    # Color scheme for different methods
    colors = {
        'balance': '#1f77b4',  # Blue
        'fedavg': '#ff7f0e',   # Orange
        'trim': '#2ca02c',     # Green
        'median': '#d62728',   # Red
        'krum': '#9467bd'      # Purple
    }

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Federated Learning Aggregation Methods Comparison\n(BALANCE vs Others)', fontsize=16, fontweight='bold')

    # Plot 1: Average Accuracy Over Rounds
    ax1 = axes[0, 0]
    for method, method_data in data.items():
        ax1.plot(method_data['rounds'], method_data['avg_accuracy'],
                label=method.upper(), color=colors.get(method, 'black'),
                linewidth=2, marker='o', markersize=4)

    ax1.set_title('Average Accuracy Over Rounds', fontweight='bold')
    ax1.set_xlabel('Round')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Average Attack Success Rate Over Rounds
    ax2 = axes[0, 1]
    for method, method_data in data.items():
        ax2.plot(method_data['rounds'], method_data['avg_asr'],
                label=method.upper(), color=colors.get(method, 'black'),
                linewidth=2, marker='s', markersize=4)

    ax2.set_title('Attack Success Rate Over Rounds', fontweight='bold')
    ax2.set_xlabel('Round')
    ax2.set_ylabel('ASR')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Final Accuracy Comparison (Bar chart)
    ax3 = axes[1, 0]
    methods = list(data.keys())
    final_accuracies = [data[m]['avg_accuracy'][-1] for m in methods]

    bars = ax3.bar(methods, final_accuracies, color=[colors.get(m, 'gray') for m in methods])
    ax3.set_title('Final Round Accuracy Comparison', fontweight='bold')
    ax3.set_ylabel('Final Accuracy')
    ax3.set_xlabel('Aggregation Method')

    # Add value labels on bars
    for bar, value in zip(bars, final_accuracies):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                '.3f', ha='center', va='bottom', fontweight='bold')

    # Plot 4: Final ASR Comparison (Bar chart)
    ax4 = axes[1, 1]
    final_asrs = [data[m]['avg_asr'][-1] for m in methods]

    bars = ax4.bar(methods, final_asrs, color=[colors.get(m, 'gray') for m in methods])
    ax4.set_title('Final Round Attack Success Rate', fontweight='bold')
    ax4.set_ylabel('Final ASR')
    ax4.set_xlabel('Aggregation Method')

    # Add value labels on bars
    for bar, value in zip(bars, final_asrs):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                '.3f', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()

    # Save the dashboard
    os.makedirs('comparison_dashboard', exist_ok=True)
    plt.savefig('comparison_dashboard/aggregation_comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig('comparison_dashboard/aggregation_comparison.pdf', bbox_inches='tight')

    print("✅ Comparative dashboard saved to: comparison_dashboard/aggregation_comparison.png")

    # Show summary table
    print("\n📊 PERFORMANCE SUMMARY:")
    print("-" * 60)
    print("<12")
    print("-" * 60)
    for method in methods:
        final_acc = data[method]['avg_accuracy'][-1]
        final_asr = data[method]['avg_asr'][-1]
        print("<12")

    # Find best performers
    best_accuracy = max(final_accuracies)
    best_asr_defense = min(final_asrs)  # Lower ASR is better

    best_acc_method = methods[final_accuracies.index(best_accuracy)]
    best_defense_method = methods[final_asrs.index(best_asr_defense)]

    print("-" * 60)
    print(f"🏆 Best Accuracy: {best_acc_method.upper()} ({best_accuracy:.3f})")
    print(f"🛡️  Best Defense: {best_defense_method.upper()} (ASR: {best_asr_defense:.3f})")

def main():
    """Main function"""
    print("🔄 AGGREGATION METHODS COMPARISON DASHBOARD")
    print("=" * 50)

    # Ask user if they want to run new simulations
    response = input("Run new simulations with all methods? (y/n): ").lower().strip()

    if response == 'y':
        run_comparison_simulations()

    # Create dashboard
    create_comparison_dashboard()

if __name__ == "__main__":
    main()