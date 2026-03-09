terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.0.0"

  cluster_name    = "${var.environment}-${var.cluster_name}"
  cluster_version = "1.25"

  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids

  eks_managed_node_groups = {
    default = {
      desired_size  = var.node_desired_size
      min_size      = var.node_min_size
      max_size      = var.node_max_size
      instance_types = [var.node_instance_type]
    }
  }

  tags = {
    Environment = var.environment
    Project     = "tripla-terraform-parse"
  }
}

resource "aws_s3_bucket" "static_assets" {
  bucket = "${var.cluster_name}-static-assets"

  tags = {
    Environment = var.environment
    Project     = "tripla-terraform-parse"
  }
}

resource "aws_s3_bucket_acl" "static_assets_acl" {
  bucket = aws_s3_bucket.static_assets.id
  acl    = var.bucket_acl
}
