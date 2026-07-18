# --- Producer policy: alpaca_stream_producer.py writes ticks into the stream ---
data "aws_iam_policy_document" "kinesis_producer" {
  statement {
    sid    = "KinesisProducerWrite"
    effect = "Allow"
    actions = [
      "kinesis:PutRecord",
      "kinesis:PutRecords",
      "kinesis:DescribeStream",
      "kinesis:DescribeStreamSummary",
    ]
    resources = [var.kinesis_stream_arn]
  }
}

resource "aws_iam_policy" "kinesis_producer" {
  name        = "MarketPulseKinesisProducer"
  description = "Write-only access to the marketpulse-ticks-stream Kinesis stream"
  policy      = data.aws_iam_policy_document.kinesis_producer.json
}

# --- Consumer policy: Bronze notebook / throwaway test consumer reads ticks ---
data "aws_iam_policy_document" "kinesis_consumer" {
  statement {
    sid    = "KinesisConsumerRead"
    effect = "Allow"
    actions = [
      "kinesis:GetRecords",
      "kinesis:GetShardIterator",
      "kinesis:DescribeStream",
      "kinesis:DescribeStreamSummary",
      "kinesis:ListShards",
      "kinesis:ListStreams",
    ]
    resources = [var.kinesis_stream_arn]
  }
}

resource "aws_iam_policy" "kinesis_consumer" {
  name        = "MarketPulseKinesisConsumer"
  description = "Read-only access to the marketpulse-ticks-stream Kinesis stream"
  policy      = data.aws_iam_policy_document.kinesis_consumer.json
}

# --- Attach both to the local CLI user for now (dev convenience) ---
# Same pattern as MarketPulseS3ReadWrite on marketpulse-admin.
# Move to per-service role attachment (Databricks instance profile, etc.)
# in Phase 9 hardening.
resource "aws_iam_user_policy_attachment" "producer_attach" {
  count      = var.attach_to_local_user ? 1 : 0
  user       = var.local_cli_user_name
  policy_arn = aws_iam_policy.kinesis_producer.arn
}

resource "aws_iam_user_policy_attachment" "consumer_attach" {
  count      = var.attach_to_local_user ? 1 : 0
  user       = var.local_cli_user_name
  policy_arn = aws_iam_policy.kinesis_consumer.arn
}