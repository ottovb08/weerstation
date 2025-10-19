fetch("thingspeak_data.csv")
  .then(response => response.text())
  .then(csvText => {
    // CSV parsen naar array van objecten
    const result = Papa.parse(csvText, { header: true });
    const data = result.data.filter(row => row.created_at); // lege regels negeren

    if (data.length === 0) return;

    // Laatste record
    const last = data[data.length - 1];
    const laatsteTemperatuur = parseFloat(last.field1);
    const laatsteLuchtdruk = parseFloat(last.field2);

    console.log("Laatste temperatuur:", laatsteTemperatuur);
    console.log("Laatste luchtdruk:", laatsteLuchtdruk);

    document.getElementById("temp").textContent = laatsteTemperatuur;
    document.getElementById("luchtdruk").textContent = laatsteLuchtdruk;
  });

