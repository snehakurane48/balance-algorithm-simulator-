from flask import Flask, request, jsonify, render_template
from my_awesome_app.balance_algo import simulate
from my_awesome_app.database import get_session, SimulationRun, Client, RoundMetric
import time

app = Flask(__name__)

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.json
    num_clients = int(data['num_clients'])
    malicious_pct = float(data['malicious_pct'])
    num_malicious = int(num_clients * malicious_pct / 100)
    attack_type = data['attack_type']
    comparison_agg = data['comparison_agg']

    # Run BALANCE simulation
    simulate(num_clients=num_clients, rounds=3, num_malicious=num_malicious, attack_type=attack_type, agg='balance', debug_size=100)
    time.sleep(1)  # Brief pause

    # Run comparison simulation
    simulate(num_clients=num_clients, rounds=3, num_malicious=num_malicious, attack_type=attack_type, agg=comparison_agg, debug_size=100)

    # Query database for the latest two runs
    session = get_session()
    runs = session.query(SimulationRun).order_by(SimulationRun.timestamp.desc()).limit(2).all()
    balance_run = runs[1] if len(runs) > 1 else runs[0]
    comp_run = runs[0]

    # Get clients (assume same for both runs)
    clients = session.query(Client).filter_by(simulation_run_id=balance_run.id).all()
    client_ids = [c.client_id for c in clients]
    true_labels = ['malicious' if c.is_malicious else 'benign' for c in clients]
    detected_labels = true_labels  # Placeholder: assume detected same as true for visualization
    attack_types = [c.attack_type for c in clients]

    # Get metrics for BALANCE
    metrics_balance = session.query(RoundMetric).filter_by(simulation_run_id=balance_run.id).all()
    rounds = sorted(set(m.round_number for m in metrics_balance))

    max_ter_balance = []
    max_asr_balance = []
    consensus_balance = []  # Placeholder, as not stored in DB

    for r in rounds:
        round_metrics = [m for m in metrics_balance if m.round_number == r]
        benign_metrics = [m for m in round_metrics if not session.query(Client).filter_by(id=m.client_id).first().is_malicious]
        max_ter = max((1 - m.eval_accuracy) for m in benign_metrics) if benign_metrics else 0
        max_ter_balance.append(max_ter)
        max_asr = max(m.asr for m in round_metrics) if round_metrics else 0
        max_asr_balance.append(max_asr)
        consensus_balance.append(0.0)  # Placeholder

    # Get metrics for comparison
    metrics_comp = session.query(RoundMetric).filter_by(simulation_run_id=comp_run.id).all()
    max_ter_comp = []
    max_asr_comp = []
    consensus_comp = []

    for r in rounds:
        round_metrics = [m for m in metrics_comp if m.round_number == r]
        benign_metrics = [m for m in round_metrics if not session.query(Client).filter_by(id=m.client_id).first().is_malicious]
        max_ter = max((1 - m.eval_accuracy) for m in benign_metrics) if benign_metrics else 0
        max_ter_comp.append(max_ter)
        max_asr = max(m.asr for m in round_metrics) if round_metrics else 0
        max_asr_comp.append(max_asr)
        consensus_comp.append(0.0)

    return jsonify({
        'client_ids': client_ids,
        'true_labels': true_labels,
        'detected_labels': detected_labels,
        'attack_types': attack_types,
        'rounds': rounds,
        'balance_metrics': {
            'max_TER': max_ter_balance,
            'max_ASR': max_asr_balance,
            'consensus_error': consensus_balance
        },
        'comparison_metrics': {
            'max_TER': max_ter_comp,
            'max_ASR': max_asr_comp,
            'consensus_error': consensus_comp
        }
    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)