from flask import Flask, request, make_response
import yfinance as yf
import os
import math

app = Flask(__name__)


def safe_float(value, default=0):
    try:
        return float(value)
    except:
        return default


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
        btc_amount = safe_float(request.form.get("btc") or 0)
        eth_amount = safe_float(request.form.get("eth") or 0)
        vwce_amount = safe_float(request.form.get("vwce") or 0)
        aapl_amount = safe_float(request.form.get("aapl") or 0)
        msft_amount = safe_float(request.form.get("msft") or 0)
        goal_amount = safe_float(request.form.get("goal") or 100000, 100000)

        # PRICE FETCHING
        def get_price(ticker, fallback):
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="5d")

                if not hist.empty:
                    return hist["Close"].iloc[-1]
                return fallback
            except:
                return fallback

        # Crypto prices in EUR
        btc_price = get_price("BTC-EUR", 60000)
        eth_price = get_price("ETH-EUR", 2000)

        # ETF price in EUR
        vwce_price = get_price("VWCE.DE", 100)

        # Convert US stocks from USD to EUR
        eurusd = get_price("EURUSD=X", 1.08)
        usd_to_eur = 1 / eurusd if eurusd > 0 else 0.93

        aapl_price = get_price("AAPL", 150) * usd_to_eur
        msft_price = get_price("MSFT", 300) * usd_to_eur

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
        goal_block, monthly_block,
        daily_block,
        btc_amount, eth_amount, vwce_amount,
        aapl_amount, msft_amount, goal_amount
    )


def render_page(result, insight,
    health, projection, goal, monthly, daily,
    btc, eth, vwce, aapl, msft, goal_val):

    has_results = bool(result.strip())

    if has_results:
        overview_content = f"""
        <div class="overview-grid">
            <div class="main-panel">
                <div class="panel-header">
                    <div>
                        <p class="eyebrow">Portfolio Snapshot</p>
                        <h2>Overview</h2>
                    </div>
                    <span class="status-pill">Live prices</span>
                </div>

                <div class="result-card">
                    {result}
                </div>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">{health}</div>
                <div class="metric-card">{projection}</div>
                <div class="metric-card">{goal}</div>
                <div class="metric-card">{monthly}</div>
            </div>

            <div class="wide-metric">
                {daily}
            </div>

            <div class="insights-panel">
                <div class="panel-header">
                    <div>
                        <p class="eyebrow">Personalized</p>
                        <h2>Quick Insights</h2>
                    </div>
                </div>
                <div class="insights">
                    {insight}
                </div>
            </div>
        </div>
        """
    else:
        overview_content = """
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <h2>Your dashboard is ready</h2>
            <p>
                Enter your holdings on the left to calculate portfolio value,
                health score, projections, goal progress, and quick insights.
            </p>
            <div class="example-box">
                Try: <strong>0.01 BTC</strong>, <strong>0.5 ETH</strong>,
                <strong>10 VWCE</strong>, <strong>1 Apple</strong>, <strong>1 Microsoft</strong>
            </div>
        </div>
        """

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

:root {{
    --bg-main: #060b16;
    --bg-card: rgba(15, 23, 42, 0.78);
    --bg-card-soft: rgba(255, 255, 255, 0.035);
    --border: rgba(148, 163, 184, 0.16);
    --border-soft: rgba(148, 163, 184, 0.10);
    --text: #f8fafc;
    --muted: #94a3b8;
    --muted-2: #64748b;
    --green: #22c55e;
    --green-soft: rgba(34, 197, 94, 0.12);
    --blue: #60a5fa;
    --blue-soft: rgba(96, 165, 250, 0.12);
    --purple: #c084fc;
    --shadow: 0 24px 70px rgba(0, 0, 0, 0.42);
}}

