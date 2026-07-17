import requests
import boto3
import json
from datetime import datetime, timezone

S3_BUCKET = "marketpulse-raw-haroonalk"
S3_PREFIX = "coingecko"
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
NUM_COINS = 20

# Fetch top N coins by market cap
def fetch_coingecko_data(n=NUM_COINS):
    

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": n,
        "page": 1,
        "sparkline": "false",
    }
    response = requests.get(COINGECKO_URL, params=params, timeout=30)
    response.raise_for_status()  
    return response.json()

# Write the fetched data to S3 as a timestamped JSON file
def write_to_s3(data, bucket, prefix):
   
    s3 = boto3.client("s3")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    key = f"{prefix}/coingecko_{timestamp}.json"

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
    return key


def main():
    print(f"Fetching top {NUM_COINS} coins from CoinGecko...")
    data = fetch_coingecko_data()
    print(f"Fetched {len(data)} records.")

    print(f"Writing to s3://{S3_BUCKET}/{S3_PREFIX}/ ...")
    key = write_to_s3(data, S3_BUCKET, S3_PREFIX)
    print(f"Done. Object written: s3://{S3_BUCKET}/{key}")

    # Quick sanity check on the data itself
    if data:
        sample = data[0]
        print("\nSample record:")
        for field in ["id", "symbol", "current_price", "market_cap", "total_volume"]:
            print(f"  {field}: {sample.get(field)}")


if __name__ == "__main__":
    main()