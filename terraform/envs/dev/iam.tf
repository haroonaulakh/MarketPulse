module "kinesis_iam" {
  source = "../../modules/iam"

  kinesis_stream_arn   = module.kinesis.stream_arn
  attach_to_local_user = true
  local_cli_user_name  = "marketpulse-admin"
}