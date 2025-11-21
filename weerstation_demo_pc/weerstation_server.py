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
body{
  background:#555;
  color:#d6af00;
  font-family:Courier New;
  text-align:center;
}
canvas{max-width:500px;margin:20px auto;}
#gauge{
  width:200px;
  height:100px;
  border-radius:200px 200px 0 0;
  background:#222;
  margin:20px auto;
  position:relative;
}
#needle{
  width:4px;
  height:80px;
  background:#d6af00;
  position:absolute;
  left:98px;
  top:20px;
  transform-origin:bottom center;
  transform:rotate({{ wind_hoek }}deg);
}
</style>
</head>
<body>

<h1>🌦️ PTI Weerstation</h1>

{% if has_data %}
<h2>Live gegevens</h2>
<p>🌡️ Temp: {{ temp }} °C</p>
<p>💧 Vocht: {{ hum }} %</p>
<p>📈 Druk: {{ druk }} hPa</p>
<p>💨 Wind: {{ wind }} km/u</p>
<p>🧭 Richting: {{ richting }} ({{ hoek }}°)</p>
<p>🌿 Groene dakbedekking: {{ t1 }} °C</p>
<p>🏠 Gewone dakbedekking: {{ t2 }} °C</p>

<!-- Windsnelheid gauge -->
<div id="gauge">
    <div id="needle"></div>
</div>

<!-- Grafieken -->
<canvas id="tempChart"></canvas>
<canvas id="humChart"></canvas>
<canvas id="drukChart"></canvas>
<canvas id="windChart"></canvas>

<script>
let temps = {{ temps }};
let hums = {{ hums }};
let druk = {{ druks }};
let winds = {{ winds }};
let labels = {{ labels }};

// Temperatuur
new Chart(document.getElementById('tempChart').getContext('2d'), {
  type:'line',
  data:{ labels:labels, datasets:[{label:'Temp °C', data:temps, borderColor:'#d6af00'}] }
});

// Vochtigheid
new Chart(document.getElementById('humChart').getContext('2d'), {
  type:'line',
  data:{ labels:labels, datasets:[{label:'Vocht %', data:hums, borderColor:'#00eaff'}] }
});

// Luchtdruk
new Chart(document.getElementById('drukChart').getContext('2d'), {
  type:'line',
  data:{ labels:labels, datasets:[{label:'Druk hPa', data:druk, borderColor:'#ff8800'}] }
});

// Wind
new Chart(document.getElementById('windChart').getContext('2d'), {
  type:'line',
  data:{ labels:labels, datasets:[{label:'Wind km/u', data:winds, borderColor:'#00ff55'}] }
});
</script>

{% else %}
<h2>Nog geen data ontvangen...</h2>
{% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    if data_log:
        d = data_log[-1]

        temps = [x.get("temp", 0) for x in data_log[-20:]]
        hums = [x.get("hum", 0) for x in data_log[-20:]]
        druks = [x.get("druk", 0) for x in data_log[-20:]]
        winds = [x.get("wind", 0) for x in data_log[-20:]]
        labels = list(range(len(temps)))

        return render_template_string(
            HTML,
            has_data=True,
            temp=d.get("temp"),
            hum=d.get("hum"),
            druk=d.get("druk"),
            wind=d.get("wind"),
            richting=d.get("richting"),
            hoek=d.get("hoek"),

            # nieuwe DS18B20 namen
            t1=d.get("groene_dakbedekking"),
            t2=d.get("gewone_dakbedekking"),

            temps=temps,
            hums=hums,
            druks=druks,
            winds=winds,
            labels=labels,

            wind_hoek = d.get("wind",0) * 3  # schaal voor gauge
        )
    return render_template_string(HTML, has_data=False)

@app.route("/update", methods=["POST"])
def update():
    content = request.get_json(force=True)
    content["tijd"] = time.time()
    data_log.append(content)
    if len(data_log) > 300:
        data_log.pop(0)
    print("Ontvangen:", content)
    return jsonify({"status":"OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)