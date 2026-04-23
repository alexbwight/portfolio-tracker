from flask import Flask, request, make_response
import requests
import yfinance as yf
import os
import math

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    insight = ""
    health_block = ""
    projection_block = ""
    goal_block = ""
    monthly_block = ""
    daily_block = ""

    # cookies
    btc_amount = request.cookies.get("btc", "")
    eth_amount = request.cookies.get("eth", "")
    vwce_amount = request.cookies.get("vwce", "")
    aapl_amount = request.cookies.get("aapl", "")
    msft_amount = request.cookies.get("msft", "")
    goal_amount = request.cookies.get("goal", "")

    btc_percent = eth_percent = vwce_percent = 0

    if request.method == "POST":
        # INPUT
        btc_amount = float(request.form.get("btc") or 0)
        eth_amount = float(request.form.get("eth") or 0)
        vwce_amount = float(request.form.get("vwce") or 0)
        aapl_amount = float(request.form.get("aapl") or 0)
        msft_amount = float(request.form.get("msft") or 0)
        goal_amount = float(request.form.get("goal") or 100000)

        # CRYPTO
        try:
            data = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=eur",
                timeout=5
            ).json()

            btc_price = data.get("bitcoin", {}).get("eur", 60000)
            eth_price = data.get("ethereum", {}).get("eur", 2000)
        except:
            btc_price = 60000
            eth_price = 2000

        # STOCKS
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

        # %
        if total_value > 0:
            btc_percent = (btc_value / total_value) * 100
            eth_percent = (eth_value / total_value) * 100
            vwce_percent = (vwce_value / total_value) * 100

        crypto_percent = btc_percent + eth_percent

        # 🔥 HEALTH SCORE
        if crypto_percent > 70:
            score = 30
            label = "High Risk"
            color = "#ef4444"
        elif crypto_percent > 40:
            score = 60
            label = "Moderate Risk"
            color = "#f59e0b"
        else:
            score = 85
            label = "Healthy Allocation"
            color = "#22c55e"

        health_block = f"""
        <h3>📊 Health: <span style="color:{color}">{score}/100</span></h3>
        <div>{label}</div>
        """

        # 🔥 PROJECTION
        r = 0.07
        years_5 = total_value * ((1 + r) ** 5)
        years_10 = total_value * ((1 + r) ** 10)

        projection_block = f"""
        <h3>📈 Projection</h3>
        5Y: €{years_5:,.0f}<br>
        10Y: €{years_10:,.0f}
        """

        # 🔥 GOAL TRACKER
        try:
            years_to_goal = math.log(goal_amount / total_value) / math.log(1 + r)
            goal_block = f"<h3>🎯 Goal</h3>{years_to_goal:.1f} years to €{goal_amount:,.0f}"
        except:
            goal_block = "<h3>🎯 Goal</h3>Set a goal"

        # 🔥 MONTHLY
        monthly = 500
        months = 60
        future_monthly = monthly * (((1 + r/12) ** months - 1) / (r/12))

        monthly_block = f"""
        <h3>💸 Monthly (€500)</h3>
        5Y: €{future_monthly:,.0f}
        """

        # 🔥 DAILY
        daily_change = total_value * 0.01

        daily_block = f"""
        <h3>📅 Daily</h3>
        ± €{daily_change:,.0f}
        """

        # OUTPUT
        result = f"""
        <h2>Total: €{total_value:,.0f}</h2>

        BTC €{btc_value:,.0f} | ETH €{eth_value:,.0f}<br>
        VWCE €{vwce_value:,.0f}<br>
        AAPL €{aapl_value:,.0f} | MSFT €{msft_value:,.0f}
        """

        insight = "⚖️ Balanced"
        if crypto_percent > 50:
            insight = "⚠️ Crypto heavy"

        response = make_response(render_page(
            result, insight,
            health_block, projection_block,
            goal_block, monthly_block, daily_block,
            btc_amount, eth_amount, vwce_amount,
            aapl_amount, msft_amount, goal_amount
        ))

        # SAVE
        for k,v in {
            "btc":btc_amount,"eth":eth_amount,"vwce":vwce_amount,
            "aapl":aapl_amount,"msft":msft_amount,"goal":goal_amount
        }.items():
            response.set_cookie(k, str(v))

        return response

    return render_page(result, insight,
        health_block, projection_block,
        goal_block, monthly_block, daily_block,
        btc_amount, eth_amount, vwce_amount,
        aapl_amount, msft_amount, goal_amount)


def render_page(result, insight,
    health, projection, goal, monthly, daily,
    btc, eth, vwce, aapl, msft, goal_val):

    return f"""
<html>
<head>
<style>
body {{
    background:#0f172a;
    color:white;
    font-family:Arial;
    text-align:center;
}}
.container {{
    display:flex;
    justify-content:center;
    gap:20px;
    flex-wrap:wrap;
}}
.card {{
    background:#1e293b;
    padding:20px;
    border-radius:12px;
    width:300px;
}}
input {{
    margin:5px;
    padding:8px;
    border-radius:6px;
}}
button {{
    padding:10px;
    background:#22c55e;
    border:none;
    border-radius:6px;
}}
</style>
</head>

<body>

<h1>📊 Wealth Dashboard</h1>

<div class="container">

<div class="card">
<form method="POST">
<input name="btc" value="{btc}" placeholder="BTC"><br>
<input name="eth" value="{eth}" placeholder="ETH"><br>
<input name="vwce" value="{vwce}" placeholder="VWCE"><br>
<input name="aapl" value="{aapl}" placeholder="Apple"><br>
<input name="msft" value="{msft}" placeholder="Microsoft"><br>
<input name="goal" value="{goal_val}" placeholder="Goal €"><br>
<button>Calculate</button>
</form>
</div>

<div class="card">
{result}
{health}
{projection}
{goal}
{monthly}
{daily}
<h3>{insight}</h3>
</div>

</div>

</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)