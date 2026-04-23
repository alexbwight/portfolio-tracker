import requests

# User input
btc_amount = float(input("How much BTC do you have: "))
eth_amount = float(input("How much ETH do you have: "))

# API request
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=eur"
data = requests.get(url).json()

# Prices
btc_price = data["bitcoin"]["eur"]
eth_price = data["ethereum"]["eur"]

# Values
btc_value = btc_amount * btc_price
eth_value = eth_amount * eth_price
total_value = btc_value + eth_value

# Output
print("\n====================")
print("   YOUR PORTFOLIO")
print("====================")

print(f"BTC value: €{btc_value:.2f}")
print(f"ETH value: €{eth_value:.2f}")

print("--------------------")
print(f"TOTAL: €{total_value:.2f}")
print("====================")

btc_percent = (btc_value / total_value) * 100
eth_percent = (eth_value / total_value) * 100

print(f"BTC: {btc_percent:.1f}%")
print(f"ETH: {eth_percent:.1f}%")


if btc_value > eth_value:
    print("BTC is your biggest position")
else:
    print("ETH is your biggest position")