from flask import Flask, render_template_string, request, jsonify
import time

app = Flask(__name__)

data_log = []

# ----------------------------------
# HTML-template (inclusief CSS + JS)
# ----------------------------------
HTML = """
<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<title>PTI Weerstation</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<meta http-equiv="refresh" content="2">
<style>
/* kleurenpalet pti #555555 #d6af00 */
*{margin:0;padding:0;box-sizing:border-box;}
body{
  font-family:'Courier New',monospace;
  background:#555555;
  color:#d6af00;
}
header{
  width:100%;height:80px;background:#555555;position:fixed;top:0;left:0;
  display:flex;justify-content:center;align-items:center;z-index:10;
}
.wrapper{width:90%;display:flex;justify-content:space-between;align-items:center;}
.logo img{height:60px;}
nav a{
  text-decoration:none;padding:0 15px;color:#d6af00;font-size:22px;
}
nav a:hover{background:#d6af00;color:#555555;border-radius:8px;}
.banner{
  background:#222;height:200px;text-align:center;
  padding-top:120px;font-size:28px;
}
.content-I{padding:30px;text-align:center;}
ul{list-style:none;padding:0;margin:20px auto;max-width:400px;text-align:left;}
li{margin:6px 0;font-size:18px;}
#kompas{
  margin:30px auto;width:150px;height:150px;border:5px solid #d6af00;
  border-radius:50%;position:relative;
}
#pijl{
  width:4px;height:60px;background:#d6af00;
  position:absolute;top:25px;left:73px;
  transform-origin:bottom center;
  transform:rotate({{ hoek }}deg);
  transition:transform 0.5s ease;
}
canvas{margin-top:20px;max-width:400px;width:90%;}
footer{
  margin-top:40px;padding:10px;background:#555555;
  color:#d6af00;text-align:center;font-size:14px;
}
</style>
</head>
<body>
<header>
  <div class="wrapper">
    <div class="logo"><img src="https://via.placeholder.com/100x60.png?text=PTI" alt="logo"></div>
    <nav>
      <a href="#">Home</a>
      <a href="#">Weerdata</a>
      <a href="#">Over</a>
    </nav>
  </div>
</header>

<div class="banner"><h2>PTI Weerstation</h2></div>

<div class="content-I">
  <h2>Live Data</h2>
  {% if has_data %}
  <ul>
    <li>🌡️ BME Temp: {{ temp }} °C</li>
    <li>💧 Luchtvochtigheid: {{ hum }} %</li>
    <li>📈 Luchtdruk: {{ druk }} hPa</li>
    <li>💨 Windsnelheid: {{ wind }} km/u</li>
    <li>🧭 Richting: {{ richting }} ({{ hoek }}°)</li>
    <li>🌡️ DS18B20 #1: {{ t1 }} °C</li>
    <li>🌡️ DS18B20 #2: {{ t2 }} °C</li>
  </ul>
  <canvas id="grafiek" height="120"></canvas>
  <div id="kompas"><div id="pijl"></div></div>
  {% else %}
  <p>Nog geen data ontvangen...</p>
  {% endif %}
</div>

<footer>© 2025 PTI Weerstation Project</footer>

<script>
{% if has_data %}
const ctx = document.getElementById('grafiek').getContext('2d');
new Chart(ctx, {
  type: 'line',
  data: {
    labels: {{ labels }},
    datasets: [{
      label: 'Temperatuur (°C)',
      data: {{ temps }},
      borderColor: '#d6af00',
      tension: 0.3
    }]
  },
  options: {
    scales: {y: {beginAtZero: false}},
    plugins: {legend: {display: false}}
  }
});
{% endif %}
</script>
</body>
</html>
"""

# ----------------------------------
# Routes
# ----------------------------------
@app.route("/")
def index():
    if data_log:
        d = data_log[-1]

        # gebruik veilige .get() zodat ontbrekende velden geen crash veroorzaken
        temps = [x.get("bme_temp", x.get("temp", 0)) for x in data_log[-10:]]
        labels = list(range(len(temps)))

        return render_template_string(
            HTML,
            has_data=True,
            temp=d.get("bme_temp", d.get("temp", "-")),
            hum=d.get("hum", "-"),
            druk=d.get("druk", "-"),
            wind=d.get("wind", "-"),
            richting=d.get("richting", "-"),
            hoek=d.get("hoek", 0),
            t1=d.get("ds18b20_1", "-"),
            t2=d.get("ds18b20_2", "-"),
            temps=temps,
            labels=labels
        )
    else:
        return render_template_string(HTML, has_data=False)

@app.route("/update", methods=["POST"])
def update():
    content = request.get_json(force=True)
    if not isinstance(content, dict):
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    content["tijd"] = time.time()
    data_log.append(content)
    if len(data_log) > 100:
        data_log.pop(0)
    print("Nieuwe data ontvangen:", content)
    return jsonify({"status": "OK"})

# ----------------------------------
# Start Flask-server
# ----------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
