output "kinesis_producer_policy_arn" {
  description = "ARN of the Kinesis producer policy"
  value       = aws_iam_policy.kinesis_producer.arn
}

output "kinesis_consumer_policy_arn" {
  description = "ARN of the Kinesis consumer policy"
  value       = aws_iam_policy.kinesis_consumer.arn
}