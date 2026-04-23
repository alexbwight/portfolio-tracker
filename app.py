from flask import Flask, request
import requests
import yfinance as yf

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    insight = ""
    chart_script = ""

    btc_percent = 0
    eth_percent = 0
    vwce_percent = 0

    if request.method == "POST":
        btc_amount = float(request.form.get("btc", 0))
        eth_amount = float(request.form.get("eth", 0))
        vwce_amount = float(request.form.get("vwce", 0))

        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=eur"
        data = requests.get(url).json()

        btc_price = data["bitcoin"]["eur"]
        eth_price = data["ethereum"]["eur"]
        try:
           vwce = yf.Ticker("VWCE.DE")
           vwce_price = vwce.history(period="1d")["Close"].iloc[-1]
        except:
           vwce_price = 100  # fallback

        btc_value = btc_amount * btc_price
        eth_value = eth_amount * eth_price
        vwce_value = vwce_amount * vwce_price

        total_value = btc_value + eth_value + vwce_value

        if total_value > 0:
            btc_percent = (btc_value / total_value) * 100
            eth_percent = (eth_value / total_value) * 100
            vwce_percent = (vwce_value / total_value) * 100

        result = f"""
        <h3>Portfolio Value</h3>
        BTC: €{btc_value:.2f} ({btc_percent:.1f}%) <br>
        ETH: €{eth_value:.2f} ({eth_percent:.1f}%) <br>
        VWCE: €{vwce_value:.2f} ({vwce_percent:.1f}%) <br><br>
        <b>Total: €{total_value:.2f}</b>
        """

        if btc_percent > 50:
            insight = "⚠️ Heavy crypto exposure"
        elif vwce_percent > 60:
            insight = "✅ Strong long-term allocation"
        else:
            insight = "⚖️ Balanced portfolio"

        # SAFE chart script
        chart_script = f"""
        <script>
        const data = {{
            labels: ['BTC', 'ETH', 'VWCE'],
            datasets: [{{
                data: [{btc_percent}, {eth_percent}, {vwce_percent}],
                backgroundColor: ['#f7931a', '#627eea', '#22c55e']
            }}]
        }};

        new Chart(document.getElementById('chart'), {{
            type: 'pie',
            data: data
        }});
        </script>
        """

    return f"""
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <title>Portfolio Tracker</title>

    <style>
        body {{
            font-family: Arial;
            background: #0f172a;
            color: white;
            text-align: center;
            padding: 50px;
        }}

        h1 {{
           font-size: 32px;
           margin-bottom: 20px;
        }}

        input {{
            padding: 12px;
            margin: 10px;
            width: 220px;
            border-radius: 8px;
            border: none;
            font-size: 14px;
        }}

        button {{
            padding: 12px 24px;
            background: #22c55e;
            border: none;
            color: white;
            font-weight: bold;
            cursor: pointer;
            border-radius: 8px;
            font-size: 14px;
        }}

        .card {{
            background: #1e293b;
            padding: 30px;
            border-radius: 16px;
            display: inline-block;
            margin-top: 20px;
            width: 350px;
        }}
    </style>
</head>

<body>

<h1>💼 Portfolio Tracker</h1>

<form method="POST">
    <input name="btc" placeholder="BTC amount"><br>
    <input name="eth" placeholder="ETH amount"><br>
    <input name="vwce" placeholder="VWCE amount"><br>
    <button type="submit">Calculate</button>
</form>

<div class="card">
    {result}
    <br><br>
    <h3>{insight}</h3>

    {"<canvas id='chart' width='300' height='300'></canvas>" if result else ""}
</div>

{chart_script}

</body>
</html>
"""

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)