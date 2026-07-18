import json
import os
import sys
import logging
from datetime import datetime, timezone

import boto3
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream
from alpaca.data.enums import DataFeed


load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")

KINESIS_STREAM = "marketpulse-ticks-stream"
AWS_REGION = "ap-southeast-1"

# Same 16-ticker universe as yfinance_historical_load.py and newsapi_pull.py
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META", 
    "JPM", "V",                                          
    "JNJ", "UNH",                                       
    "TSLA", "WMT", "KO",                                 
    "XOM", "CVX",                                         
    "BA",                                                 
]



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)

kinesis = boto3.client("kinesis", region_name=AWS_REGION)

put_count = 0  


def push_to_kinesis(record: dict) -> None:
    global put_count
    payload = json.dumps(record).encode("utf-8")
    kinesis.put_record(
        StreamName=KINESIS_STREAM,
        Data=payload,
        PartitionKey=record.get("ticker", "unknown"),
    )
    put_count += 1
    if put_count % 10 == 1:  
        log.info(
            "Pushed record #%d | %s @ $%.2f",
            put_count,
            record.get("ticker"),
            record.get("price", 0),
        )




async def handle_trade(trade) -> None:
    record = {
        "ticker": trade.symbol,
        "price": float(trade.price),
        "size": int(trade.size),
        "timestamp": trade.timestamp.isoformat(),
        "exchange": trade.exchange,
        "trade_id": trade.id,
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "alpaca_iex",
    }
    push_to_kinesis(record)



def run_test():
    log.info("TEST MODE: pushing one synthetic tick to Kinesis...")
    test_record = {
        "ticker": "TEST",
        "price": 123.45,
        "size": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exchange": "TEST",
        "trade_id": 0,
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "alpaca_iex_test",
    }
    push_to_kinesis(test_record)
    log.info("Test tick pushed successfully. Exiting.")


def main():
    if not ALPACA_API_KEY or not ALPACA_API_SECRET:
        log.error("ALPACA_API_KEY and ALPACA_API_SECRET must be set in .env")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test()
        return

    log.info("Starting Alpaca stream producer")
    log.info("Tickers: %s", ", ".join(TICKERS))
    log.info("Kinesis stream: %s (%s)", KINESIS_STREAM, AWS_REGION)
    log.info(
        "NOTE: IEX feed only streams during US market hours "
        "(Mon-Fri 9:30 AM - 4:00 PM ET). Outside those hours "
        "the connection is open but no trades will arrive."
    )

    stream = StockDataStream(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_API_SECRET,
        feed=DataFeed.IEX,
    )

    stream.subscribe_trades(handle_trade, *TICKERS)

    log.info("WebSocket connected — waiting for trades...")

    try:
        stream.run()
    except KeyboardInterrupt:
        log.info("Interrupted. Total records pushed: %d", put_count)
    except Exception as e:
        log.error("Stream error: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    main()