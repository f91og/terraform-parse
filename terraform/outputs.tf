output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint of the EKS cluster"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "static_assets_bucket_name" {
  description = "Name of the S3 bucket used for static assets"
  value       = aws_s3_bucket.static_assets.id
}