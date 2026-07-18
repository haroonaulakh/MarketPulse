output "stream_name" {
  description = "Name of the Kinesis stream"
  value       = aws_kinesis_stream.ticks_stream.name
}

output "stream_arn" {
  description = "ARN of the Kinesis stream — used by producer/consumer IAM policies later"
  value       = aws_kinesis_stream.ticks_stream.arn
}

output "shard_count" {
  description = "Current shard count"
  value       = aws_kinesis_stream.ticks_stream.shard_count
}