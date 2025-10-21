# weerstation_demo_pc.py
# Demo van een lokaal weerstation-dashboard (zonder Pico)
# Draait op je pc, opent een website met live gesimuleerde data

from flask import Flask, render_template, jsonify
import random, time

app = Flask(__name__)
# ---------------------------
# Server-routes
# ---------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data')
def get_data():
    data = {
        "temp": random.uniform(18.0, 26.0),
        "pressure": random.uniform(730.0, 760.0),
        "wind_speed": random.uniform(0.0, 20.0),
        "wind_dir": random.choice(["Noorden", "Oosten", "Zuiden", "Westen", "NO", "ZW"])
    }
    return jsonify(data)

if __name__ == '__main__':
    print("Server gestart op: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000)
