import yfinance as yf
import boto3
import io
from datetime import datetime, timezone

S3_BUCKET = "marketpulse-raw-haroonalk"
S3_PREFIX = "yfinance/ohlcv_5y"
PERIOD = "5y"        
INTERVAL = "1d"      # daily bars

TICKERS = [
    # Tech
    "AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META",
    # Finance
    "JPM", "V",
    # Healthcare
    "JNJ", "UNH",
    # Consumer
    "TSLA", "WMT", "KO",
    # Energy
    "XOM", "CVX",
    # Industrials
    "BA",
]

# fetch 5 years of OHLCV data for each ticker (of each day)
def fetch_ohlcv(ticker):
    df = yf.download(
        ticker,
        period=PERIOD,
        interval=INTERVAL,
        auto_adjust=False,   
        progress=False,
    )
    if df.empty:
        return None

    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)

    # make Date a normal column
    df = df.reset_index()         
    df["ticker"] = ticker          
    df["ingested_at_utc"] = datetime.now(timezone.utc).isoformat()
    return df


def write_parquet_to_s3(df, bucket, key):
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())


def main():
    print(f"Loading {PERIOD} of {INTERVAL} OHLCV for {len(TICKERS)} tickers...\n")
    results = {}

    for ticker in TICKERS:
        try:
            df = fetch_ohlcv(ticker)
            if df is None or df.empty:
                print(f"  [WARN] {ticker}: no data returned, skipping")
                results[ticker] = 0
                continue

            key = f"{S3_PREFIX}/{ticker}.parquet"
            write_parquet_to_s3(df, S3_BUCKET, key)
            results[ticker] = len(df)
            print(f"  [OK]   {ticker}: {len(df)} rows -> s3://{S3_BUCKET}/{key}")

        except Exception as e:
            print(f"  [FAIL] {ticker}: {e}")
            results[ticker] = -1

    
    total = sum(v for v in results.values() if v > 0)
    failed = [t for t, v in results.items() if v <= 0]
    print(f"\nDone. Total rows written: {total}")
    if failed:
        print(f"Tickers with issues (re-run these): {failed}")
    else:
        print("All tickers loaded successfully.")


if __name__ == "__main__":
    main()