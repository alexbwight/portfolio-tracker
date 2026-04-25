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
        <div style="font-size:30px; color:{color}; font-weight:800;">
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wealth Dashboard</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: 'Inter', Arial, sans-serif;
    color: #f8fafc;
    background:
        radial-gradient(circle at top left, rgba(34,197,94,0.12), transparent 35%),
        radial-gradient(circle at top right, rgba(59,130,246,0.12), transparent 30%),
        linear-gradient(180deg, #020617 0%, #0f172a 100%);
    min-height: 100vh;
    padding: 32px 20px 50px;
}}

.page {{
    max-width: 1120px;
    margin: 0 auto;
}}

.hero {{
    text-align: center;
    margin-bottom: 28px;
}}

.hero h1 {{
    margin: 0;
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -0.04em;
}}

.subtitle {{
    color: #94a3b8;
    margin: 12px 0 8px;
    font-size: 16px;
}}

.demo {{
    display: inline-block;
    margin-top: 10px;
    color: #cbd5e1;
    font-size: 13px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 10px 14px;
    border-radius: 999px;
}}

.layout {{
    display: grid;
    grid-template-columns: 360px 1fr;
    gap: 22px;
    align-items: start;
}}

.card {{
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(148,163,184,0.16);
    border-radius: 22px;
    padding: 24px;
    box-shadow:
        0 20px 50px rgba(0,0,0,0.38),
        inset 0 1px 0 rgba(255,255,255,0.04);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}}

.form-title {{
    margin: 0 0 10px;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.02em;
}}

.help {{
    color: #94a3b8;
    font-size: 14px;
    line-height: 1.5;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(148,163,184,0.10);
    padding: 14px;
    border-radius: 16px;
    margin: 0 0 18px;
}}

.section-label {{
    text-align: left;
    color: #e2e8f0;
    font-weight: 700;
    font-size: 14px;
    margin: 18px 0 8px;
}}

input {{
    width: 100%;
    margin: 7px 0;
    padding: 13px 14px;
    border-radius: 14px;
    border: 1px solid rgba(148,163,184,0.18);
    background: rgba(255,255,255,0.04);
    color: white;
    font-size: 14px;
    outline: none;
    transition: 0.2s ease;
}}

input::placeholder {{
    color: #94a3b8;
}}

input:focus {{
    border-color: rgba(34,197,94,0.75);
    box-shadow: 0 0 0 4px rgba(34,197,94,0.12);
    background: rgba(255,255,255,0.06);
}}

button {{
    width: 100%;
    margin-top: 16px;
    padding: 14px 18px;
    border: none;
    border-radius: 14px;
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    color: white;
    font-weight: 800;
    font-size: 15px;
    cursor: pointer;
    box-shadow: 0 12px 24px rgba(34,197,94,0.22);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}

button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 16px 30px rgba(34,197,94,0.30);
}}

.summary-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}}

.summary-title {{
    font-size: 24px;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.03em;
}}

.pill {{
    font-size: 12px;
    color: #bbf7d0;
    background: rgba(34,197,94,0.10);
    border: 1px solid rgba(34,197,94,0.25);
    padding: 8px 12px;
    border-radius: 999px;
}}

.result-block {{
    text-align: left;
    line-height: 1.7;
}}

.result-block h2 {{
    margin: 0 0 12px;
    font-size: 34px;
    letter-spacing: -0.04em;
}}

.result-block h3 {{
    margin: 18px 0 8px;
    font-size: 15px;
    color: #cbd5e1;
}}

.metrics {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 18px;
}}

.metric-card {{
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 16px;
    padding: 16px;
    text-align: left;
}}

.metric-card h3 {{
    margin: 0 0 10px;
    font-size: 14px;
    color: #cbd5e1;
}}

.metric-card div {{
    line-height: 1.6;
}}

.insight-wrap {{
    margin-top: 18px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 18px;
    padding: 18px;
    text-align: left;
}}

.insight-wrap h3 {{
    margin: 0 0 12px;
    font-size: 16px;
}}

.insights {{
    color: #e2e8f0;
    line-height: 1.7;
}}

.feedback {{
    text-align: center;
    margin-top: 24px;
    color: #94a3b8;
    font-size: 14px;
}}

.feedback a {{
    display: inline-block;
    margin-top: 8px;
    color: #86efac;
    text-decoration: none;
    font-weight: 700;
}}

.feedback a:hover {{
    text-decoration: underline;
}}

@media (max-width: 900px) {{
    .layout {{
        grid-template-columns: 1fr;
    }}

    .hero h1 {{
        font-size: 34px;
    }}
}}

@media (max-width: 640px) {{
    body {{
        padding: 22px 14px 40px;
    }}

    .card {{
        padding: 18px;
        border-radius: 18px;
    }}

    .hero h1 {{
        font-size: 28px;
    }}

    .subtitle {{
        font-size: 14px;
    }}

    .demo {{
        font-size: 12px;
        line-height: 1.4;
        border-radius: 14px;
    }}

    .metrics {{
        grid-template-columns: 1fr;
    }}

    .result-block h2 {{
        font-size: 28px;
    }}
}}
</style>
</head>

<body>
<div class="page">

    <div class="hero">
        <h1>📊 Wealth Dashboard</h1>
        <p class="subtitle">No login. No account linking. Quick portfolio insights.</p>
        <div class="demo">Try example: 0.01 BTC, 0.5 ETH, 10 VWCE, 1 Apple, 1 Microsoft</div>
    </div>

    <div class="layout">

        <div class="card">
            <h2 class="form-title">Your Portfolio</h2>

            <p class="help">
                Enter the amount of each asset you own, not the euro value.<br>
                Example: 0.01 BTC, 0.5 ETH, 10 VWCE shares.
            </p>

            <form method="POST">
                <div class="section-label">Crypto</div>
                <input name="btc" value="{btc}" placeholder="BTC amount">
                <input name="eth" value="{eth}" placeholder="ETH amount">

                <div class="section-label">Stocks</div>
                <input name="vwce" value="{vwce}" placeholder="VWCE shares">
                <input name="aapl" value="{aapl}" placeholder="Apple shares">
                <input name="msft" value="{msft}" placeholder="Microsoft shares">

                <div class="section-label">Goal</div>
                <input name="goal" value="{goal_val}" placeholder="Goal €">

                <button type="submit">Calculate Portfolio</button>
            </form>
        </div>

        <div class="card">
            <div class="summary-header">
                <h2 class="summary-title">Overview</h2>
                <div class="pill">Privacy-first</div>
            </div>

            <div class="result-block">
                {result}
            </div>

            <div class="metrics">
                <div class="metric-card">{health}</div>
                <div class="metric-card">{projection}</div>
                <div class="metric-card">{goal}</div>
                <div class="metric-card">{monthly}</div>
            </div>

            <div class="metric-card" style="margin-top: 14px;">
                {daily}
            </div>

            <div class="insight-wrap">
                <h3>⚡ Quick Insights</h3>
                <div class="insights">
                    {insight}
                </div>
            </div>
        </div>

    </div>

    <div class="feedback">
        <p>Found something confusing?</p>
        <a href="mailto:alexbwight@gmail.com?subject=Wealth Dashboard Feedback">
            Send feedback
        </a>
    </div>

</div>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)