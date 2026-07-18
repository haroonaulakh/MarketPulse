variable "stream_name" {
  description = "Name of the Kinesis Data Stream"
  type        = string
  default     = "marketpulse-ticks-stream"
}

variable "shard_count" {
  description = "Number of shards (1 shard = ~1MB/s in, 2MB/s out — plenty for paper-trading tick volume)"
  type        = number
  default     = 1
}

variable "retention_period_hours" {
  description = "How long records stay in the stream before expiring"
  type        = number
  default     = 24
}

variable "tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}