body {{
    margin: 0;
    min-height: 100vh;
    font-family: 'Inter', Arial, sans-serif;
    color: var(--text);
    background:
        radial-gradient(circle at 10% 0%, rgba(34,197,94,0.16), transparent 28%),
        radial-gradient(circle at 90% 0%, rgba(96,165,250,0.15), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(192,132,252,0.12), transparent 34%),
        linear-gradient(180deg, #050914 0%, #0f172a 100%);
    padding: 28px 18px 50px;
}}

.page {{
    max-width: 1180px;
    margin: 0 auto;
}}

.nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 26px;
    flex-wrap: wrap;
}}

.brand {{
    display: flex;
    align-items: center;
    gap: 13px;
}}

.logo {{
    width: 48px;
    height: 48px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 23px;
    background: linear-gradient(135deg, #22c55e, #14b8a6);
    box-shadow: 0 16px 34px rgba(34,197,94,0.25);
}}

.brand h1 {{
    margin: 0;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.04em;
}}

.brand p {{
    margin: 4px 0 0;
    color: var(--muted);
    font-size: 13px;
}}

.nav-actions {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}}

.nav-pill {{
    border: 1px solid var(--border);
    background: rgba(255,255,255,0.045);
    color: #dbeafe;
    border-radius: 999px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 600;
}}

.hero {{
    margin-bottom: 24px;
}}

.hero-card {{
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border);
    background:
        linear-gradient(135deg, rgba(15,23,42,0.90), rgba(30,41,59,0.72)),
        radial-gradient(circle at top right, rgba(34,197,94,0.12), transparent 32%);
    border-radius: 30px;
    padding: 34px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}}

.hero-card::after {{
    content: "";
    position: absolute;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    right: -90px;
    top: -90px;
    background: radial-gradient(circle, rgba(96,165,250,0.16), transparent 65%);
}}

.hero-content {{
    position: relative;
    z-index: 1;
    max-width: 800px;
}}

.hero-kicker {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
    padding: 9px 13px;
    border-radius: 999px;
    border: 1px solid rgba(34,197,94,0.26);
    background: rgba(34,197,94,0.10);
    color: #bbf7d0;
    font-size: 13px;
    font-weight: 700;
}}

.hero-title {{
    margin: 0;
    font-size: 44px;
    line-height: 1.03;
    font-weight: 800;
    letter-spacing: -0.055em;
}}

.gradient-text {{
    background: linear-gradient(135deg, #86efac 0%, #60a5fa 52%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero-subtitle {{
    max-width: 680px;
    margin: 16px 0 0;
    color: #cbd5e1;
    font-size: 16px;
    line-height: 1.7;
}}

.hero-features {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 22px;
}}

.feature-chip {{
    border: 1px solid var(--border-soft);
    background: rgba(255,255,255,0.045);
    color: #dbeafe;
    border-radius: 999px;
    padding: 10px 13px;
    font-size: 13px;
    font-weight: 600;
}}

.layout {{
    display: grid;
    grid-template-columns: 360px minmax(0, 1fr);
    gap: 22px;
    align-items: start;
}}

.card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 26px;
    padding: 24px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}}

.input-card {{
    position: sticky;
    top: 18px;
}}

.card-label {{
    display: inline-flex;
    margin-bottom: 14px;
    padding: 8px 12px;
    border-radius: 999px;
    background: var(--blue-soft);
    border: 1px solid rgba(96,165,250,0.25);
    color: #bfdbfe;
    font-size: 12px;
    font-weight: 700;
}}

.card-title {{
    margin: 0 0 14px;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.035em;
}}

.help {{
    color: var(--muted);
    font-size: 14px;
    line-height: 1.6;
    background: rgba(255,255,255,0.035);
    border: 1px solid var(--border-soft);
    padding: 14px;
    border-radius: 18px;
    margin-bottom: 18px;
}}

.form-section {{
    margin-top: 18px;
}}

.form-section-title {{
    display: flex;
    align-items: center;
    gap: 8px;
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 9px;
}}

input {{
    width: 100%;
    margin: 6px 0;
    padding: 14px 15px;
    border-radius: 16px;
    border: 1px solid rgba(148,163,184,0.18);
    background: rgba(255,255,255,0.045);
    color: white;
    font-size: 14px;
    outline: none;
    transition: 0.18s ease;
}}

