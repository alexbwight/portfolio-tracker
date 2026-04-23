from flask import Flask, request, make_response
import requests
import yfinance as yf
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    insight = ""
    chart_script = ""

    # defaults (for first load + cookies)
    btc_amount = request.cookies.get("btc", "")
    eth_amount = request.cookies.get("eth", "")
    vwce_amount = request.cookies.get("vwce", "")
    aapl_amount = request.cookies.get("aapl", "")
    msft_amount = request.cookies.get("msft", "")

    btc_percent = eth_percent = vwce_percent = 0

    if request.method == "POST":
        # SAFE INPUT
        btc_amount = float(request.form.get("btc") or 0)
        eth_amount = float(request.form.get("eth") or 0)
        vwce_amount = float(request.form.get("vwce") or 0)
        aapl_amount = float(request.form.get("aapl") or 0)
        msft_amount = float(request.form.get("msft") or 0)

        # 🔥 CRYPTO API (SAFE)
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=eur"
            data = requests.get(url, timeout=5).json()

            btc_price = data.get("bitcoin", {}).get("eur", 60000)
            eth_price = data.get("ethereum", {}).get("eur", 2000)
        except:
            btc_price = 60000
            eth_price = 2000

        # 🔥 STOCKS
        def get_price(ticker, fallback):
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="1d")
                return hist["Close"].iloc[-1] if not hist.empty else fallback
            except:
                return fallback

        vwce_price = get_price("VWCE.DE", 100)
        aapl_price = get_price("AAPL", 150)
        msft_price = get_price("MSFT", 300)

        # VALUES
        btc_value = btc_amount * btc_price
        eth_value = eth_amount * eth_price
        vwce_value = vwce_amount * vwce_price
        aapl_value = aapl_amount * aapl_price
        msft_value = msft_amount * msft_price

        total_value = btc_value + eth_value + vwce_value + aapl_value + msft_value

        # PERCENTAGES (only main 3 for chart)
        if total_value > 0:
            btc_percent = (btc_value / total_value) * 100
            eth_percent = (eth_value / total_value) * 100
            vwce_percent = (vwce_value / total_value) * 100

        # OUTPUT
        result = f"""
        <h2>💰 Portfolio Overview</h2>

        <h3>Crypto</h3>
        BTC: €{btc_value:,.2f} ({btc_percent:.1f}%) <br>
        ETH: €{eth_value:,.2f} ({eth_percent:.1f}%) <br><br>

        <h3>Stocks</h3>
        VWCE: €{vwce_value:,.2f} ({vwce_percent:.1f}%) <br>
        Apple: €{aapl_value:,.2f} <br>
        Microsoft: €{msft_value:,.2f} <br><br>

        <hr>

        <h2>Total: €{total_value:,.2f}</h2>
        """

        # INSIGHT
        if btc_percent > 50:
            insight = "⚠️ Heavy crypto exposure"
        elif vwce_percent > 60:
            insight = "✅ Strong long-term allocation"
        else:
            insight = "⚖️ Balanced portfolio"

        # CHART
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

        # SAVE COOKIES
        response = make_response(render_page(
            result, insight, chart_script,
            btc_amount, eth_amount, vwce_amount,
            aapl_amount, msft_amount
        ))

        response.set_cookie("btc", str(btc_amount))
        response.set_cookie("eth", str(eth_amount))
        response.set_cookie("vwce", str(vwce_amount))
        response.set_cookie("aapl", str(aapl_amount))
        response.set_cookie("msft", str(msft_amount))

        return response

    return render_page(
        result, insight, chart_script,
        btc_amount, eth_amount, vwce_amount,
        aapl_amount, msft_amount
    )


def render_page(result, insight, chart_script, btc, eth, vwce, aapl, msft):
    return f"""
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <title>Wealth Dashboard</title>

    <style>
        body {{
            font-family: Arial;
            background: #0f172a;
            color: white;
            text-align: center;
            padding: 40px;
        }}

        h1 {{
            font-size: 34px;
        }}

        .container {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .card {{
            background: #1e293b;
            padding: 25px;
            border-radius: 16px;
            width: 320px;
        }}

        input {{
            padding: 10px;
            margin: 6px;
            width: 200px;
            border-radius: 8px;
            border: none;
        }}

        button {{
            padding: 12px 20px;
            background: #22c55e;
            border: none;
            color: white;
            border-radius: 8px;
            cursor: pointer;
        }}

        hr {{
            border: 1px solid #334155;
        }}
    </style>
</head>

<body>

<h1>📊 Wealth Dashboard</h1>

<div class="container">

<div class="card">
<form method="POST">
    <h3>Crypto</h3>
    <input name="btc" value="{btc}" placeholder="BTC"><br>
    <input name="eth" value="{eth}" placeholder="ETH"><br>

    <h3>Stocks</h3>
    <input name="vwce" value="{vwce}" placeholder="VWCE"><br>
    <input name="aapl" value="{aapl}" placeholder="Apple"><br>
    <input name="msft" value="{msft}" placeholder="Microsoft"><br>

    <button type="submit">Calculate</button>
</form>
</div>

<div class="card">
{result}
<br><br>
<h3>{insight}</h3>
{"<canvas id='chart'></canvas>" if result else ""}
</div>

</div>

{chart_script}

</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)