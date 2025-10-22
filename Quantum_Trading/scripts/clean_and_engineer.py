import pandas as pd
import ta
import os

def clean_and_engineer(input_file: str, output_file: str):
    """
    Load a raw CSV of OHLCV data, clean it, add technical indicators, and save processed CSV.
    """
    print(f"📊 Processing {input_file}...")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ ERROR: File not found: {input_file}")
        print(f"   Current working directory: {os.getcwd()}")
        return False
    
    try:
        # Read CSV with better error handling
        df = pd.read_csv(input_file, index_col=0, parse_dates=True)
        
        # If dates are still objects, try to convert them
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            df.index = pd.to_datetime(df.index, errors='coerce')
            # Drop rows where date conversion failed
            df = df[df.index.notna()]
            
    except Exception as e:
        print(f"❌ Error reading file {input_file}: {e}")
        return False

    # If the CSV has a column level with ticker names, flatten it
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]  # keep just the field name

    # Force numeric conversion on price columns
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing values in price columns
    initial_rows = len(df)
    df.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)
    df.sort_index(inplace=True)
    
    # Check if we have enough data after cleaning
    if len(df) == 0:
        print(f"❌ No valid data remaining after cleaning in {input_file}")
        return False

    print(f"   Data shape: {df.shape}, Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    if initial_rows != len(df):
        print(f"   Removed {initial_rows - len(df)} rows with missing/invalid data")

    try:
        # Add technical indicators with error handling
        df['SMA_10'] = ta.trend.sma_indicator(df['Close'], window=10)
        df['EMA_10'] = ta.trend.ema_indicator(df['Close'], window=10)
        df['RSI_14'] = ta.momentum.rsi(df['Close'], window=14)
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        df['Bollinger_High'] = ta.volatility.bollinger_hband(df['Close'], window=20, window_dev=2)
        df['Bollinger_Low'] = ta.volatility.bollinger_lband(df['Close'], window=20, window_dev=2)
        df['Bollinger_Middle'] = ta.volatility.bollinger_mavg(df['Close'], window=20)
        
        # Add volume-based indicators
        if 'Volume' in df.columns and df['Volume'].notna().any():
            df['Volume_SMA_20'] = ta.trend.sma_indicator(df['Volume'], window=20)
        
        # Add volatility indicator
        df['ATR_14'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        
        print(f"   ✅ Added {len([col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']])} technical indicators")
        
    except Exception as e:
        print(f"❌ Error calculating technical indicators: {e}")
        return False

    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file)
        print(f"💾 Processed data saved to {output_file}")
        print(f"   Final shape: {df.shape}, Columns: {list(df.columns)}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving file {output_file}: {e}")
        return False


def process_all_files():
    """Process all raw data files in the data/raw directory"""
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    
    if not os.path.exists(raw_dir):
        print(f"❌ Raw data directory not found: {raw_dir}")
        return
    
    # Get all CSV files in raw directory
    csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"📭 No CSV files found in {raw_dir}")
        return
    
    print(f"🔍 Found {len(csv_files)} CSV files to process:")
    
    success_count = 0
    for csv_file in csv_files:
        input_path = os.path.join(raw_dir, csv_file)
        # Create output filename
        output_filename = csv_file.replace('.csv', '_processed.csv')
        output_path = os.path.join(processed_dir, output_filename)
        
        print(f"\n{'='*50}")
        if clean_and_engineer(input_path, output_path):
            success_count += 1
        print(f"{'='*50}")
    
    print(f"\n🎯 Processing Summary: {success_count}/{len(csv_files)} files processed successfully")


if __name__ == "__main__":
    print("🚀 Starting Financial Data Processing Pipeline...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Option 1: Process specific files (your original approach)
    # clean_and_engineer("data/raw/AAPL_1mo_1d.csv", "data/processed/AAPL_1mo_1d_processed.csv")
    # clean_and_engineer("data/raw/MSFT_6mo_1d.csv", "data/processed/MSFT_6mo_1d_processed.csv")
    # clean_and_engineer("data/raw/GOOGL_1y_1wk.csv", "data/processed/GOOGL_1y_1wk_processed.csv")
    
    # Option 2: Process all CSV files automatically (recommended)
    process_all_files()
    
    print("\n✅ Data processing completed!")