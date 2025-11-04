from flask import Flask, render_template_string, request, jsonify
import time

app = Flask(__name__)

data_log = []

HTML = """
<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<title>PTI Weerstation</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<meta http-equiv="refresh" content="2">
<style>
{{style}}
</style>
</head>
<body>
<header>
  <div class="wrapper">
    <div class="logo"><img src="https://via.placeholder.com/100x60.png?text=PTI" alt="logo"></div>
    <nav>
      <a href="#">Home</a><a href="#">Weerdata</a><a href="#">Over</a>
    </nav>
  </div>
</header>

<div class="banner"><h2>PTI Weerstation</h2></div>

<div class="content-I">
  <div class="tekst-I">
    <h2>Live Data</h2>
    <ul>
      <li>🌡️ BME Temp: {{temp}} °C</li>
      <li>💧 Luchtvochtigheid: {{hum}} %</li>
      <li>📈 Luchtdruk: {{druk}} hPa</li>
      <li>💨 Windsnelheid: {{wind}} km/u</li>
      <li>🧭 Richting: {{richting}} ({{hoek}}°)</li>
      <li>🌡️ DS18B20 #1: {{t1}} °C</li>
      <li>🌡️ DS18B20 #2: {{t2}} °C</li>
    </ul>
    <canvas id="grafiek" height="120"></canvas>
    <div id="kompas">
      <div id="pijl" style="transform: rotate({{hoek}}deg);"></div>
    </div>
  </div>
</div>

<script>
const ctx = document.getElementById('grafiek').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: {{labels}},
    datasets: [{
      label: 'Temperatuur (°C)',
      data: {{temps}},
      borderColor: '#d6af00'
    }]
  },
  options: {scales: {y: {beginAtZero: false}}}
});
</script>
</body>
</html>
"""

style = """/* kleurenpalet pti #555555 #d6af00*/
*{margin:0;padding:0;}
body{font-family:'Courier New',monospace;background:#555555;color:#d6af00;}
header{width:100%;height:80px;background:#555555;position:fixed;}
.wrapper{width:90%;margin:0 auto;}
.logo img{height:60px;}
nav{float:right;line-height:80px;}
nav a{text-decoration:none;padding:0 20px;color:#d6af00;font-size:30px;}
nav a:hover{background:#d6af00;color:#555555;}
.banner{background:#222;height:200px;text-align:center;padding-top:40px;}
#kompas{margin:20px auto;width:150px;height:150px;border:5px solid #d6af00;border-radius:50%;position:relative;}
#pijl{width:4px;height:60px;background:#d6af00;position:absolute;top:25px;left:73px;transform-origin:bottom center;}
"""

@app.route("/")
def index():
    if data_log:
        d = data_log[-1]
        temps = [d["bme_temp"] for d in data_log[-10:]]
        labels = [i for i in range(len(temps))]
        return render_template_string(
            HTML,
            style=style,
            temp=d["bme_temp"],
            hum=d["hum"],
            druk=d["druk"],
            wind=d["wind"],
            richting=d["richting"],
            hoek=d["hoek"],
            t1=d["ds18b20_1"],
            t2=d["ds18b20_2"],
            temps=temps,
            labels=labels
        )
    else:
        return "Nog geen data ontvangen."

@app.route("/update", methods=["POST"])
def update():
    content = request.get_json()
    content["tijd"] = time.time()
    data_log.append(content)
    if len(data_log) > 100:
        data_log.pop(0)
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)