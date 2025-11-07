from flask import Flask, render_template_string, request, jsonify
import time
import json
import os

app = Flask(__name__)
data_log = []

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ---------------------------
# HTML + CSS + JavaScript
# ---------------------------
HTML = """
<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<title>PTI Weerstation</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/justgage"></script>
<script src="https://cdn.jsdelivr.net/npm/raphael"></script>
<meta http-equiv="refresh" content="4">
<style>
body {
  font-family: 'Courier New', monospace;
  background: #555555;
  color: #d6af00;
  text-align: center;
  margin: 0;
  padding: 0;
}
header {
  background: #222;
  padding: 10px 0;
  font-size: 28px;
}
ul {
  list-style: none;
  padding: 0;
  margin: 20px auto;
  max-width: 400px;
  text-align: left;
}
li { margin: 6px 0; font-size: 18px; }
canvas {
  margin: 20px auto;
  max-width: 600px;
  width: 90%;
  display: block;
}
#gauge {
  width: 300px;
  height: 160px;
  margin: 20px auto;
}
footer {
  margin-top: 30px;
  padding: 10px;
  background: #333;
  color: #d6af00;
  font-size: 14px;
}
#kompas {
  margin: 30px auto;
  width: 150px;
  height: 150px;
  border: 5px solid #d6af00;
  border-radius: 50%;
  position: relative;
}
#pijl {
  width: 4px;
  height: 60px;
  background: #d6af00;
  position: absolute;
  top: 25px;
  left: 73px;
  transform-origin: bottom center;
  transform: rotate({{ hoek }}deg);
  transition: transform 0.5s ease;
}
</style>
</head>
<body>
<header>🌦️ PTI Weerstation</header>

{% if has_data %}
<ul>
  <li>🌡️ BME Temp: {{ temp }} °C</li>
  <li>💧 Luchtvochtigheid: {{ hum }} %</li>
  <li>📈 Luchtdruk: {{ druk }} hPa</li>
  <li>💨 Windsnelheid: {{ wind }} km/u</li>
  <li>🧭 Richting: {{ richting }} ({{ hoek }}°)</li>
  <li>🌿 Groene dakbedekking: {{ t1 }} °C</li>
  <li>🏠 Gewone dakbedekking: {{ t2 }} °C</li>
</ul>

<h3>📊 Temperatuur</h3>
<canvas id="tempChart"></canvas>

<h3>💧 Luchtvochtigheid</h3>
<canvas id="humChart"></canvas>

<h3>📈 Luchtdruk</h3>
<canvas id="drukChart"></canvas>

<h3>💨 Windsnelheid</h3>
<div id="gauge"></div>

<div id="kompas"><div id="pijl"></div></div>

{% else %}
<p>⏳ Nog geen data ontvangen...</p>
{% endif %}

<footer>© 2025 PTI Weerstation Project</footer>

<script>
{% if has_data %}
// ========== Chart.js: temperatuur ==========
new Chart(document.getElementById('tempChart'), {
  type: 'line',
  data: {
    labels: {{ labels }},
    datasets: [{
      label: 'Temperatuur (°C)',
      data: {{ temps }},
      borderColor: '#d6af00',
      tension: 0.3,
      fill: false
    }]
  },
  options: { scales: { y: { beginAtZero: false } } }
});

// ========== Chart.js: luchtvochtigheid ==========
new Chart(document.getElementById('humChart'), {
  type: 'line',
  data: {
    labels: {{ labels }},
    datasets: [{
      label: 'Luchtvochtigheid (%)',
      data: {{ hums }},
      borderColor: '#00ffff',
      tension: 0.3,
      fill: false
    }]
  },
  options: { scales: { y: { beginAtZero: true, max: 100 } } }
});

// ========== Chart.js: luchtdruk ==========
new Chart(document.getElementById('drukChart'), {
  type: 'line',
  data: {
    labels: {{ labels }},
    datasets: [{
      label: 'Luchtdruk (hPa)',
      data: {{ drukken }},
      borderColor: '#ffaa00',
      tension: 0.3,
      fill: false
    }]
  },
  options: { scales: { y: { beginAtZero: false } } }
});

// ========== JustGage: Windsnelheid ==========
var gauge = new JustGage({
  id: "gauge",
  value: {{ wind }},
  min: 0,
  max: 100,
  title: "Windsnelheid (km/u)",
  label: "km/u",
  pointer: true,
  gaugeWidthScale: 0.6,
  levelColors: ["#00ff00", "#ffff00", "#ff0000"]
});
{% endif %}
</script>
</body>
</html>
"""

# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def index():
    if data_log:
        d = data_log[-1]
        temps = [x.get("temp", 0) for x in data_log[-20:]]
        hums = [x.get("hum", 0) for x in data_log[-20:]]
        drukken = [x.get("druk", 0) for x in data_log[-20:]]
        labels = list(range(len(temps)))

        return render_template_string(
            HTML,
            has_data=True,
            temp=d.get("temp", "-"),
            hum=d.get("hum", "-"),
            druk=d.get("druk", "-"),
            wind=d.get("wind", "-"),
            richting=d.get("richting", "-"),
            hoek=d.get("hoek", 0),
            t1=d.get("ds18b20_1", "-"),
            t2=d.get("ds18b20_2", "-"),
            temps=temps,
            hums=hums,
            drukken=drukken,
            labels=labels
        )
    else:
        return render_template_string(HTML, has_data=False)

@app.route("/update", methods=["POST"])
def update():
    content = request.get_json(force=True)
    if not isinstance(content, dict):
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    content["tijd"] = time.strftime("%Y-%m-%d %H:%M:%S")
    data_log.append(content)
    if len(data_log) > 500:
        data_log.pop(0)

    # Log opslaan in bestand (dagelijks)
    filename = f"{DATA_DIR}/metingen_{time.strftime('%Y-%m-%d')}.txt"
    with open(filename, "a") as f:
        f.write(json.dumps(content) + "\n")

    print("Nieuwe data ontvangen:", content)
    return jsonify({"status": "OK"})

# ---------------------------
# Start Flask-server
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)