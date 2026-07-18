module "kinesis" {
  source = "../../modules/kinesis"

  stream_name            = "marketpulse-ticks-stream"
  shard_count            = 1
  retention_period_hours = 24

  tags = {
    Environment = "dev"
  }
}

output "kinesis_stream_name" {
  value = module.kinesis.stream_name
}

output "kinesis_stream_arn" {
  value = module.kinesis.stream_arn
}