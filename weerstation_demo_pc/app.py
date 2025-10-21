from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data')
def data():
    # Simuleer live weerdata
    return jsonify({
        "temperature": random.uniform(15, 30),
        "pressure": random.uniform(720, 760),
        "wind_speed": random.uniform(0, 50),
        "wind_direction": random.choice(["Noorden", "Oosten", "Zuiden", "Westen", "Noordoosten", "Zuidwesten"])
    })

if __name__ == '__main__':
    print("Server gestart op: http://127.0.0.1:5000")
    app.run(debug=True)