import yfinance as yf
import matplotlib.pyplot as plt

# Fetch historical stock data for Apple (AAPL) of past 1 month
data = yf.download("AAPL", period="1y", interval="1d")

print(data.head()) # Print the first few rows of the data

# Plot the closing prices
plt.plot(data.index, data['Close'])
plt.title('AAPL Closing Prices - Last 1 Year')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
