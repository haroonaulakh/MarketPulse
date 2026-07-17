terraform {
  backend "s3" {
    bucket         = "marketpulse-tf-state"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "marketpulse-tf-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = "ap-southeast-1"
}

module "s3_raw" {
  source      = "../../modules/s3"
  bucket_name = "marketpulse-raw-haroonalk"
}

module "s3_bronze" {
  source      = "../../modules/s3"
  bucket_name = "marketpulse-bronze-haroonalk"
}

module "s3_silver" {
  source      = "../../modules/s3"
  bucket_name = "marketpulse-silver-haroonalk"
}

module "s3_gold" {
  source      = "../../modules/s3"
  bucket_name = "marketpulse-gold-haroonalk"
}

module "s3_artifacts" {
  source      = "../../modules/s3"
  bucket_name = "marketpulse-artifacts-haroonalk"
}