<h2>Weerstation</h2>
<p>In dit project maken we een weerstation dat op het dak van onze school zal geplaatst worden (Richtpunt Campus Zottegem). Dit weerstation voorzien van een raspberry pico zal
zijn data doorsturen naar onze NAS. Die op zijn beurt een website runt met Flask waar onze metingen kunnen afgelezen worden</p>
<br>
<h3>Weerstation</h3>
<p>Ons weerstation heeft een raspberry pico als microcontroller. We meten verschillende waarden:</p>
<ul>
  <li>temperatuur</li>
  <li>luchtvochtigheid</li>
  <li>neerslag</li>
  <li>windsnelheid</li>
  <li>windrichting</li>
  <li>uv-index</li>
</ul>
<p>De raspberry pico verzamelt deze data en verstuurd die dan via de wifi naar onze NAS</p>
<br>
<h3>NAS</h3>
<p>Voor onze NAS gebruiken we een Raspberry Pi 5 en een SSD van 25O GB met OpenMediaVault. Op deze NAS wordt ook een FLASK server gerunt die onze website host. Op deze website kun je de gegevens van het moment zelf bekijken en weken/maanden/jaren terugkijken in grafieken.</p>
