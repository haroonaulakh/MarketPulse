variable "kinesis_stream_arn" {
  description = "ARN of the marketpulse-ticks-stream Kinesis stream"
  type        = string
}

variable "attach_to_local_user" {
  description = "Whether to attach these policies directly to the local CLI IAM user (dev convenience)"
  type        = bool
  default     = true
}

variable "local_cli_user_name" {
  description = "IAM user name for the local CLI credentials"
  type        = string
}