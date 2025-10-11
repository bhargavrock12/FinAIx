import yfinance as yf
import os

# Define the project's root directory relative to this script's location
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def fetch_and_save(ticker: str, period: str = "1y", interval: str = "1d"):
    """
    Fetch historical stock data for a given ticker and save it to a CSV file.

    Parameters:
    - ticker: Stock ticker symbol (e.g., "AAPL" for Apple)
    - period: Data period to download (e.g., "1y" for 1 year)
    - interval: Data interval (e.g., "1d" for daily data)
    """
    # Fetch historical stock data
    print(f"Fetching data for {ticker}...")
    data = yf.download(ticker, period=period, interval=interval)

    if data.empty:
        print(f"No data found for ticker {ticker}.")
        return

    # Define the directory to save raw data
    data_dir = os.path.join(PROJECT_ROOT, 'data', 'raw')
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Save to CSV
    file_path = os.path.join(data_dir, f"{ticker}_{period}_{interval}.csv")
    data.to_csv(file_path)
    print(f"Data for {ticker} saved to {file_path}")

if __name__ == "__main__":
    # Example usage
    fetch_and_save("AAPL", period="1mo", interval="1d")  # Fetch 1 month of daily data for Apple
    fetch_and_save("MSFT", period="6mo", interval="1d")  # Fetch 6 months of daily data for Microsoft
    fetch_and_save("GOOGL", period="1y", interval="1wk")  # Fetch 1 year of weekly data for Alphabet