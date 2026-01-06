document.getElementById('config-form').addEventListener('submit', function(e) {
    e.preventDefault();
    runSimulation();
});

let terChart, asrChart, consensusChart;

function initCharts() {
    if (typeof Chart === 'undefined') {
        alert('Chart.js library not loaded. Please check your internet connection.');
        return;
    }
    const ctxTer = document.getElementById('ter-chart').getContext('2d');
    terChart = new Chart(ctxTer, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'BALANCE',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }, {
                label: 'Comparison',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Max TER vs Rounds'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    const ctxAsr = document.getElementById('asr-chart').getContext('2d');
    asrChart = new Chart(ctxAsr, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'BALANCE',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }, {
                label: 'Comparison',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Max ASR vs Rounds'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    const ctxConsensus = document.getElementById('consensus-chart').getContext('2d');
    consensusChart = new Chart(ctxConsensus, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'BALANCE',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }, {
                label: 'Comparison',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Consensus Error vs Rounds'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function runSimulation() {
    const button = document.getElementById('run-button');
    button.disabled = true;
    button.textContent = 'Running Simulation...';

    const numClients = document.getElementById('num_clients').value;
    const maliciousPct = document.getElementById('malicious_pct').value;
    const attackType = document.getElementById('attack_type').value;
    const comparisonAgg = document.getElementById('comparison_agg').value;

    const data = {
        num_clients: numClients,
        malicious_pct: maliciousPct,
        attack_type: attackType,
        comparison_agg: comparisonAgg
    };

    fetch('/run_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data received:', data);
        try {
            updateNetworkView(data);
            updateCharts(data);
            updateResultsTable(data);
        } catch (e) {
            console.error('Error updating UI:', e);
            alert('Error updating interface: ' + e.message);
        }
        button.disabled = false;
        button.textContent = 'Run Simulation';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error running simulation. Check console for details.');
        button.disabled = false;
        button.textContent = 'Run Simulation';
    });
}

function updateNetworkView(data) {
    const canvas = document.getElementById('network-canvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 100;
    const numClients = data.client_ids.length;

    for (let i = 0; i < numClients; i++) {
        const angle = (i / numClients) * 2 * Math.PI - Math.PI / 2;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);

        // Draw node
        ctx.beginPath();
        ctx.arc(x, y, 20, 0, 2 * Math.PI);
        ctx.fillStyle = data.true_labels[i] === 'malicious' ? 'red' : 'green';
        ctx.fill();
        ctx.strokeStyle = data.detected_labels[i] !== data.true_labels[i] ? 'yellow' : 'black';
        ctx.lineWidth = 3;
        ctx.stroke();

        // Draw label
        ctx.fillStyle = 'black';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(data.client_ids[i].toString(), x, y + 4);
    }

    // Draw connections (simple ring)
    for (let i = 0; i < numClients; i++) {
        const angle1 = (i / numClients) * 2 * Math.PI - Math.PI / 2;
        const x1 = centerX + radius * Math.cos(angle1);
        const y1 = centerY + radius * Math.sin(angle1);

        const next = (i + 1) % numClients;
        const angle2 = (next / numClients) * 2 * Math.PI - Math.PI / 2;
        const x2 = centerX + radius * Math.cos(angle2);
        const y2 = centerY + radius * Math.sin(angle2);

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = 'gray';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
}

function updateCharts(data) {
    const rounds = data.rounds.map(r => `Round ${r}`);

    terChart.data.labels = rounds;
    terChart.data.datasets[0].data = data.balance_metrics.max_TER;
    terChart.data.datasets[1].data = data.comparison_metrics.max_TER;
    terChart.update();

    asrChart.data.labels = rounds;
    asrChart.data.datasets[0].data = data.balance_metrics.max_ASR;
    asrChart.data.datasets[1].data = data.comparison_metrics.max_ASR;
    asrChart.update();

    consensusChart.data.labels = rounds;
    consensusChart.data.datasets[0].data = data.balance_metrics.consensus_error;
    consensusChart.data.datasets[1].data = data.comparison_metrics.consensus_error;
    consensusChart.update();
}

function updateResultsTable(data) {
    const tbody = document.querySelector('#results-table tbody');
    tbody.innerHTML = '';

    for (let i = 0; i < data.client_ids.length; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${data.client_ids[i]}</td>
            <td>${data.true_labels[i]}</td>
            <td>${data.detected_labels[i]}</td>
            <td>${data.attack_types[i]}</td>
        `;
        tbody.appendChild(row);
    }
}

initCharts();