resource "aws_kinesis_stream" "ticks_stream" {
  name             = var.stream_name
  shard_count      = var.shard_count
  retention_period = var.retention_period_hours

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }

  shard_level_metrics = [
    "IncomingBytes",
    "IncomingRecords",
    "OutgoingBytes",
    "OutgoingRecords",
    "WriteProvisionedThroughputExceeded",
    "ReadProvisionedThroughputExceeded",
  ]

  encryption_type = "KMS"
  kms_key_id      = "alias/aws/kinesis"

  tags = merge(
    var.tags,
    {
      Name    = var.stream_name
      Project = "marketpulse"
    }
  )
}