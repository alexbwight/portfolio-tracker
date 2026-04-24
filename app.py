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
    aapl_percent = msft_percent = 0

    if request.method == "POST":
        # INPUT
        btc_amount = float(request.form.get("btc") or 0)
        eth_amount = float(request.form.get("eth") or 0)
        vwce_amount = float(request.form.get("vwce") or 0)
        aapl_amount = float(request.form.get("aapl") or 0)
        msft_amount = float(request.form.get("msft") or 0)
        goal_amount = float(request.form.get("goal") or 100000)

        # CRYPTO PRICES
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

        # STOCK PRICES
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

        # PERCENTAGES
        if total_value > 0:
            btc_percent = (btc_value / total_value) * 100
            eth_percent = (eth_value / total_value) * 100
            vwce_percent = (vwce_value / total_value) * 100
            aapl_percent = (aapl_value / total_value) * 100
            msft_percent = (msft_value / total_value) * 100

        crypto_percent = btc_percent + eth_percent
        stock_percent = vwce_percent + aapl_percent + msft_percent

        # HEALTH SCORE
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
        <h3>📊 Portfolio Health</h3>
        <div style="font-size:30px; color:{color}; font-weight:bold;">
            {score}/100
        </div>
        <div>{label}</div>
        """

        # PROJECTION
        r = 0.07

        years_5 = total_value * ((1 + r) ** 5)
        years_10 = total_value * ((1 + r) ** 10)

        projection_block = f"""
        <h3>📈 Future Projection</h3>
        5Y: €{years_5:,.0f}<br>
        10Y: €{years_10:,.0f}<br>
        <small>Assumes 7% annual growth. Estimate, not a guarantee.</small>
        """

        # GOAL TRACKER
        if total_value <= 0:
            goal_block = "<h3>🎯 Goal</h3>Enter your portfolio first"
        elif goal_amount <= total_value:
            goal_block = f"<h3>🎯 Goal</h3>Goal reached: €{goal_amount:,.0f}"
        else:
            years_to_goal = math.log(goal_amount / total_value) / math.log(1 + r)
            goal_block = f"<h3>🎯 Goal</h3>{years_to_goal:.1f} years to €{goal_amount:,.0f}"

        # MONTHLY INVESTING SIMULATOR
        monthly = 500
        months = 60
        monthly_rate = r / 12

        future_existing = total_value * ((1 + monthly_rate) ** months)
        future_contributions = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        future_with_monthly = future_existing + future_contributions

        monthly_block = f"""
        <h3>💸 Monthly Investing</h3>
        If you add €500/month:<br>
        5Y estimate: €{future_with_monthly:,.0f}
        """

        # DAILY MOVE ESTIMATE
        daily_change = total_value * 0.01

        daily_block = f"""
        <h3>📅 Daily Move Estimate</h3>
        A 1% move = ± €{daily_change:,.0f}
        """

        # OUTPUT
        result = f"""
        <h2>Total: €{total_value:,.0f}</h2>

        <h3>Crypto</h3>
        BTC: €{btc_value:,.0f} ({btc_percent:.1f}%)<br>
        ETH: €{eth_value:,.0f} ({eth_percent:.1f}%)<br>

        <h3>Stocks</h3>
        VWCE: €{vwce_value:,.0f} ({vwce_percent:.1f}%)<br>
        Apple: €{aapl_value:,.0f} ({aapl_percent:.1f}%)<br>
        Microsoft: €{msft_value:,.0f} ({msft_percent:.1f}%)
        """

        # QUICK INSIGHTS
        quick_insights = []

        if crypto_percent > 30:
            quick_insights.append("⚠️ Crypto is a large part of your portfolio, so volatility may be high.")
        else:
            quick_insights.append("✅ Crypto exposure looks controlled.")

        if vwce_percent > 50:
            quick_insights.append("✅ Strong ETF base for long-term investing.")
        else:
            quick_insights.append("ℹ️ Your ETF allocation is lower than your other assets.")

        if stock_percent > crypto_percent:
            quick_insights.append("✅ Most of your portfolio is in stocks/ETFs.")
        else:
            quick_insights.append("⚠️ Crypto is bigger than your stock/ETF allocation.")

        quick_insights.append("🔒 No login or account linking required.")

        insight = "<br><br>".join(quick_insights)

        response = make_response(render_page(
            result, insight,
            health_block, projection_block,
            goal_block, monthly_block, daily_block,
            btc_amount, eth_amount, vwce_amount,
            aapl_amount, msft_amount, goal_amount
        ))

        # SAVE COOKIES
        for k, v in {
            "btc": btc_amount,
            "eth": eth_amount,
            "vwce": vwce_amount,
            "aapl": aapl_amount,
            "msft": msft_amount,
            "goal": goal_amount
        }.items():
            response.set_cookie(k, str(v))

        return response

    return render_page(
        result, insight,
        health_block, projection_block,
        goal_block, monthly_block, daily_block,
        btc_amount, eth_amount, vwce_amount,
        aapl_amount, msft_amount, goal_amount
    )


def render_page(result, insight,
    health, projection, goal, monthly, daily,
    btc, eth, vwce, aapl, msft, goal_val):

    return f"""
<html>
<head>
<style>
body {{
    background: #0f172a;
    color: white;
    font-family: Arial;
    text-align: center;
    margin: 0;
    padding: 35px;
}}

.subtitle {{
    color: #94a3b8;
    margin-top: -10px;
    margin-bottom: 30px;
}}

.container {{
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
}}

.card {{
    background: #1e293b;
    padding: 22px;
    border-radius: 14px;
    width: 320px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}}

input {{
    margin: 6px;
    padding: 10px;
    width: 220px;
    border-radius: 8px;
    border: none;
}}

button {{
    margin-top: 10px;
    padding: 12px 20px;
    background: #22c55e;
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: bold;
    cursor: pointer;
}}

h3 {{
    color: #cbd5e1;
}}

small {{
    color: #94a3b8;
}}

.insights {{
    text-align: left;
    line-height: 1.4;
    background: #0f172a;
    padding: 12px;
    border-radius: 10px;
}}
</style>
</head>

<body>

<h1>📊 Wealth Dashboard</h1>
<p class="subtitle">No login. No account linking. Quick portfolio insights.</p>

<div class="container">

<div class="card">
<form method="POST">
<h3>Crypto</h3>
<input name="btc" value="{btc}" placeholder="BTC amount"><br>
<input name="eth" value="{eth}" placeholder="ETH amount"><br>

<h3>Stocks</h3>
<input name="vwce" value="{vwce}" placeholder="VWCE shares"><br>
<input name="aapl" value="{aapl}" placeholder="Apple shares"><br>
<input name="msft" value="{msft}" placeholder="Microsoft shares"><br>

<h3>Goal</h3>
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

<h3>⚡ Quick Insights</h3>
<div class="insights">
{insight}
</div>
</div>

</div>

</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)