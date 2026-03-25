from flask import Flask, render_template, jsonify
from main import MainPumpStationEmulator
import threading
import time
import random

app = Flask(__name__)

emulator = MainPumpStationEmulator()

def run_emulator():
    # НЕ запускаем автоматически - пользователь управляет сам
    while True:
        for agg_id in emulator.aggregates:
            agg = emulator.aggregates[agg_id]
            if agg.status.value in ["ОСН", "П"]:
                # Небольшие случайные изменения параметров
                agg.temp_bearing_front += random.uniform(-0.3, 0.3)
                agg.vibration_horizontal += random.uniform(-0.05, 0.05)
                agg.pressure_outlet += random.uniform(-0.01, 0.01)
        time.sleep(1)

emulator_thread = threading.Thread(target=run_emulator, daemon=True)
emulator_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    data = {}
    for agg_id, agg in emulator.aggregates.items():
        data[agg_id] = {
            'status': agg.status.value,
            'pressure_inlet': round(agg.pressure_inlet, 3),
            'pressure_outlet': round(agg.pressure_outlet, 3),
            'temp_bearing': round(agg.temp_bearing_front, 1),
            'vibration': round(agg.vibration_horizontal, 2),
            'flow_rate': round(agg.flow_rate, 3),
            'power': round(agg.power, 1),
            'health_score': round(agg.health_score, 1)
        }
    return jsonify(data)

@app.route('/api/anomaly/<aggregate_id>/<anomaly_type>', methods=['POST'])
def trigger_anomaly(aggregate_id, anomaly_type):
    emulator.simulate_anomaly(aggregate_id, anomaly_type)
    return jsonify({'status': 'ok'})

@app.route('/api/start/<aggregate_id>', methods=['POST'])
def start_aggregate(aggregate_id):
    result = emulator.start_aggregate(aggregate_id)
    return jsonify({'status': 'ok' if result else 'error'})

@app.route('/api/stop/<aggregate_id>', methods=['POST'])
def stop_aggregate(aggregate_id):
    result = emulator.stop_aggregate(aggregate_id)
    return jsonify({'status': 'ok' if result else 'error'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)