input::placeholder {{
    color: #94a3b8;
}}

input:focus {{
    border-color: rgba(96,165,250,0.8);
    box-shadow: 0 0 0 4px rgba(96,165,250,0.13);
    background: rgba(255,255,255,0.065);
}}

button {{
    width: 100%;
    margin-top: 18px;
    padding: 15px 18px;
    border: none;
    border-radius: 17px;
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    color: white;
    font-weight: 800;
    font-size: 15px;
    cursor: pointer;
    box-shadow: 0 18px 36px rgba(34,197,94,0.24);
    transition: 0.16s ease;
}}

button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 22px 42px rgba(34,197,94,0.30);
}}

.example-note {{
    color: var(--muted-2);
    font-size: 12px;
    line-height: 1.5;
    margin-top: 14px;
}}

.dashboard-card {{
    min-height: 520px;
}}

.overview-grid {{
    display: grid;
    gap: 16px;
}}

.panel-header {{
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: center;
    margin-bottom: 14px;
}}

.eyebrow {{
    margin: 0 0 5px;
    color: var(--muted);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.panel-header h2 {{
    margin: 0;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.04em;
}}

.status-pill {{
    border-radius: 999px;
    padding: 8px 12px;
    color: #bbf7d0;
    background: var(--green-soft);
    border: 1px solid rgba(34,197,94,0.25);
    font-size: 12px;
    font-weight: 800;
    white-space: nowrap;
}}

.result-card,
.metric-card,
.wide-metric,
.insights-panel {{
    background: var(--bg-card-soft);
    border: 1px solid var(--border-soft);
    border-radius: 20px;
    padding: 18px;
}}

.result-card {{
    text-align: left;
}}

.result-card h2 {{
    margin: 0 0 10px;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.055em;
}}

.result-card h3 {{
    margin: 18px 0 8px;
    color: #cbd5e1;
    font-size: 14px;
}}

.metrics-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}}

.metric-card {{
    text-align: left;
}}

.metric-card h3,
.wide-metric h3 {{
    margin: 0 0 10px;
    color: #cbd5e1;
    font-size: 14px;
}}

.metric-card div,
.wide-metric div {{
    line-height: 1.7;
}}

.wide-metric {{
    text-align: left;
}}

.insights-panel {{
    background:
        linear-gradient(135deg, rgba(34,197,94,0.07), rgba(96,165,250,0.05)),
        rgba(255,255,255,0.03);
}}

.insights {{
    color: #e2e8f0;
    line-height: 1.8;
    text-align: left;
}}

.empty-state {{
    min-height: 500px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #cbd5e1;
    padding: 30px;
}}

.empty-icon {{
    width: 74px;
    height: 74px;
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    background: rgba(34,197,94,0.10);
    border: 1px solid rgba(34,197,94,0.20);
    margin-bottom: 18px;
}}

.empty-state h2 {{
    margin: 0 0 10px;
    font-size: 28px;
    letter-spacing: -0.04em;
}}

.empty-state p {{
    max-width: 460px;
    color: var(--muted);
    line-height: 1.7;
}}

.example-box {{
    margin-top: 14px;
    padding: 13px 15px;
    border-radius: 16px;
    border: 1px solid var(--border-soft);
    background: rgba(255,255,255,0.04);
    color: #dbeafe;
    font-size: 13px;
}}

.feedback {{
    margin-top: 28px;
    text-align: center;
    color: var(--muted);
    font-size: 14px;
}}

.feedback a {{
    display: inline-flex;
    margin-top: 8px;
    color: #86efac;
    text-decoration: none;
    font-weight: 800;
}}

.feedback a:hover {{
    text-decoration: underline;
}}

.disclaimer {{
    margin-top: 14px;
    color: var(--muted-2);
    font-size: 12px;
}}

@media (max-width: 980px) {{
    .layout {{
        grid-template-columns: 1fr;
    }}

    .input-card {{
        position: static;
    }}

    .hero-title {{
        font-size: 36px;
    }}
}}

