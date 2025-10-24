from flask import Flask, render_template, jsonify
import random, time

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data')
def data():
    data = {
        "temperatuur": round(random.uniform(15, 25), 2),
        "luchtdruk": round(random.uniform(990, 1030), 2),
        "windsnelheid": round(random.uniform(0, 25), 2),
        "windrichting": random.choice(["Noorden", "Noordoosten", "Oosten", "Zuidoosten", "Zuiden", "Zuidwesten", "Westen", "Noordwesten"]),
        "windhoek": random.randint(0, 359),
        "tijd": time.strftime("%H:%M:%S")
    }
    return jsonify(data)

if __name__ == '__main__':
    print("🌦  Server gestart op: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000)