let charts = {};
let updateCount = 0;

function initCharts() {
    const tempCtx = document.getElementById('tempChart').getContext('2d');
    const vibCtx = document.getElementById('vibrationChart').getContext('2d');

    charts.temp = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'МНА-21',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'МНА-22',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 40,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });

    charts.vibration = new Chart(vibCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'МНА-21',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'МНА-22',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

async function updateInterface() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        const container = document.getElementById('aggregates');
        if (container) {
            container.innerHTML = '';
        }

        const now = new Date().toLocaleTimeString();

        for (const [id, agg] of Object.entries(data)) {
            if (container) {
                const card = createAggregateCard(id, agg);
                container.appendChild(card);
            }

            updateCharts(id, agg, now);
        }

        updateCount++;
    } catch (error) {
        console.error('Ошибка получения данных:', error);
    }
}

function createAggregateCard(id, agg) {
    const card = document.createElement('div');
    card.className = 'aggregate-card';

    let statusClass = '';
    switch(agg.status) {
        case 'ОСН': statusClass = 'status-ОСН'; break;
        case 'П': statusClass = 'status-П'; break;
        case 'ОСТ': statusClass = 'status-ОСТ'; break;
        case 'ГОТОВ': statusClass = 'status-ГОТОВ'; break;
        default: statusClass = '';
    }

    card.innerHTML = `
        <div class="aggregate-header">
            <span class="aggregate-id">${id}</span>
            <span class="status-badge ${statusClass}">${agg.status}</span>
        </div>
        <div class="parameters">
            <div class="parameter">
                <div class="parameter-label">Давление</div>
                <div class="parameter-value">${agg.pressure_outlet} <span class="parameter-unit">МПа</span></div>
            </div>
            <div class="parameter">
                <div class="parameter-label">Температура</div>
                <div class="parameter-value">${agg.temp_bearing} <span class="parameter-unit">°C</span></div>
            </div>
            <div class="parameter">
                <div class="parameter-label">Вибрация</div>
                <div class="parameter-value">${agg.vibration} <span class="parameter-unit">мм/с</span></div>
            </div>
            <div class="parameter">
                <div class="parameter-label">Расход</div>
                <div class="parameter-value">${agg.flow_rate} <span class="parameter-unit">м³/с</span></div>
            </div>
            <div class="parameter">
                <div class="parameter-label">Мощность</div>
                <div class="parameter-value">${agg.power} <span class="parameter-unit">кВт</span></div>
            </div>
            <div class="parameter">
                <div class="parameter-label">Health</div>
                <div class="parameter-value">${agg.health_score} <span class="parameter-unit">%</span></div>
            </div>
        </div>
        <div style="margin-top: 15px; display: flex; gap: 10px;">
            <button onclick="startAggregate('${id}')" class="btn btn-success" style="flex: 1;">Старт</button>
            <button onclick="stopAggregate('${id}')" class="btn btn-danger" style="flex: 1;">Стоп</button>
        </div>
    `;

    return card;
}

function updateCharts(id, agg, timestamp) {
    if (!charts.temp || !charts.vibration) return;

    if (charts.temp.data.labels.length > 20) {
        charts.temp.data.labels.shift();
        charts.vibration.data.labels.shift();

        charts.temp.data.datasets.forEach(dataset => {
            if (dataset.data.length > 20) dataset.data.shift();
        });

        charts.vibration.data.datasets.forEach(dataset => {
            if (dataset.data.length > 20) dataset.data.shift();
        });
    }

    charts.temp.data.labels.push(timestamp);
    charts.vibration.data.labels.push(timestamp);

    const tempDataset = charts.temp.data.datasets.find(d => d.label === id);
    const vibDataset = charts.vibration.data.datasets.find(d => d.label === id);

    if (tempDataset) {
        tempDataset.data.push(agg.temp_bearing);
    }

    if (vibDataset) {
        vibDataset.data.push(agg.vibration);
    }

    charts.temp.update('none');
    charts.vibration.update('none');
}

async function startAggregate(id) {
    await fetch(`/api/start/${id}`, { method: 'POST' });
}

async function stopAggregate(id) {
    await fetch(`/api/stop/${id}`, { method: 'POST' });
}

async function startAll() {
    for (const id of ['МНА-21', 'МНА-22', 'МНА-23', 'МНА-24']) {
        await startAggregate(id);
    }
}

async function stopAll() {
    for (const id of ['МНА-21', 'МНА-22', 'МНА-23', 'МНА-24']) {
        await stopAggregate(id);
    }
}

async function simulateAnomaly() {
    await fetch('/api/anomaly/МНА-21/overheating', { method: 'POST' });
}

window.onload = function() {
    initCharts();
    updateInterface();
    setInterval(updateInterface, 2000);
};