@media (max-width: 640px) {{
    body {{
        padding: 18px 12px 36px;
    }}

    .brand h1 {{
        font-size: 22px;
    }}

    .logo {{
        width: 42px;
        height: 42px;
    }}

    .nav-actions {{
        width: 100%;
    }}

    .nav-pill {{
        width: 100%;
        text-align: center;
    }}

    .hero-card {{
        padding: 22px;
        border-radius: 24px;
    }}

    .hero-title {{
        font-size: 29px;
    }}

    .hero-subtitle {{
        font-size: 14px;
    }}

    .feature-chip {{
        width: 100%;
        text-align: center;
    }}

    .card {{
        padding: 18px;
        border-radius: 22px;
    }}

    .metrics-grid {{
        grid-template-columns: 1fr;
    }}

    .result-card h2 {{
        font-size: 29px;
    }}

    .panel-header {{
        align-items: flex-start;
        flex-direction: column;
    }}
}}
</style>
</head>

<body>
<div class="page">

    <div class="nav">
        <div class="brand">
            <div class="logo">📈</div>
            <div>
                <h1>Wealth Dashboard</h1>
                <p>Simple portfolio intelligence</p>
            </div>
        </div>

        <div class="nav-actions">
            <div class="nav-pill">🔒 No login</div>
            <div class="nav-pill">⚡ Quick insights</div>
        </div>
    </div>

    <section class="hero">
        <div class="hero-card">
            <div class="hero-content">
                <div class="hero-kicker">Privacy-first wealth tracking</div>

                <h2 class="hero-title">
                    A cleaner way to understand your
                    <span class="gradient-text">crypto, stocks, and future wealth.</span>
                </h2>

                <p class="hero-subtitle">
                    Enter your holdings manually and get instant portfolio value,
                    health score, goal progress, future projections, and simple insights —
                    without connecting your broker or exchange.
                </p>

                <div class="hero-features">
                    <div class="feature-chip">📊 Portfolio health</div>
                    <div class="feature-chip">📈 Future projection</div>
                    <div class="feature-chip">🎯 Goal tracker</div>
                    <div class="feature-chip">💸 Monthly investing estimate</div>
                </div>
            </div>
        </div>
    </section>

    <main class="layout">

        <aside class="card input-card">
            <div class="card-label">Input</div>
            <h2 class="card-title">Add your holdings</h2>

            <div class="help">
                Enter the amount of each asset you own, not the euro value.
                <br><br>
                Example: <strong>0.01 BTC</strong>, <strong>0.5 ETH</strong>,
                <strong>10 VWCE</strong>, <strong>1 Apple</strong>, <strong>1 Microsoft</strong>.
            </div>

            <form method="POST">
                <div class="form-section">
                    <div class="form-section-title">₿ Crypto</div>
                    <input name="btc" value="{btc}" placeholder="BTC amount">
                    <input name="eth" value="{eth}" placeholder="ETH amount">
                </div>

                <div class="form-section">
                    <div class="form-section-title">📊 Stocks & ETFs</div>
                    <input name="vwce" value="{vwce}" placeholder="VWCE shares">
                    <input name="aapl" value="{aapl}" placeholder="Apple shares">
                    <input name="msft" value="{msft}" placeholder="Microsoft shares">
                </div>

                <div class="form-section">
                    <div class="form-section-title">🎯 Target</div>
                    <input name="goal" value="{goal_val}" placeholder="Goal €">
                </div>

                <button type="submit">Calculate Dashboard</button>
            </form>

            <div class="example-note">
                Your values are saved in your browser cookies for convenience.
            </div>
        </aside>

        <section class="card dashboard-card">
            {overview_content}
        </section>

    </main>

    <div class="feedback">
        <p>Found something confusing, useless, or missing?</p>
        <a href="https://buildpulse-y2h5.onrender.com/p/wealth-dashboard-65aac1" target="_blank" rel="noopener noreferrer">
            Leave feedback
        </a>
        <div class="disclaimer">
            Educational tool only. Estimates are not financial advice.
        </div>
    </div>

</div>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)