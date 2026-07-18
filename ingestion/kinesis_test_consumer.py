import json
import time

import boto3

KINESIS_STREAM = "marketpulse-ticks-stream"
AWS_REGION = "ap-southeast-1"

kinesis = boto3.client("kinesis", region_name=AWS_REGION)


def main():
    desc = kinesis.describe_stream(StreamName=KINESIS_STREAM)
    shard_id = desc["StreamDescription"]["Shards"][0]["ShardId"]
    print(f"Reading from shard: {shard_id}\n")

    iterator = kinesis.get_shard_iterator(
        StreamName=KINESIS_STREAM,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON",
    )["ShardIterator"]

    records_read = 0
    max_records = 10
    empty_polls = 0

    while records_read < max_records and empty_polls < 5:
        response = kinesis.get_records(ShardIterator=iterator, Limit=10)
        records = response["Records"]
        iterator = response["NextShardIterator"]

        if not records:
            empty_polls += 1
            print(f"  (no records yet, poll {empty_polls}/5 — waiting 2s)")
            time.sleep(2)
            continue

        for r in records:
            raw = r["Data"]
            try:
                data = json.loads(raw)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(f"  (non-JSON record, raw bytes: {raw[:100]})")
            records_read += 1

    print(f"\nDone. Read {records_read} record(s) from Kinesis.")


if __name__ == "__main__":
    main()